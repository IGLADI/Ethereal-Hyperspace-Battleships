from discord import app_commands
import discord
from discord.ext import commands

import data
from player import Player
from utils import check_player_exists, get_betted_amount


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
    async def pay(self, interaction: discord.Interaction, amount_to_pay: int, member_recipient: discord.Member):
        if await check_player_exists(interaction) is False:
            return
        if amount_to_pay <= 0:
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
        if sender.money - betted_amount < amount_to_pay:
            await interaction.response.send_message("You don't have enough money.", ephemeral=True)
            return

        sender.money -= amount_to_pay
        recipient.money += amount_to_pay
        await interaction.response.send_message(f"You gave ${amount_to_pay} to {member_recipient.name}.")

    @app_commands.command(name="balance", description="Check your balance")
    async def balance(self, interaction: discord.Interaction):
        if await check_player_exists(interaction) is False:
            return

        player = data.players[interaction.user]
        betted_amount = get_betted_amount(interaction)
        balance = player.money
        balance -= betted_amount
        await interaction.response.send_message(f"Your current balance is ${balance}.", ephemeral=True)

    # TODO maybe add displayname
    # ! (still keep id and add a check so that only one user can create an account with a name)
    @app_commands.command(name="register", description="Register as a player")
    async def register(self, interaction: discord.Interaction, player_class: str):
        db = Database()
        if db.player_exists(interaction.user.id):
            await interaction.response.send_message(
                "You are already registered as a player.", ephemeral=True
            )
            return

        # TODO: mariadb errors
        # - Integrity error: "You are already logged in"
        # - DataError: "Wrong class."
        db.get_guild_player_counts()
        db.connection.commit()
        results = db.get_results()
        next_guild = database.get_next_guild(results)
        db.store_player(
            interaction.user.id,
            interaction.user.global_name,
            player_class,
            next_guild,
        )
        db.connection.commit()

        await interaction.response.send_message(
            f"Welcome to Ethereal Hyperspace Battleships {interaction.user.name}!",
            ephemeral=True,
        )

    @app_commands.command(name="where_am_i", description="Get your location info")
    async def where_am_i(self, interaction: discord.Interaction):
        '''Returns the location of the player'''
        if await check_player_exists(interaction) is False:
            return

        player = data.players[interaction.user]
        player_location = player.ship.location
        location_name = player_location.is_planet()
        await interaction.response.send_message(f"You are currently at {player_location}, also known as {location_name}.", ephemeral=True)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(GeneralCommands(client))
