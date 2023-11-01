MAIN_URL = "https://api-fantasy.llt-services.com/api/v3/"

class FantasyAPI:
    def __init__(self, token):
        self.headers = {
            'Authorization': f'Bearer {token}'
        }
