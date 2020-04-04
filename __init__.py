from flask import Flask
from flask_restplus import Api, Resource, Namespace, reqparse
from werkzeug.exceptions import HTTPException
import json
from servey_db_identity import Schema
from auth import URL
import authentication

identity = Schema(URL)
discord = authentication.Discord("http://localhost:5000/auth/discord/authenticate")

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


api = Api(app, doc="/")
api.title = name

code_parser = reqparse.RequestParser()
code_parser.add_argument("code", type=str, help="Discord user authentication code")


auth = Namespace("auth")
api.add_namespace(auth)


@auth.route("/discord/authenticate")
class DiscordAuthenticate(Resource):
    @api.doc("Exchange a Discord authentication code for an OAuth2 token.")
    def get(self):
        args = code_parser.parse_args()
        code = args["code"]
        token = discord.exchange_code(code)
        user = discord.get_user(token)
        identity.set_auth_discord(user["id"], token)

        return "Success!"


def main():
    app.run()


if __name__ == "__main__":
    main()
