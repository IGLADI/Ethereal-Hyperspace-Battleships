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

    # TODO add any additional commands here
    @app_commands.command(name="help", description="Provides a list of bot commands")
    async def help(
        self, 
        interaction: discord.Interaction, 
        page: Literal[
            'main', 'guild', 'resources', 'travel', 'economic'
        ] = 'main'
        ):

        # Main page command list
        def help_main():
            return {
                "help {page name}": "Show commands from that page"
            }
        
        # Guild page command list
        def help_guild():
            return {
                "guild": "Get guild info",
                "guild_members": "Get guild members",
                "guild_leave": "Leave your guild",
                "guild_join {guild name}": "Join a guild",
                "guild_create {guild name}": "Create a guild",
            }

        # Resources page command list
        def help_resources():
            return {
                "resources": "Get info on resources and mining",
                "mine": "Mine a random resource",
                "inventory": "Check your cargo",
                "sell {resource} {amount}": "Sell resources",
                "buy {resource} {amount}": "Buy resources",
            }

        # Travel page command list
        def help_travel():
            return {
                "where_am_i": "Get your location info",
                "travel {x} {y}": "Travel to a location",
                "scan": "Scan the area for players and locations",
            }

        # Economic page command list
        def help_economic():
            return {
                "balance": "Check your money",
                "pay {amount} {player}": "Give money to a player",
                "trade": "idk, i didn't write this...",
            }

        switch_dict = {
            'main': help_main,
            'guild': help_guild,
            'resources': help_resources,
            'travel': help_travel,
            'economic': help_economic        
        }

        help_function = switch_dict.get(page)
        commands = help_function()
        
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
        guild_name: Literal["The Federation", "The Empire", "The Alliance", "The Independents"],
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

        player = Player.get(interaction.user.id)

        await interaction.response.send_message(
            f"Welcome to Ethereal Hyperspace Battleships {player.name}!",
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
