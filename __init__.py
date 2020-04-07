import flask
from flask import Flask
from flask_restplus import Api, Resource, Namespace
from werkzeug.exceptions import HTTPException
import json
from .servey_db_identity import Schema
from . import authentication
from os import environ


try:
    discord_redirect = environ["SERVEY_API_DISCORD_REDIRECT"]
    discord_id = environ["SERVEY_API_DISCORD_ID"]
    discord_secret = environ["SERVEY_API_DISCORD_SECRET"]
    database_url = environ["SERVEY_DB_URL"]

except KeyError:
    raise EnvironmentError("The following environment variables must be set: "
                           "SERVEY_API_DISCORD_REDIRECT, SERVEY_API_DISCORD_ID, SERVEY_API_DISCORD_SECRET, "
                           "SERVEY_DB_URL") from None

identity = Schema(database_url)
discord = authentication.Discord(discord_redirect, discord_id, discord_secret)

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


api = SecureApi(app, doc="/")
api.title = name

auth = Namespace("auth")
api.add_namespace(auth)


@auth.route("/discord/authenticate/<string:code>")
class DiscordAuthenticate(Resource):
    @staticmethod
    @api.doc("Exchange a Discord authentication code for an OAuth2 token.")
    def get(code):
        token = discord.exchange_code(code)
        user = discord.get_user(token)
        identity.ensure_user(user["id"])
        identity.set_auth_discord(user["id"], token)

        return "Success!"


def main():
    app.run()


if __name__ == "__main__":
    main()
