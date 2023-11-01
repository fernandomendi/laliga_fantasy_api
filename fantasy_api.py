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

    def get_player_data(self, player_id):
        response = requests.get(MARCA_FANTASY_ENDPOINT + f"player/{player_id}", headers=self.headers, timeout=self.request_timeout)
        payload = response.json()

        positions = {
            "Portero" : "GOA",
            "Defensa" : "DEF",
            "Centrocampista" : "MID",
            "Delantero" : "STR"
        }

        status = payload["playerStatus"]
        name = payload["nickname"]
        team = payload["team"]["name"]
        position = positions[payload["position"]]
        points = list(map(lambda x: x["totalPoints"], payload["playerStats"]))
        average_points = payload["averagePoints"]
        market_value = payload["marketValue"]

        return status, name, team, position, points, average_points, market_value
