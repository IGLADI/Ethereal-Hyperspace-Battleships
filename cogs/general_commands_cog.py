from discord import app_commands
import discord
from discord.ext import commands

from typing import Literal
from mariadb import IntegrityError
from player import Player
from utils import check_registered

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
        banner = NormalBanner(text=help_message, user=interaction.user)
        await interaction.response.send_message(embed=banner.embed, ephemeral=True)

    @app_commands.command(name="balance", description="Check your balance")
    @app_commands.check(check_registered)
    async def balance(self, interaction: discord.Interaction):
        if await check_player_exists(interaction) is False:
            return

        player = Player.get(interaction.user.id)
        betted_amount = get_betted_amount(interaction)
        balance = player.money
        balance -= betted_amount
        banner = NormalBanner(text=f"Your current balance is ${balance}.", user=interaction.user)
        await interaction.response.send_message(embed=banner.embed, ephemeral=True)

    # TODO maybe add displayname
    # ! (still keep id and add a check so that only one user can create an account with a name)
    @app_commands.command(name="register", description="Register as a player")
    async def register(
        self,
        interaction: discord.Interaction,
        player_class: Literal["martian", "dwarf", "droid"],
        guild_name: Literal["The Federation", "The Empire", "The Alliance", "The Independents"],
    ):
        if Player.exists(interaction.user.id):
            banner = ErrorBanner(text="You are already registered as a player.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        print("interaction.user.id:", interaction.user.id)

        try:
            Player.register(
                interaction.user.id,
                interaction.user.global_name,
                player_class,
                guild_name,
            )
        except IntegrityError:
            await interaction.response.send_message(
                "Duplicate values.",
                ephemeral=True,
            )
            return

        Player.get(interaction.user.id)

        banner = SuccessBanner(text="Welcome to Ethereal Hyperspace Battleships!", user=interaction.user)
        await interaction.response.send_message(embed=banner.embed, ephemeral=True)

    @app_commands.command(name="where_am_i", description="Get your location info")
    @app_commands.check(check_registered)
    async def where_am_i(self, interaction: discord.Interaction):
        """Returns the location of the player"""
        player = Player.get(interaction.user.id)
        coordinates = (player.x_pos, player.y_pos)
        location_name = player.location_name()
        banner = NormalBanner(
            text=f"You are currently at {coordinates}, also known as {location_name}.", user=interaction.user
        )
        await interaction.response.send_message(embed=banner.embed, ephemeral=True)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(GeneralCommands(client))
