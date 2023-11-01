import requests

MARCA_FANTASY_ENDPOINT = "https://api-fantasy.llt-services.com/api/v3/"

class FantasyAPI:
    def __init__(self, token):
        self.headers = {
            'Authorization': f'Bearer {token}'
        }
        self.request_timeout = 30

    def get(self, path, args):
        return getattr(self, F"get_{path}")(**args)
    
    # ------------------------------------------------------------------------------------
    
    def get_league_id(self, league_name):
        response = requests.get(MARCA_FANTASY_ENDPOINT + "leagues", headers=self.headers, timeout=self.request_timeout)
        payload = response.json()

        for league in payload:
            if league_name == league["name"]:
                return league["id"]
