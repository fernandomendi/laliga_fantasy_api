import requests

MARCA_FANTASY_ENDPOINT = "https://api-fantasy.llt-services.com/api/v3/"

class FantasyAPI:
    def __init__(self, token):
        self.headers = {
            'Authorization': f'Bearer {token}'
        }
        self.request_timeout = 30

    def get(self, path, **kwargs):
        return getattr(self, F"get_{path}")(**kwargs)
    
    # ------------------------------------------------------------------------------------
    
    def get_league_id(self, league_name):
        response = requests.get(MARCA_FANTASY_ENDPOINT + "leagues", headers=self.headers, timeout=self.request_timeout)
        payload = response.json()

        for league in payload:
            if league_name == league["name"]:
                return league["id"]

    def get_player_ids(self):
        response = requests.get(MARCA_FANTASY_ENDPOINT + "players", headers=self.headers, timeout=self.request_timeout)
        payload = response.json()

        return list(map(lambda x: int(x["id"]), payload))
