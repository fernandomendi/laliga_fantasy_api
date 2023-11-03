import requests
import pandas as pd
from tqdm import tqdm
tqdm.pandas()


class FantasyAPI:
    def __init__(self, token):
        self.endpoint = "https://api-fantasy.llt-services.com/api/v3/"
        self.headers = {
            'Authorization': f'Bearer {token}'
        }
        self.request_timeout = 30

    def get(self, path, **kwargs):
        return getattr(self, F"get_{path}")(**kwargs)
    
    # ------------------------------------------------------------------------------------
    
    def get_league_id(self, league_name):
        response = requests.get(self.endpoint + "leagues", headers=self.headers, timeout=self.request_timeout)
        payload = response.json()

        for league in payload:
            if league_name == league["name"]:
                return league["id"]

    def get_player_ids(self):
        response = requests.get(self.endpoint + "players", headers=self.headers, timeout=self.request_timeout)
        payload = response.json()

        return list(map(lambda x: int(x["id"]), payload))

    def get_player_data(self, player_id):
        response = requests.get(self.endpoint + f"player/{player_id}", headers=self.headers, timeout=self.request_timeout)
        payload = response.json()

        positions = {
            "Portero" : "GOA",
            "Defensa" : "DEF",
            "Centrocampista" : "MID",
            "Delantero" : "STR",
            "Entrenador" : "COA"
        }

        status = payload["playerStatus"]
        name = payload["nickname"]
        team = payload["team"]["name"]
        position = positions[payload["position"]]
        points = list(map(lambda x: x["totalPoints"], payload["playerStats"]))
        average_points = payload["averagePoints"]
        market_value = payload["marketValue"]

        return status, name, team, position, points, average_points, market_value

    def get_players(self):
        player_ids = self.get("player_ids")
        players_df = pd.DataFrame(player_ids, columns=["id"])
        players_df[["status", "name", "team", "position", "points", "average_points", "market_value"]] = players_df.id.progress_apply(lambda x: self.get("player_data", player_id=x)).apply(pd.Series)

        return players_df

    def get_squads(self, league_id):
        response = requests.get(self.endpoint + f"leagues/{league_id}/teams", headers=self.headers, timeout=self.request_timeout)
        payload = response.json()

        squad_df = pd.DataFrame()
        for squad in payload:
            squad_df = pd.concat([squad_df, pd.DataFrame(map(lambda x: (int(x["playerMaster"]["id"]), squad["manager"]["managerName"]), squad["players"]), columns=["player_id", "manager_name"])])
        return squad_df

    def get_market(self, league_id):
        response = requests.get(self.endpoint + f"leagues/{league_id}/market", headers=self.headers, timeout=self.request_timeout)
        payload = response.json()

        return list(map(lambda x: int(x["playerMaster"]["id"]), filter(lambda x: x["discr"] == "marketPlayerLeague", payload)))

    def get_league_players(self, league_id):
        squads_df = self.get("squads", league_id=league_id)
        market_df = pd.DataFrame(self.get("market", league_id=league_id), columns=["player_id"])
        market_df["manager_name"] = None
        league_players_df = pd.concat([squads_df, market_df])

        return league_players_df
