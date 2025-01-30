import json


class Config:

    def __init__(self, path):
        file = open(path)
        j = json.load(file)

        self.clan_tag = j['clan-tag']
        self.api_token = j['coc-api-token']
        self.bot_token = j['bot-token']
