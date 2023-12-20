import discord
from discord import app_commands
from discord.ext import commands

from typing import Literal

from ui.trade_menu import TradeModal
from player import Player
from utils import get_resource_amount


async def check_registered(interaction: discord.Interaction) -> bool:
    """Check if a player is registered, if not sends an error message. Else run the function."""
    if not Player.exists(interaction.user.id):
        await interaction.response.send_message("You are not registered as a player.", ephemeral=True)
        return False
    return True


class TradeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
            await interaction.response.send_message("You can't give money to yourself.", ephemeral=True)
            return

        if amount_to_pay <= 0:
            await interaction.response.send_message("Please provide a positive amount of money.", ephemeral=True)
            return

        if not Player.exists(recipient_id):
            await interaction.response.send_message("The recipient doesn't have an account.", ephemeral=True)
            return

        sender = Player.get(sender_id)
        recipient = Player.get(recipient_id)

        if sender.money < amount_to_pay:
            await interaction.response.send_message("You don't have enough money.", ephemeral=True)
            return

        sender.money = sender.money - amount_to_pay
        recipient.money = recipient.money + amount_to_pay

        await interaction.response.send_message(f"You gave ${amount_to_pay} to {member_recipient.name}.")

    @app_commands.command(name="give_resources", description="Give resources to another player")
    @app_commands.check(check_registered)
    async def give_resources(
        self,
        interaction: discord.Interaction,
        amount_to_give: int,
        resource: Literal["Copper", "Silver", "Gold"],
        recipient: discord.Member,
    ):
        sender_id = interaction.user.id
        recipient_id = recipient.id

        if sender_id == recipient_id:
            await interaction.response.send_message("You can't give resources to yourself.", ephemeral=True)
            return

        if amount_to_give <= 0:
            await interaction.response.send_message("Please provide a positive amount of resources.", ephemeral=True)
            return

        if not Player.exists(recipient_id):
            await interaction.response.send_message("The recipient doesn't have an account.", ephemeral=True)
            return

        sender = Player.get(sender_id)
        recipient = Player.get(recipient_id)

        if get_resource_amount(sender.ship.modules["Cargo"], resource) < amount_to_give:
            await interaction.response.send_message("You don't have enough resources.", ephemeral=True)
            return

        sender.ship.modules["Cargo"].add_resource(resource, -1 * amount_to_give)
        recipient.ship.modules["Cargo"].add_resource(resource, amount_to_give)
        # TODO implement by UI
        message = f"You gave {amount_to_give} {resource} to {recipient.name}."
        await interaction.response.send_message(message)

    # TODO should implement better texts
    @app_commands.command(name="trade", description="Trade resources with another player")
    @app_commands.check(check_registered)
    async def trade(
        self,
        interaction: discord.Interaction,
        recipient: discord.Member,
        send_or_receive_money: Literal["send", "receive"] = "send",
        amount: int = 0,
    ):
        sender_id = interaction.user.id
        recipient_id = recipient.id
        print("recipient_id:", recipient_id)
        print("Player.exists(recipient_id):", Player.exists(recipient_id))

        if sender_id == recipient_id:
            await interaction.response.send_message("You can't trade with yourself.", ephemeral=True)
            return

        if not Player.exists(recipient_id):
            await interaction.response.send_message("The recipient doesn't have an account.", ephemeral=True)
            return

        sender = Player.get(sender_id)
        recipient_player = Player.get(recipient_id)

        if send_or_receive_money == "receive":
            amount = -amount

        if amount < 0:
            await interaction.response.send_message("Please provide a positive amount of money.", ephemeral=True)
            return

        if send_or_receive_money == "receive":
            amount = -amount

        if amount < 0:
            if recipient_player.money < abs(amount):
                await interaction.response.send_message(
                    "The recipient doesn't have enough money to send.", ephemeral=True
                )
                return
        else:
            if sender.money < abs(amount):
                await interaction.response.send_message("You don't have enough money to send.", ephemeral=True)
                return

        # TODO set required to false with default values of 0
        ask_resources = {
            "title": "Resources You Ask",
            "required": False,
            "questions": ["copper", "silver", "gold"],
        }
        give_resources = {
            "title": "Resources You Offer:",
            "required": False,
            "questions": ["copper", "silver", "gold"],
        }
        inputs = [
            ask_resources,
            give_resources,
        ]
        paginator = TradeModal(inputs, amount, recipient, author_id=interaction.user.id)

        await paginator.send(interaction)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(TradeCog(client))
