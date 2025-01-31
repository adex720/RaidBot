import json


class Config:

    def __init__(self, path):
        file = open(path)
        j = json.load(file)

        self.clan_tag = j['clan-tag']
        self.api_token = j['coc-api-token']

        self.bot_token = j['bot-token']

        self.database_address = j['database-address']
        self.database_port = j['database-port']
        self.database_name = j['database-name']
        self.database_username = j['database-user']
        self.database_password = j['database-password']
