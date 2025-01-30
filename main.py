import discord
from ClashOfClansClient import ClashOfClansClient

from Config import Config
from Bot import Bot


def main():
    config = Config('config.json')

    client = ClashOfClansClient(config.api_token, config.clan_tag)

    intents = discord.Intents.default()
    intents.message_content = True

    bot = Bot(config.bot_token, intents, client)

    # client.close()


if __name__ == "__main__":
    main()
