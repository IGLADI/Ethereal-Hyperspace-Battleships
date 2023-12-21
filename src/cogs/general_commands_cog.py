from discord import app_commands
import discord
from discord.ext import commands

from typing import Literal
from mariadb import IntegrityError
from player import Player
from ui.help_banner import HelpBanner
from ui.simple_banner import NormalBanner
from utils import send_bug_report
from utils import check_registered


class GeneralCommands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="help", description="Provides a list of bot commands")
    async def help(self, interaction: discord.Interaction):
        commands = {
            "balance": "Check your balance",
            "bug_report": "Report a bug",
            "register": "Register as a player",
            "where_am_i": "Get your location info",
        }
        banner = HelpBanner(commands, interaction.user)
        await interaction.response.send_message(embed=banner.embed, ephemeral=True)

    @app_commands.command(name="balance", description="Check your balance")
    @app_commands.check(check_registered)
    async def balance(self, interaction: discord.Interaction):
        player = Player.get(interaction.user.id)
        banner = NormalBanner(text=f"Your current balance is ${player.money}.", user=interaction.user)
        await interaction.response.send_message(embed=banner.embed, ephemeral=True)

    # TODO maybe add displayname
    # ! (still keep id and add a check so that only one user can create an account with a name)
    @app_commands.command(name="register", description="Register as a player")
    async def register(
        self,
        interaction: discord.Interaction,
        player_class: Literal["martian", "dwarf", "droid"],
        guild_name: Literal[
            "The Federation", "The Empire", "The Alliance", "The Independents"
        ],

    ):
        if Player.exists(interaction.user.id):
            await interaction.response.send_message("You are already registered as a player.", ephemeral=True)
            return

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
        role = discord.utils.get(interaction.guild.roles, name=guild_name)
        if role:
            await interaction.user.add_roles(role) 
        else:
            raise NotImplementedError

        await interaction.response.send_message(
            f"Welcome to Ethereal Hyperspace Battleships {interaction.user.name}!\n You are now registered as a {player_class} in {guild_name}.",
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
