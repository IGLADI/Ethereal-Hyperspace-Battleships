import discord
from discord import app_commands
from discord.ext import commands

from typing import Literal

from ui.trade_menu import TradeModal
from ui.simple_banner import ErrorBanner, SuccessBanner
from player import Player
from utils import get_resource_amount


async def check_registered(interaction: discord.Interaction) -> bool:
    """Check if a player is registered, if not sends an error message. Else run the function."""
    if not Player.exists(interaction.user.id):
        banner = ErrorBanner(text="You are not registered as a player.", user=interaction.user)
        await interaction.response.send_message(embed=banner.embed, ephemeral=True)
        return False
    return True


class TradeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ? TODO maybe add a min lvl to give money (avoid spamming discord acounts)/start with 0 money
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
            banner = ErrorBanner(text="You can't give money to yourself.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        if amount_to_pay <= 0:
            banner = ErrorBanner(text="Please provide a positive amount of money.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        if not Player.exists(recipient_id):
            banner = ErrorBanner(text="The recipient doesn't have an account.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        sender = Player.get(sender_id)
        recipient = Player.get(recipient_id)

        if sender.money < amount_to_pay:
            banner = ErrorBanner(text="You don't have enough money.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        sender.money = sender.money - amount_to_pay
        recipient.money = recipient.money + amount_to_pay

        banner = SuccessBanner(text=f"You gave ${amount_to_pay} to {member_recipient.name}.", user=interaction.user)
        await interaction.response.send_message(embed=banner.embed)

        message = f"{interaction.user.mention} gave you ${amount_to_pay}."
        banner = SuccessBanner(text=message, user=interaction.user)
        await member_recipient.send(embed=banner.embed)

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
        recipient_discord_account = recipient
        recipient_id = recipient.id

        if sender_id == recipient_id:
            banner = ErrorBanner(text="You can't give resources to yourself.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        if amount_to_give <= 0:
            banner = ErrorBanner(text="Please provide a positive amount of resources.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        if not Player.exists(recipient_id):
            banner = ErrorBanner(text="The recipient doesn't have an account.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        sender = Player.get(sender_id)
        recipient = Player.get(recipient_id)
        
        if sender == recipient:
            banner = ErrorBanner(text="You can't give resources to yourself.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        if get_resource_amount(sender.ship.modules["Cargo"], resource) < amount_to_give:
            banner = ErrorBanner(text="You don't have enough resources.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        sender.ship.modules["Cargo"].add_resource(resource, -1 * amount_to_give)
        recipient.ship.modules["Cargo"].add_resource(resource, amount_to_give)

        message = f"You gave {amount_to_give} {resource} to {recipient.name}."
        banner = SuccessBanner(text=message, user=interaction.user)
        await interaction.response.send_message(embed=banner.embed)
        
        message = f"{interaction.user.mention} gave you {amount_to_give} {resource}."
        banner = SuccessBanner(text=message, user=interaction.user)
        await recipient_discord_account.send(embed=banner.embed)

    # TODO should implement better texts
    @app_commands.command(name="trade", description="Trade resources with another player")
    @app_commands.check(check_registered)
    async def trade(
        self,
        interaction: discord.Interaction,
        recipient: discord.Member,
        transaction_action: Literal["send", "receive"] = "send",
        amount: int = 0,
    ):
        sender_id = interaction.user.id
        recipient_id = recipient.id


        if not Player.exists(recipient_id):
            banner = ErrorBanner(text="The recipient doesn't have an account.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        sender = Player.get(sender_id)
        recipient_player = Player.get(recipient_id)
        
        if sender == recipient_player:
            banner = ErrorBanner(text="You can't trade with yourself.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        if amount < 0:
            banner = ErrorBanner(text="Please provide a positive amount of money.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        if transaction_action == "send":
            amount = -amount

        if amount < 0:
            if recipient_player.money < abs(amount):
                banner = ErrorBanner(text="The recipiant doesn't have enough money to send.", user=interaction.user)
                await interaction.response.send_message(embed=banner.embed, ephemeral=True)
                return
        else:
            if sender.money < abs(amount):
                banner = ErrorBanner(text="You don't have enough money to send.", user=interaction.user)
                await interaction.response.send_message(embed=banner.embed, ephemeral=True)
                return

        # TODO set required to false with default values of 0
        ask_resources = {
            "title": "Resources You Ask:",
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


async def check_recipiant_has_an_account(recipient: discord.Member, interaction: discord.Interaction) -> bool:
    if recipient not in Player.players:
        banner = ErrorBanner(text="The recipient doesn't have an account.", user=interaction.user)
        await interaction.response.send_message(embed=banner.embed, ephemeral=True)
        return False
    else:
        return True
