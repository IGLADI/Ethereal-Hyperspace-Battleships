from discord import app_commands
import discord
from discord.ext import commands

from typing import Literal
from mariadb import IntegrityError
from player import Player
from utils import send_bug_report
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
        await interaction.response.send_message(help_message, ephemeral=True)

    @app_commands.command(name="balance", description="Check your balance")
    @app_commands.check(check_registered)
    async def balance(self, interaction: discord.Interaction):
        player = Player.get(interaction.user.id)
        await interaction.response.send_message(f"Your current balance is ${player.money}.", ephemeral=True)

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
            await interaction.response.send_message("You are already registered as a player.", ephemeral=True)
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

        await interaction.response.send_message(
            f"Welcome to Ethereal Hyperspace Battleships {interaction.user.name}!",
            ephemeral=True,
        )

    @app_commands.command(name="where_am_i", description="Get your location info")
    @app_commands.check(check_registered)
    async def where_am_i(self, interaction: discord.Interaction):
        """Returns the location of the player"""
        player = Player.get(interaction.user.id)
        coordinates = (player.x_pos, player.y_pos)
        location_name = player.location_name()
        await interaction.response.send_message(
            f"You are currently at {coordinates}, also known as {location_name}.",
            ephemeral=True,
        )

    @app_commands.command(name="bug_report", description="Report a bug")
    async def bug_report(
        self,
        interaction: discord.Interaction,
        bug_description: str,
    ):
        """Report a bug"""
        await interaction.response.send_message("Sending Report", ephemeral=True)
        await interaction.delete_original_response()

        send_bug_report(interaction.user.id, bug_description)

        await interaction.user.send(
            f"Thank you for your bug report: {bug_description}. The team will take a look and fix this issue as soon as possible."
        )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(GeneralCommands(client))
