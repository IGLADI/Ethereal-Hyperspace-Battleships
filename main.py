import discord
from discord.ext import commands
from typing import Literal
from tabulate import tabulate
import json
import random
import asyncio
import time
from player import Player
from races import Racer

# check discord.py docs AND discord developer portal docs
# https://discordpy.readthedocs.io/en/stable/interactions/api.html
# https://discord.com/developers/docs/interactions/receiving-and-responding

# TODO implement nice messages (temporary messages have been made for dev but need to be cleaned up for final version)
# TODO add asci emojis/tabulate/figlet/... to the msgs (also colors?)
# ! check for racing condition (buying something while betting ect) => use betted_amount(interaction) & ...

# intents = what does the bot listen to (subscibe to certain webhooks)
# (for development all intents are enabled)
intents = discord.Intents.all()

# load the bot token from config.json KEEP THIS TOKEN PRIVATE (gitignore)
with open("config.json", "r") as config_file:
    config_data = json.load(config_file)
    TOKEN = config_data.get("bot_token", "")

# intialize the bot to support slash commands
bot = commands.Bot(command_prefix="/", intents=intents)


# when the bot is started
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print("--------------------------------------------")
    try:
        # sync slash commands with discord to show in command menu
        synced = await bot.tree.sync()
        print(f"Synced {synced} commands")
    except Exception as e:
        print(e)
    print("--------------------------------------------")


# message from the bot when it joins a server
@bot.event
async def on_guild_join(guild):
    # Forloop used per the documentation to send the message in the first channel that the bot can send messages in
    # by discord this is the welcome channel (where you see people join a  server)
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            # TODO should have a complete intro message
            await channel.send("Hello! Welcome to Ethereal Hyperspace Battleships type /help for more info.")
        break


# TODO save all the data every minute in a json file and when the bot is started again load the data from the json
# ? OR directly save the data in a json file and load it for each action (might be slow)
# initialize data, this is temporary and will be replaced by a json file
players = {}
race_games = {}


# all bot commands
# per trial & discord developer portal documentation (not discord.py):
# try using bot.tree and discord.Interaction instead of bot and ctx


async def check_player_exists(interaction):
    if interaction.user not in players:
        await interaction.response.send_message("You are not registered as a player.", ephemeral=True)
        return False
    return True


@bot.tree.command(name="help", description="Need help?")
async def help(interaction: discord.Interaction):
    help_message = ""
    help_message += "Welcome to Ethereal Hyperspace Battleships!\n"
    help_message += "Here is a list of commands:\n"
    help_message += "/help - Get help\n"
    help_message += "/register_player - Register as a player\n"
    help_message += "/check_balance - Check your money\n"
    help_message += "/give_money - Give money to a player\n"
    help_message += "/organize_casino_game - Organize a casino game in this channel\n"
    help_message += "/bet_on_race - Bet on a race\n"
    # TODO add all your commands here
    await interaction.response.send_message(help_message, ephemeral=True)


# ? TODO maybe add a min lvl to give money (avoid spamming discord acounts)
# Checked for race condition (spamming the command to multiply money because that money can't go under 0)
# but discord seems to already block it and only start the new command one the first one has been processed (per user)
@bot.tree.command(name="give_money", description="Give money to a player")
async def give_money(interaction: discord.Interaction, amount: int, member_recipient: discord.Member):
    if await check_player_exists(interaction) is False:
        return
    if amount <= 0:
        await interaction.response.send_message("Please provide a positive amount of money.", ephemeral=True)
        return
    if member_recipient not in players:
        await interaction.response.send_message("The recipient doesn't have an account.", ephemeral=True)
        return
    sender = players[interaction.user]
    recipient = players[member_recipient]
    betted_amount = get_betted_amount(interaction)
    if sender == recipient:
        await interaction.response.send_message("You can't give money to yourself.", ephemeral=True)
        return
    if sender.money - betted_amount < amount:
        await interaction.response.send_message("You don't have enough money.", ephemeral=True)
        return

    sender.money -= amount
    recipient.money += amount
    await interaction.response.send_message(f"You gave ${amount} to {member_recipient.name}.")


@bot.tree.command(name="check_balance", description="Check your balance")
async def check_money(interaction: discord.Interaction):
    if await check_player_exists(interaction) is False:
        return

    player = players[interaction.user]
    betted_amount = get_betted_amount(interaction)
    money_amount = player.money
    money_amount -= betted_amount
    await interaction.response.send_message(f"Your current balance is ${money_amount}.", ephemeral=True)


# TODO maybe add username (still keep id or add a check so that only one user can create an account with a name)
@bot.tree.command(name="register_player", description="Register as a player")
async def register_player(interaction: discord.Interaction):
    if interaction.user not in players:
        player = Player(interaction.user)
        players[interaction.user] = player
        await interaction.response.send_message(
            f"Welcome to Ethereal Hyperspace Battleships {interaction.user.name}!", ephemeral=True
        )
    else:
        await interaction.response.send_message("You are already registered as a player.", ephemeral=True)


# TODO add a /get_race_info command that explains the differencez
# TODO add imgs (AI/start w hardcoded)
race_details = {
    "blob": {"distance": 10, "min_speed": 0, "max_speed": 1},
    "swoop": {"distance": 1000, "min_speed": 10, "max_speed": 50},
    "ratts": {"distance": 100, "min_speed": 0, "max_speed": 10},
    "pod": {"distance": 10000, "min_speed": 25, "max_speed": 100},
}


# TODO maybe make a discord thread for the race?
# TODO split this function into multiple functions & split functions across multiple files (using cogs)
@bot.tree.command(name="organize_casino_race", description="casino racing game")
async def organize_casino_race(
    interaction: discord.Interaction,
    race_type: Literal["blob", "swoop", "ratts", "pod"],
    amount_of_racers: int,
):
    race_info = race_details.get(race_type.lower())
    race_distance = race_info["distance"]
    min_speed = race_info["min_speed"]
    max_speed = race_info["max_speed"]
    global race_games

    if await check_player_exists(interaction) is False:
        return
    if amount_of_racers < 2:
        await interaction.response.send_message("You need at least 2 racers.", ephemeral=True)
        return
    if amount_of_racers > 50:
        await interaction.response.send_message("You can't have more than 50 racers.", ephemeral=True)
        return
    if interaction.channel_id in race_games:
        await interaction.response.send_message("A race is already in progress in this channel.", ephemeral=True)
        return

    race_games[interaction.channel_id] = {
        "racers": [],
        "bets": [],
    }
    racers = []
    timer = 60

    intro = f"Welcome to this {race_type} race! \nGive a hard applause to the racers:"
    for _ in range(amount_of_racers):
        new_racer = Racer()
        # don't create 2 racers with the same first name
        while any(racer.name.split(" ")[0] == new_racer.name.split(" ")[0] for racer in racers):
            new_racer = Racer()
        racers.append(new_racer)
        intro += f"\n{racers[-1].name}"
    await interaction.response.send_message(intro)
    message_to_send = f"A new race game will begin in {timer}s! \n"
    message_to_send += "Type `/bet_on_race <bet_amount> <player_to_bet_on>` to participate."
    message = await interaction.followup.send(message_to_send, wait=True)
    race_games[interaction.channel_id]["racers"] = racers

    while True:
        if timer <= 0:
            break
        message_to_send = f"A new race game will begin in {timer}s! \n"
        message_to_send += "Type `/bet_on_race <bet_amount> <player_to_bet_on>` to participate."
        timer -= 1
        await message.edit(content=message_to_send)
        await asyncio.sleep(1)
    await message.delete()

    if len(race_games[interaction.channel_id].get("bets", [])) < 2:
        await interaction.followup.send("Not enough players to start the race.")
        del race_games[interaction.channel_id]
        return

    start_message = f"The {race_type} race is starting now!"
    start_message += "\nHere are the bets:"
    bet_table = []
    headers = ["Player", "Bet Amount", "Racer"]
    for bet in race_games[interaction.channel_id].get("bets", []):
        bet_table.append([bet["player"], bet["bet_amount"], bet["racer_to_bet_on"]])
    table = tabulate(bet_table, headers=headers)
    await interaction.followup.send(f"{start_message}\n```{table}```")
    racers_list = race_games[interaction.channel_id]["racers"]
    distances = [racer.distance for racer in racers_list]
    race_status = []
    for racer in racers_list:
        distance = 0
        race_status.append([racer.name, f"{distance}m"])
    race_table = tabulate(race_status, headers=["Racer", "Distance"])
    message = await interaction.followup.send(f"```\n{race_table}\n```", wait=True)

    while max(distances) < race_distance:
        race_data = []
        for racer in racers_list:
            racer.distance += random.randint(min_speed, max_speed)
            distance = race_distance if racer.distance > race_distance else racer.distance
            # ? maybe add 0000.. so that amount of numbers dont change
            race_data.append([racer.name, f"{distance}m"])

        race_table = tabulate(race_data, headers=["Racer", "Distance"])
        await message.edit(content=f"```\n{race_table}\n```")
        distances = [racer.distance for racer in racers_list]
        time.sleep(0.1)

    winner = max(race_games[interaction.channel_id]["racers"], key=lambda racer: racer.distance)
    winner_message = f"The winner is {winner.name}!"
    await interaction.followup.send(content=winner_message)

    player_winnings = {}
    for bet in race_games[interaction.channel_id].get("bets", []):
        player_winnings[bet["player"]] = 0
    for bet in race_games[interaction.channel_id].get("bets", []):
        if bet["racer_to_bet_on"].strip().lower().split(" ")[0] == winner.name.strip().lower().split(" ")[0]:
            player_winnings[bet["player"]] += bet["bet_amount"] * (amount_of_racers - 1)
        else:
            player_winnings[bet["player"]] -= bet["bet_amount"]

    for player, amount in player_winnings.items():
        if amount > 0:
            await interaction.followup.send(f"{player.name} won ${amount}!")
        elif amount < 0:
            await interaction.followup.send(f"{player.name} lost ${-amount}!")
    for player, amount in player_winnings.items():
        players[player].money += amount

    del race_games[interaction.channel_id]


def get_betted_amount(interaction):
    betted_amount = 0
    for channel_id in race_games:
        for bet in race_games[channel_id]["bets"]:
            if interaction.user == bet["player"]:
                betted_amount += bet["bet_amount"]
    return betted_amount


# ? maybe change this to use discord drop down menus? (to choose on which racer to bet on)
# TODO add a command to modify/remove betts
@bot.tree.command(name="bet_on_race", description="Bet...")
async def bet_on_race(interaction: discord.Interaction, betamount: int, racer_to_bet_on: str):
    global race_games
    if await check_player_exists(interaction) is False:
        return
    if interaction.channel_id not in race_games:
        await interaction.response.send_message(
            "No race game is currently in progress in this channel.", ephemeral=True
        )
        return
    betted_amount = get_betted_amount(interaction)
    if players[interaction.user].money - betted_amount < betamount:
        await interaction.response.send_message("You don't have enough money.", ephemeral=True)
        return
    if any(
        bet["player"] == interaction.user
        and bet["racer_to_bet_on"].strip().lower().split(" ")[0] == racer_to_bet_on.strip().lower().split(" ")[0]
        for bet in race_games[interaction.channel_id]["bets"]
    ):
        # TODO modify the message once the ... commands are implemented
        await interaction.response.send_message(
            f"You have already bet on {racer_to_bet_on.capitalize()} for this race.\n use ... to change your bets",
            ephemeral=True,
        )
        return
    racers_in_channel = race_games[interaction.channel_id]["racers"]
    if not any(
        racer.name.strip().lower().split(" ")[0] == racer_to_bet_on.strip().lower().split(" ")[0]
        for racer in racers_in_channel
    ):
        racer_names = "\n".join([racer.name for racer in racers_in_channel])
        await interaction.response.send_message(
            f"This racer isn't in the race!\nPlease pick one of the following racers:\n{racer_names}", ephemeral=True
        )
        return

    race_games[interaction.channel_id]["bets"].append(
        {"player": interaction.user, "bet_amount": betamount, "racer_to_bet_on": racer_to_bet_on}
    )
    # ? maybe always display first+last name?
    await interaction.response.send_message(f"You have bet ${betamount} on {racer_to_bet_on.capitalize()}.")


# TODO check Rich presence on discord developer portal to show activity on profiles
# TODO add a "try my commands" & add app buttun (see midjourneys profile)


# start the bot with the token in the config file
bot.run(TOKEN)
