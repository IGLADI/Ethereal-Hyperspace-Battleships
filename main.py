import discord
from discord.ext import commands

import json

# check discord.py docs AND discord developer portal docs, please use cogs and slash commands (discord.py 2.0)
# https://discordpy.readthedocs.io/en/stable/interactions/api.html
# https://discord.com/developers/docs/interactions/receiving-and-responding

# TODO add some eastereggs (42)

# TODO implement nice messages (temporary messages have been made for dev but need to be cleaned up for final version)
# TODO add asci emojis/tabulate/figlet/... to the msgs (also colors?)

# ! check for racing condition (buying something while betting ect) => use get_betted_amount(interaction) & ...
# discord seems to already block it and only process one command at a time per user

# TODO save all the data every minute in a json file and when the bot is started again load the data from the json
# ? OR directly save the data in a json file and load it for each action (might be slow)
# ? or use a (local) database


class Client(commands.Bot):
    def __init__(self):
        # intents = what does the bot listen to (subscibe to certain webhooks)
        # (for development all intents are enabled)
        intents = discord.Intents.all()
        # intialize the bot with intents to support slash commands
        super().__init__(command_prefix="/", intents=intents)

        # load the slash commands from the different cog files
        self.cogslist = [
            "cogs.general_commands_cog",
            "cogs.casino_games.casino_cog",
            "cogs.casino_games.race_game_cog",
            "cogs.ship_cog",
        ]

    # this overwrites the default sync setup (used by self.tree.sync in on_ready)
    async def setup_hook(self):
        for ext in self.cogslist:
            await self.load_extension(ext)

    # when the bot is started
    async def on_ready(self):
        print(f"Logged in as {self.user.name}")
        print("--------------------------------------------")
        try:
            # sync slash commands with discord to show in command menu
            synced = await self.tree.sync()
            print(f"Synced {synced} commands")
        except Exception as e:
            print(e)
        print("--------------------------------------------")


# load the bot token from config.json KEEP THIS TOKEN PRIVATE (gitignore)
with open("config.json", "r") as f:
    data = json.load(f)
    TOKEN = data["bot_token"]

# create the bot
client = Client()


# message from the bot when it joins a server
@client.event
async def on_guild_join(guild):
    # Forloop used per the documentation to send the message in the first channel that the bot can send messages in
    # by discord this is the welcome channel (where you see people join a server)
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            # TODO should have a complete intro message
            await channel.send("Hello! Welcome to Ethereal Hyperspace Battleships type /help for more info.")
        break


# start the bot with the token in the config file
client.run(TOKEN)


# TODO check Rich presence on discord developer portal to show activity on profiles
# ? TODO add a "try my commands" (see midjourneys profile)
