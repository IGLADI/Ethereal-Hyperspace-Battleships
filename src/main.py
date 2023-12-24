import args

import discord
from discord.ext import commands

from create_channels import create_channels

import json
import argparse
import random
import asyncio

import data
from planet import Planet
from player import Player
from event import EventManager

from create_roles import create_roles
from ui.simple_banner import SimpleBanner

# check discord.py docs AND discord developer portal docs, please use cogs and slash commands (discord.py 2.0)
# https://discordpy.readthedocs.io/en/stable/interactions/api.html
# https://discord.com/developers/docs/interactions/receiving-and-responding

# TODO add some eastereggs (42)

# ! check for racing condition (buying something while betting ect) => use get_betted_amount(interaction) & ...
# discord seems to already block it and only process one command at a time per user


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
            "cogs.mine_cog",
            "cogs.travel_cog",
            "cogs.trade_cog",
            "cogs.combat_cog",
            "cogs.event_cog",
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
        # EventManager (only workking on 1 server)
        guild = self.guilds[0]
        event_manager = EventManager(guild)
        event_manager.start_event_timer()
        data.event_manager = event_manager


# load the bot token from config.json KEEP THIS TOKEN PRIVATE (gitignore)
with open("config.json", "r") as f:
    config_data = json.load(f)
    TOKEN = config_data["bot_token"]

# create the bot
client = Client()

# message from the bot when it joins a server
@client.event
async def on_guild_join(guild):
    # Forloop used per the documentation to send the message in the first channel that the bot can send messages in
    # by discord this is the welcome channel (where you see people join a server)
    global_guild = guild
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            # TODO should have a complete intro message
            await channel.send("Hello! Welcome to Ethereal Hyperspace Battleships type /help for more info.")
        break
    try:
        await create_roles(guild)
        await create_channels(guild)
    except Exception as e:
        await channel.send(
            "This bot can only run on community servers. Not on private servers! Bye!\n https://support.discord.com/hc/en-us/articles/360047132851-Enabling-Your-Community-Server"
        )
        await guild.leave()


@client.event
async def on_message(message):
    if client.user == message.author:
        return
    channel = message.channel

    if not isinstance(channel, discord.TextChannel):
        return
    if not isinstance(channel.category, discord.CategoryChannel):
        return
    if channel.category.name not in data.guild_names:
        return

    player = Player.get(message.author.id)
    if player.on_message_reward_cooldown:
        return

    if random.randint(1, data.REWARD_ON_MESSAGE_CHANCE) != 1:
        return

    player.money += 1000
    banner = SimpleBanner(text="You got 1000$ for sending a message!", user=message.author, color=discord.Color.gold())
    await channel.send(embed=banner.embed)

    # 4. if he got a reward start the cooldown
    player.on_message_reward_cooldown = True
    await asyncio.sleep(data.REWARD_ON_MESSAGE_COOLDOWN)
    player.on_message_reward_cooldown = False


# start the bot with the token in the config file
client.run(TOKEN)


# TODO check Rich presence on discord developer portal to show activity on profiles
# ? TODO add a "try my commands" (see midjourneys profile)
