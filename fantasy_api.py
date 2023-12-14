import requests
import pandas as pd
from tqdm import tqdm
tqdm.pandas()


class FantasyAPI:
    def __init__(self, token):
        self.endpoint = "https://api-fantasy.llt-services.com/api/v3/"
        self.session = requests.Session()
        self.session.headers = {
            'Authorization': f'Bearer {token}'
        }
        self.session.request_timeout=30

    def get(self, path, **kwargs):
        return getattr(self, f"_FantasyAPI__get_{path}")(**kwargs)
    
    # ------------------------------------------------------------------------------------
    
    def __get_league_id(self, league_name):
        response = self.session.get(self.endpoint + "leagues")
        payload = response.json()

        for league in payload:
            if league_name == league["name"]:
                return league["id"]

    def __get_player_ids(self):
        response = self.session.get(self.endpoint + "players")
        payload = response.json()

        return list(map(lambda x: int(x["id"]), payload))

    def __get_player_data(self, player_id):
        response = self.session.get(self.endpoint + f"player/{player_id}")
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

    def __get_players(self):
        player_ids = self.get("player_ids")
        players_df = pd.DataFrame(player_ids, columns=["id"])
        players_df[["status", "name", "team", "position", "points", "average_points", "market_value"]] = players_df.id.progress_apply(lambda x: self.get("player_data", player_id=x)).apply(pd.Series)

        return players_df

    def __get_squads(self, league_id):
        response = self.session.get(self.endpoint + f"leagues/{league_id}/teams")
        payload = response.json()

        squad_df = pd.DataFrame()
        for squad in payload:
            squad_df = pd.concat([squad_df, pd.DataFrame(map(lambda x: (int(x["playerMaster"]["id"]), squad["manager"]["managerName"]), squad["players"]), columns=["player_id", "manager_name"])])
        return squad_df

    def __get_market(self, league_id):
        response = self.session.get(self.endpoint + f"league/{league_id}/market")
        payload = response.json()

        return list(map(lambda x: int(x["playerMaster"]["id"]), filter(lambda x: x["discr"] == "marketPlayerLeague", payload)))

    def __get_league_players(self, league_id):
        squads_df = self.get("squads", league_id=league_id)
        market_df = pd.DataFrame(self.get("market", league_id=league_id), columns=["player_id"])
        market_df["manager_name"] = None
        league_players_df = pd.concat([squads_df, market_df])

        return league_players_df
