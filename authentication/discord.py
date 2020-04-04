import requests


class Discord(object):
    redirect = None
    client_id = "584422682100105300"
    client_secret = "Wyg6tKZCt97B6G06QVMgDq0EesBDUBh0"
    api = "https://discordapp.com/api/v6"

    def __init__(self, redirect):
        self.redirect = redirect

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

        request = requests.post(f"{self.api}/oauth2/token", data, headers)
        request.raise_for_status()
        result = request.json()

        return result["access_token"]

    def get_user(self, token):
        headers = {"Authorization": f"Bearer {token}"}
        request = requests.get(f"{self.api}/users/@me", headers=headers)
        request.raise_for_status()
        return request.json()
