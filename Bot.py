import datetime
import math
import time

import discord
# https://discordpy.readthedocs.io/en/latest/index.html
# https://github.com/Rapptz/discord.py

from discord.ext import commands, tasks

MILLISECONDS_IN_HOUR = 1000 * 60 * 60
MILLISECONDS_IN_RAID = 3 * 24 * MILLISECONDS_IN_HOUR


def split_string(text, split='\n', max_length=2000):
    result = []
    length = 0
    current = ""

    for line in text.split(split):
        add = len(line)

        if length + add < max_length:
            current += line + split
            length += add + 1
            continue

        result.append(current)

        if len(line) <= max_length:
            current = line
            length = len(line)
            continue

        if split != ' ':
            new = split_string(line, split=' ', max_length=max_length)
            for entry in new:
                result.append(entry)

            current = ""
            length = 0
            continue

        while len(line) > max_length:
            result.append(line[:max_length])
            line = line[max_length:]

        result.append(line)

        current = ""
        length = 0

    if len(current) > 0:
        result.append(current)

    return result


def split_list(text, split='\n', max_length=2000):
    return split_string(split.join(text), split, max_length)


async def handle_reply(interaction, text, max_message_count=5):
    if text is None or len(text) == 0:
        return

    if isinstance(text, str):
        await interaction.response.send_message(text)
        return

    await interaction.response.send_message(text[0])

    if interaction.channel is not None:
        for i in range(1, min(max_message_count, len(text))):
            await interaction.channel.send(text[i])


class Bot:

    def __init__(self, token, intents, client, database):
        self.client = client
        self.db = database

        bot = commands.Bot(command_prefix='!', intents=intents, activity=discord.Game(name="Clash of Clans", type=3),
                           status=discord.Status.online)

        @bot.event
        async def on_ready():
            print('Logged in to Discord', bot.user)
            await bot.tree.sync()
            await client.log_in()

            task.start()

        @bot.tree.command(name="jäsenet", description="Listaa klaanin jäsenet")
        async def listaa_jasenet(interaction):
            data = await self.client.get_members()
            await handle_reply(interaction, split_list([row['name'] for row in data]))

        @bot.tree.command(name="raidi", description="Listaa viimeisimmän raidin tulokset")
        async def listaa_raidi(interaction):
            ended = not await self.is_raid_on()
            message = None if ended else f'Raidia jäljellä {await self.get_hours_left_on_raid()} tuntia'
            result = await self.get_raid_activity(message)
            await handle_reply(interaction, result)

        @bot.tree.command(name="muistutus", description="Lisää muistutus tekemättömistä raideista")
        async def muistutus(interaction, tunnit: int, tag: str):
            """Lisää muistutus tekemättömistä raideista

            Args:
                interaction (discord.Interaction): Interaction
                tunnit (int): Muistuta kun raidia on näin monta tuntia jäljellä. -1 poistaa muistutuksen
                tag (str): Clash of Clans -käyttäjän tägi
            """
            await handle_reply(interaction, await self.add_reminder(tunnit, interaction.user.id, tag))

        @bot.tree.command(name="päivitysnopeus",
                          description="Aseta kuinka monen tunnin välein lista raiditilanteesta lähetetään")
        async def paivitys_nopeus(interaction, tunnit: int):
            """Aseta kuinka monen tunnin välein lista raiditilanteesta lähetetään

                Args:
                    interaction (discord.Interaction): Interaction
                    tunnit (int): Monenko tunnin välein tilanne päivitetään
                """

            if not await self.is_manager(interaction.user):
                await interaction.response.send_message('Pyydä klaanin tai botin ylläpitoa vaihtamaan aikaa')
                return

            result = await self.set_update_frequency(tunnit)
            if result == 1:
                await interaction.response.send_message('Päivitysnopeus päivitetty')
                return

            await interaction.response.send_message('Anna kelvollinen aika väliltä 0-72 tuntia')

        @bot.tree.command(name="github", description="Linkki botin koodiin")
        async def github(interaction):
            await interaction.response.send_message('https://github.com/adex720/RaidBot')

        @bot.tree.command(name="tietokanta", description="Aja koodia botin tietokannassa (Vain botin omistaja)")
        async def tietokanta(interaction, syote: str):
            """Aja koodia botin tietokannassa (Vain botin omistaja)

                Args:
                    interaction (discord.Interaction): Interaction
                    syote (str): Koodi
                """
            if interaction.user.id != 560815341140181034:
                return

            await self.run_on_db(interaction, syote)

        @tasks.loop(minutes=31)
        async def task():
            print('Checking reminders')
            await self.check_reminders()

        self.bot = bot
        bot.run(token)

    async def is_manager(self, user):
        manager_roles = self.db.get_manager_roles()

        for role in user.roles:
            if role.id in manager_roles:
                return True

        return False

    async def get_raid_activity(self, only_missing=False, start_message=None):
        raid_data = await self.client.get_raid_activity()
        member_data = await self.client.get_members()

        # end = data['endTime']
        members = raid_data['members']

        result = []
        attacked = set()
        for member in members:
            result.append((-member['attacks'], member['name'] + ': ' + str(member['attacks']) + '/6'))
            # result.append({member['attacks'], member['name'] + ': ' + str(member['attacks']) + '/6, ' + str(
            #     member['capitalResourcesLooted'])})

            attacked.add(member['tag'])

        for member in member_data:
            if member['tag'] in attacked:
                continue

            result.append((0, member['name'] + ' 0/6'))

        if only_missing:
            result = [x for x in result if x[0] > -6]

        result.sort()

        begin = [] if start_message is None else [start_message]

        return split_list(begin + [rivi for m, rivi in result])

    async def is_raid_on(self):
        return await self.get_hours_left_on_raid() >= 0

    async def get_hours_left_on_raid(self):
        now = math.floor(time.time() * 1000)
        return (await self.get_end_time() - now) // MILLISECONDS_IN_HOUR

    async def get_hours_raid_has_been_active(self):
        now = math.floor(time.time() * 1000)
        return (now - await self.get_end_time() + MILLISECONDS_IN_RAID) // MILLISECONDS_IN_HOUR

    async def get_end_time(self):
        data = await self.client.get_raid_activity()

        end = data['endTime']  # yyyymmddThhmmss.000Z
        year = int(end[:4])
        month = int(end[4:6])
        day = int(end[6:8])
        hour = int(end[9:11])
        minute = int(end[11:13])
        second = int(end[13:15])

        date = datetime.datetime(year, month, day, hour, minute, second, tzinfo=datetime.timezone.utc)
        end_time = math.floor(date.timestamp() * 1000)

        return end_time

    async def check_reminders(self):
        raid_data = await self.client.get_raid_activity(override_cache=True)

        last_update = self.db.get_last_update_time()
        if not await self.is_raid_on():
            if last_update < await self.get_end_time():
                await self.send_info_message()

            return

        member_data = await self.client.get_members(override_cache=True)

        now = math.floor(time.time() * 1000)
        update_hours = self.db.get_update_frequency()
        next_update = last_update + update_hours * MILLISECONDS_IN_HOUR

        hours_left = await self.get_hours_left_on_raid()
        if now >= next_update and await self.get_hours_raid_has_been_active() >= update_hours // 2:
            await self.send_info_message()

        reminders = self.db.get_reminders()

        progress = {}

        for member in raid_data['members']:
            missing = 6 - member['attacks']
            tag = member['tag']
            progress[tag] = missing

        for member in member_data:
            tag = member['tag']

            if tag not in progress:
                progress[tag] = 6

        reminder_texts = []
        extra_tags = []

        for name, tag, hours, user_id in reminders:
            if tag not in progress:
                extra_tags.append(tag)
                continue

            missing = progress[tag]

            if missing == 0:
                continue

            if hours_left <= hours:
                reminder_texts.append(
                    '<@' + str(user_id) + '>, muista raidit! ' + name + ' tehnyt ' + str(6 - missing) + '/6')

        if len(reminder_texts) == 0:
            return

        channel = self.bot.get_channel(self.db.get_reminder_channel_id())
        for message in split_list(reminder_texts):
            await channel.send(message)

    async def send_info_message(self):
        ended = not await self.is_raid_on()
        message = 'Hyökkäykset jätti tekemättä:' if ended \
            else f'Raidia jäljellä {await self.get_hours_left_on_raid()} tuntia'

        text = await self.get_raid_activity(only_missing=True, start_message=message)

        channel = self.bot.get_channel(self.db.get_info_channel_id())
        for message in text:
            await channel.send(message)

        self.db.updated()

    async def add_reminder(self, hours, user_id, tag):
        if hours < -1 or hours > 72:
            return 'Anna tuntien määrä väliltä 0-72. Poista muistutus antamalla -1'

        if hours == -1:
            self.db.remove_by_tag(tag)
            return 'Poistettiin muistutus'

        result = await self.db.set_reminder_time(user_id, hours, tag, self.client)
        if result == -1:
            return 'Annettu tägi ei vastaa ketään klaanin pelaajista'
        if result == 0:
            return 'Luotiin uusi muistutus'
        if result == 1:
            return 'Päivitettiin pelaajan muistutus, ja siirrettiin se tälle Discord-käyttäjälle'

        return 'Jotain ihmeellistä tapahtui'

    async def set_update_frequency(self, frequency):
        if frequency < 0 or frequency > 72:
            return -1

        self.db.set_update_frequency(frequency)
        return 1

    async def run_on_db(self, interaction, command):
        cursor = self.db.db.cursor(buffered=True)
        try:
            cursor.execute(command)
            got = cursor.fetchall()
            self.db.db.commit()
            result = 'None'
            if got is not None:
                result = '\n'.join(', '.join(got))

        except Exception as e:
            result = repr(e)

        await handle_reply(interaction, result)
