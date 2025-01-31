import coc
# https://cocpy.readthedocs.io/en/latest/models/players.html
# https://github.com/mathsman5133/coc.py

import math
import time


class ClashOfClansClient:
    cached_members = None
    members_updated = 0

    cached_raid = None
    raid_updated = 0

    cache_time = 1000 * 60 * 15

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

    async def get_members(self, override_cache=False):
        if not self.connected:
            return ['Not connected to Clash of Clans api']

        now = math.floor(time.time() * 1000)
        if override_cache or now > self.members_updated + self.cache_time:
            data = await self.client.http.get_clan_members(self.clan_tag)
            self.cached_members = data['items']
            self.members_updated = now

        return self.cached_members

    async def get_raid_activity(self, override_cache=False):
        if not self.connected:
            return ['Not connected to Clash of Clans api']

        now = math.floor(time.time() * 1000)
        if override_cache or now > self.raid_updated + self.cache_time:
            data = await self.client.http.get_clan_raid_log(self.clan_tag, **{"limit": 1})
            self.cached_raid = data['items'][0]
            self.raid_updated = now

        return self.cached_raid
