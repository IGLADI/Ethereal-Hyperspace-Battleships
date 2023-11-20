from discord import app_commands
import discord
from discord.ext import commands

import data
from player import Player
from utils import check_player_exists, get_betted_amount


class GeneralCommands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="help", description="Need help?")
    async def help(self, interaction: discord.Interaction):
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
    # but discord seems to already block it and only start the new command once the first one has been processed
    @app_commands.command(name="give_money", description="Give money to a player")
    async def give_money(self, interaction: discord.Interaction, amount: int, member_recipient: discord.Member):
        if await check_player_exists(interaction) is False:
            return
        if amount <= 0:
            await interaction.response.send_message("Please provide a positive amount of money.", ephemeral=True)
            return
        if member_recipient not in data.players:
            await interaction.response.send_message("The recipient doesn't have an account.", ephemeral=True)
            return
        sender = data.players[interaction.user]
        recipient = data.players[member_recipient]
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

    @app_commands.command(name="check_balance", description="Check your balance")
    async def check_money(self, interaction: discord.Interaction):
        if await check_player_exists(interaction) is False:
            return

        player = data.players[interaction.user]
        betted_amount = get_betted_amount(interaction)
        money_amount = player.money
        money_amount -= betted_amount
        await interaction.response.send_message(f"Your current balance is ${money_amount}.", ephemeral=True)

    # TODO maybe add username
    # ! (still keep id or add a check so that only one user can create an account with a name)
    @app_commands.command(name="register_player", description="Register as a player")
    async def register_player(self, interaction: discord.Interaction):
        if interaction.user not in data.players:
            player = Player(interaction.user)
            data.players[interaction.user] = player
            await interaction.response.send_message(
                f"Welcome to Ethereal Hyperspace Battleships {interaction.user.name}!", ephemeral=True
            )
        else:
            await interaction.response.send_message("You are already registered as a player.", ephemeral=True)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(GeneralCommands(client))
