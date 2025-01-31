import discord
from ClashOfClansClient import ClashOfClansClient

from Bot import Bot
from Config import Config
from Database import Database


def main():
    config = Config('config.json')

    database = Database(config.database_address, config.database_port, config.database_name, config.database_username,
                        config.database_password)

    client = ClashOfClansClient(config.api_token, config.clan_tag)

    intents = discord.Intents.default()
    intents.message_content = True

    bot = Bot(config.bot_token, intents, client, database)

    # client.close()


if __name__ == "__main__":
    main()
