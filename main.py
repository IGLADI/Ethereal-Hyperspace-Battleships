import discord
from discord.ext import commands
import json
from player import Player

# check discord.py docs AND https://discord.com/developers/docs/interactions/receiving-and-responding
# discord official docs is better to support /commands but discord.py explains a lot about bases of the library

# TODO implement nice messages (temporary messages have been made for dev but need to be cleaned up)

# intents = what does the bot listen, for (for development all intents are enabled)
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
    print("------")
    try:
        # sync slash commands with discord to show in command menu
        synced = await bot.tree.sync()
        print(f"Synced {synced} commands")
    except Exception as e:
        print(e)
    print("------")


# message from the bot when it joins a server
@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            # TODO make a clean intro message with /help ect
            await channel.send("Hello! I'm Ethereal Hyperspace Battleships")
        break


# TODO save all the data every minute in a json file and when the bot is started again load the data from the json
# initialize data, this is temporary and will be replaced by a json file
players = {}


# all bot commands
# per trial & discord developer portal documentation (not discord.py):
# try using bot.tree and discord.Interaction instead of bot and ctx


@bot.tree.command(name="help", description="Need help?")
async def help(interaction: discord.Interaction):
    help_message = ""
    help_message += "Welcome to Ethereal Hyperspace Battleships!\n"
    help_message += "Here is a list of commands:\n"
    help_message += "/help - Get help\n"
    help_message += "/register_player - Register as a player\n"
    help_message += "/check_money - Check your money\n"
    help_message += "/give_money - Give money to a player\n"
    # TODO add all your commands here
    await interaction.response.send_message(help_message)


@bot.tree.command(name="give_money", description="Give money to a player")
async def give_money(interaction: discord.Interaction, amount: int, member: discord.Member):
    if amount <= 0:
        await interaction.response.send_message("Please provide a positive amount of money.")
        return
    if interaction.user not in players:
        await interaction.response.send_message("You are not registered as a player.")
        return
    if member not in players:
        await interaction.response.send_message("The recipient doesn't have an account.")
        return

    sender = players[interaction.user]
    recipient = players[member]

    if sender.money < amount:
        await interaction.response.send_message("You don't have enough money.")
        return

    sender.money -= amount
    recipient.money += amount
    await interaction.response.send_message(f"You gave {amount}$ to {member.name}.")


@bot.tree.command(name="check_balance", description="Check your balance")
async def check_money(interaction: discord.Interaction):
    if interaction.user in players:
        player = players[interaction.user]
        money_amount = player.money
        await interaction.response.send_message(f"Your current balance is {money_amount}$.")
    else:
        await interaction.response.send_message("You are not registered as a player.")


@bot.tree.command(name="register_player", description="Register as a player")
async def register_player(interaction: discord.Interaction):
    if interaction.user not in players:
        player = Player(interaction.user)
        players[interaction.user] = player
        await interaction.response.send_message(f"Welcome to Ethereal Hyperspace Battleships {interaction.user.name}!")
    else:
        await interaction.response.send_message("You are already registered as a player.")


# start the bot with the token in the config file
bot.run(TOKEN)
