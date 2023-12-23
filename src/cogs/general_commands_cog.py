from discord import app_commands
import discord
from discord.ext import commands

from typing import Literal
from mariadb import IntegrityError
from player import Player
from ui.help_banner import HelpBanner
from ui.simple_banner import ErrorBanner, NormalBanner
from utils import send_bug_report
from utils import check_registered
from tutorial import Tutorial
import asyncio


class GeneralCommands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    # TODO add any additional commands here
    @app_commands.command(name="help", description="Provides a list of bot commands")
    @app_commands.check(check_registered)
    async def help_command(self, interaction: discord.Interaction):
        banner = HelpBanner(interaction.user)
        await interaction.response.send_message(embed=banner.embed, view=banner, ephemeral=True)

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
            banner = ErrorBanner(interaction.user, "You are already registered as a player.")
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
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

        banner = NormalBanner(
            text=f"Welcome to Ethereal Hyperspace Battleships {interaction.user.name}!\n You are now registered as a {player_class} in {guild_name}.",
            user=interaction.user,
        )
        await interaction.response.send_message(embed=banner.embed, ephemeral=True)

    @app_commands.command(name="tutorial", description="Start a tutorial to learn how to play")
    @app_commands.check(check_registered)
    async def tutorial(self, interaction: discord.Interaction):
        player = Player.get(interaction.user.id)
        if player._tutorial == 1:
            banner = ErrorBanner(interaction.user, "You have already completed the tutorial.")
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return
        if player._tutorial == 0:
            banner = ErrorBanner(interaction.user, "You are already in the tutorial.")
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return
        player._tutorial = 0

        banner = NormalBanner(
            text=f"Welcome to the tutorial {interaction.user.name}!\n We just got a distress call from Ruebñ... He need help on the coordinates (0,0). Can you travel to him and help him out using the /travel command?",
            user=interaction.user,
        )
        await interaction.response.send_message(embed=banner.embed, ephemeral=True)
        tut = Tutorial(player)
        tut.travel_to_Ruebn()
        while tut._travelled == False:
            await asyncio.sleep(1)
        banner = NormalBanner(
            text=f"Thank you for coming {interaction.user.name}!\n We just got attacked by space pirates! They fled right before you arrived. Can you use your radar to scan the area and find them? (/scan)",
            user=interaction.user,
        )
        await asyncio.sleep(3)
        await interaction.followup.send(embed=banner.embed, ephemeral=True)
        tut.scan_for_pirates()

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
