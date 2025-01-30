import discord

from discord.ext import commands


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
    if isinstance(text, str):
        await interaction.response.send_message(text)
        return

    await interaction.response.send_message(text[0])

    if interaction.channel is not None:
        for i in range(1, min(max_message_count, len(text))):
            await interaction.channel.send(text[i])


class Bot:

    def __init__(self, token, intents, client):
        self.client = client

        bot = commands.Bot(command_prefix='!', intents=intents, activity=discord.Game(name="Clash of Clans", type=3),
                           status=discord.Status.online)

        @bot.event
        async def on_ready():
            print('Logged in to Discord', bot.user)
            await bot.tree.sync()
            await client.log_in()

        @bot.tree.command(name="jasenet", description="Listaa klaanin jäsenet")
        async def listaa_jasenet(interaction):
            data = await self.client.get_members()
            await handle_reply(interaction, split_list([row['name'] for row in data]))

        @bot.tree.command(name="raidi", description="Listaa viimeisimmän raidin tulokset")
        async def listaa_raidi(interaction):
            result = await self.get_raid_activity()
            await handle_reply(interaction, result)

        bot.run(token)

    async def get_raid_activity(self):
        data = await self.client.get_raid_activity()
        # end = data['endTime']
        members = data['members']

        result = []
        attacked = set()
        for member in members:
            result.append((-member['attacks'], member['name'] + ': ' + str(member['attacks']) + '/6'))
            # result.append({member['attacks'], member['name'] + ': ' + str(member['attacks']) + '/6, ' + str(
            #     member['capitalResourcesLooted'])})

            attacked.add(member['tag'])

        member_data = await self.client.get_members()

        for member in member_data:
            if member['tag'] in attacked:
                continue

            result.append((0, member['name'] + ' 0/6'))

        result.sort()

        return split_list([rivi for m, rivi in result])
