from discord import app_commands
import discord
from discord.ext import commands

from typing import Literal
from mariadb import IntegrityError
from player import Player


async def check_registered(interaction: discord.Interaction) -> bool:
    """Check if a player is registered, if not sends an error message. Else run the function."""
    if not Player.exists(interaction.user.id):
        await interaction.response.send_message(
            "You are not registered as a player.", ephemeral=True
        )
        return False
    return True


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

    # ? TODO maybe add a min lvl to give money (avoid spamming discord acounts)
    # Checked for race condition (spamming the command to multiply money because that money can't go under 0)
    # but discord seems to already block it and only start the new command once the first one has been processed
    @app_commands.command(name="pay", description="Gift money to a player")
    @app_commands.check(check_registered)
    async def pay(
        self,
        interaction: discord.Interaction,
        amount_to_pay: int,
        member_recipient: discord.Member,
    ):
        sender_id = interaction.user.id
        recipient_id = member_recipient.id

        if sender_id == recipient_id:
            await interaction.response.send_message(
                "You can't give money to yourself.", ephemeral=True
            )
            return

        if amount_to_pay <= 0:
            await interaction.response.send_message(
                "Please provide a positive amount of money.", ephemeral=True
            )
            return

        if not Player.exists(recipient_id):
            await interaction.response.send_message(
                "The recipient doesn't have an account.", ephemeral=True
            )
            return

        sender = Player.get(sender_id)
        recipient = Player.get(recipient_id)

        if sender.money < amount_to_pay:
            await interaction.response.send_message(
                "You don't have enough money.", ephemeral=True
            )
            return

        sender.money = sender.money - amount_to_pay
        recipient.money = recipient.money + amount_to_pay

        await interaction.response.send_message(
            f"You gave ${amount_to_pay} to {member_recipient.name}."
        )

    @app_commands.check(check_registered)
    @app_commands.command(name="balance", description="Check your balance")
    async def balance(self, interaction: discord.Interaction):
        player = Player.get(interaction.user.id)
        balance = player.money
        await interaction.response.send_message(
            f"Your current balance is ${balance}.", ephemeral=True
        )

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
            await interaction.response.send_message(
                "You are already registered as a player.", ephemeral=True
            )
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
                f"Duplicate values.",
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
    async def bug_report(self, interaction: discord.Interaction, bug_report: str):
        """Report a bug"""
        player = Player.get(interaction.user.id)
        player.report_bug(bug_report)
        await interaction.response.send_message(
            f"Your bug report has been sent. Thank you for your feedback!",
            ephemeral=True,
        )

async def setup(client: commands.Bot) -> None:
    await client.add_cog(GeneralCommands(client))
