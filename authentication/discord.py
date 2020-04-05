import requests

api = "https://discordapp.com/api/v6"


class Discord(object):
    redirect = None
    client_id = None
    client_secret = None

    def __init__(self, redirect, client_id, client_secret):
        self.redirect = redirect
        self.client_id = client_id
        self.client_secret = client_secret

    def exchange_code(self, code):
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect,
            "scope": "identify"
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        request = requests.post(f"{api}/oauth2/token", data, headers)
        request.raise_for_status()
        result = request.json()

        return result["access_token"]

    @staticmethod
    def get_user(token):
        headers = {"Authorization": f"Bearer {token}"}
        request = requests.get(f"{api}/users/@me", headers=headers)
        request.raise_for_status()
        return request.json()
