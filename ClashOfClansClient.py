import coc


class ClashOfClansClient:

    def __init__(self, token, clan_tag):
        self.clan_tag = clan_tag
        self.client = coc.Client()

        self.token = token
        self.connected = False

    async def log_in(self):
        if self.connected:
            return

        await self.client.login_with_tokens(self.token)
        self.connected = True
        print('Connected to COC-api')

    async def close(self):
        if not self.connected:
            return

        with self.client.close() as _:
            self.connected = False
            print('Disconnected from COC-api')

    async def get_members(self):
        if not self.connected:
            return ['Not connected to Clash of Clans api']

        data = await self.client.http.get_clan_members(self.clan_tag)
        return data['items']

    async def get_raid_activity(self):
        if not self.connected:
            return ['Not connected to Clash of Clans api']

        raw = await self.client.http.get_clan_raid_log(self.clan_tag, **{"limit": 1})
        return raw['items'][0]
