from discord import app_commands
import discord
from discord.ext import commands

import data
from player import Player
from utils import check_player_exists, get_betted_amount
from ui.simple_banner import SimpleBanner


class GeneralCommands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="help", description="Provides a list of bot commands")
    async def help(self, interaction: discord.Interaction):
        # Welcome message and tutorial
        help_message = "Welcome to Ethereal Hyperspace Battleships!\n"
        help_message += "To start out, please type /register followed by /tutorial.\n"
        # Command list
        help_message += "Here is a list of commands:\n"
        help_message += "/help - Get help\n"
        help_message += "/guild - Get guild info\n"
        help_message += "/resources - Get info on resources and mining\n"
        help_message += "/balance - Check your money\n"
        help_message += "/pay - Give money to a player\n"
        await interaction.response.send_message(help_message, ephemeral=True)

    @app_commands.command(name="balance", description="Check your balance")
    async def balance(self, interaction: discord.Interaction):
        if await check_player_exists(interaction) is False:
            return

        player = data.players[interaction.user]
        betted_amount = get_betted_amount(interaction)
        balance = player.money
        balance -= betted_amount
        balance_banner = SimpleBanner(user=interaction.user, text=f"Your current balance is ${balance}.")
        await interaction.response.send_message(embed=balance_banner.embed, ephemeral=True)

    # TODO maybe add displayname
    # ! (still keep id and add a check so that only one user can create an account with a name)
    @app_commands.command(name="register", description="Register as a player")
    async def register(self, interaction: discord.Interaction):
        if interaction.user not in data.players:
            player = Player(interaction.user)
            data.players[interaction.user] = player
            await interaction.response.send_message(
                f"Welcome to Ethereal Hyperspace Battleships {interaction.user.name}!", ephemeral=True
            )
        else:
            await interaction.response.send_message("You are already registered as a player.", ephemeral=True)

    @app_commands.command(name="where_am_i", description="Get your location info")
    async def where_am_i(self, interaction: discord.Interaction):
        """Returns the location of the player"""
        if await check_player_exists(interaction) is False:
            return

        player = data.players[interaction.user]
        player_location = player.ship.location
        location_name = player_location.is_planet()
        await interaction.response.send_message(
            f"You are currently at {player_location}, also known as {location_name}.", ephemeral=True
        )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(GeneralCommands(client))
