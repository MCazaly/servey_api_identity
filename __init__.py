import flask
from flask import Flask, request
from flask_restplus import Api, Resource, Namespace, reqparse, fields
from werkzeug.exceptions import HTTPException
import json
from .servey_db_identity import Schema
from . import authentication
from os import environ


try:
    discord_id = environ["SERVEY_API_DISCORD_ID"]
    discord_secret = environ["SERVEY_API_DISCORD_SECRET"]
    database_url = environ["SERVEY_DB_URL"]

except KeyError:
    raise EnvironmentError("The following environment variables must be set: "
                           "SERVEY_API_DISCORD_ID, SERVEY_API_DISCORD_SECRET, SERVEY_DB_URL") from None

identity = Schema(database_url)

name = "ServeyMcServeface API (Identity)"
app = Flask(name)


@app.errorhandler(HTTPException)
def exception_handler(exception):
    response = exception.get_response()
    response.data = json.dumps({
        "code": exception.code,
        "name": exception.name,
        "description": exception.description,
    })
    response.content_type = "application/json"
    return response


class SecureApi(Api):
    @property
    def specs_url(self):
        # HTTPS monkey patch
        scheme = "http" if ":5000" in self.base_url else "https"
        return flask.url_for(self.endpoint("specs"), _external=True, _scheme=scheme)


code_parser = reqparse.RequestParser()
code_parser.add_argument("code", type=str, help="Discord user authentication code")

api = SecureApi(app, doc="/")
api.title = name

auth = Namespace("auth")
api.add_namespace(auth)

discord_fields = api.model("discord_auth",
                           {
                               "code": fields.String(required=True, description="Discord authentication code"),
                               "redirect": fields.String(required=False, description="Authorized redirect URI")
                           })


@auth.route("/discord/authenticate")
@auth.expect()
class DiscordAuthenticate(Resource):
    @staticmethod
    @api.doc("Exchange a Discord authentication code for an AssCo. API token.")
    @api.expect(discord_fields)
    def post():
        code = request.json.get("code")
        redirect = request.json.get("redirect")
        return discord_authenticate(code, redirect)


@auth.route("/discord/authenticate/legacy")
class DiscordAuthenticateLegacy(Resource):
    @staticmethod
    @api.doc("Direct Discord code exchange using URL parameter.")
    def get():
        args = code_parser.parse_args()
        code = args["code"]
        if ":5000" not in request.base_url:
            redirect = request.base_url.replace("http://", "https://")
        else:
            redirect = request.base_url
        return discord_authenticate(code, redirect)


def discord_authenticate(code, redirect):
    discord = authentication.Discord(redirect, discord_id, discord_secret)
    token = discord.exchange_code(code)
    user = discord.get_user(token)
    identity.ensure_user(user["id"])
    identity.set_auth_discord(user["id"], token)

    return {
        "api_token": identity.get_api_token(user["id"])
    }


def main():
    app.run()


if __name__ == "__main__":
    main()
