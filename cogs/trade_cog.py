import discord
from discord import app_commands
from discord.ext import commands

from typing import Literal

import data
from trade_menu import TradeModal
from utils import check_player_exists


class TradeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        if sender == recipient:
            await interaction.response.send_message("You can't give money to yourself.", ephemeral=True)
            return
        if sender.money < amount_to_pay:
            await interaction.response.send_message("You don't have enough money.", ephemeral=True)
            return

        sender.money -= amount_to_pay
        recipient.money += amount_to_pay
        await interaction.response.send_message(f"You gave ${amount_to_pay} to {member_recipient.name}.")

    @app_commands.command(name="give_resources", description="Give resources to another player")
    async def give_resources(
        self,
        interaction: discord.Interaction,
        amount_to_give: int,
        resource: Literal["Copper", "Silver", "Gold", "Uranium", "Black Matter"],
        recipient: discord.Member,
    ):
        if await check_player_exists(interaction) is False:
            return
        if amount_to_give <= 0:
            await interaction.response.send_message("Please provide a positive amount of resources.", ephemeral=True)
            return
        if recipient not in data.players:
            await interaction.response.send_message("The recipient doesn't have an account.", ephemeral=True)
            return
        sender = data.players[interaction.user]
        recipient = data.players[recipient]
        if sender == recipient:
            await interaction.response.send_message("You can't give resources to yourself.", ephemeral=True)
            return
        if sender.ship.modules[5].get_resource_amount(resource) < amount_to_give:
            await interaction.response.send_message("You don't have enough resources.", ephemeral=True)
            return

        sender.ship.modules[5].remove_resource(resource, amount_to_give)
        recipient.ship.modules[5].add_resource(resource, amount_to_give)
        # TODO implement by UI
        message = f"You gave {amount_to_give} {resource} to {recipient.id}."
        await interaction.response.send_message(message)

    # TODO should implement better texts
    @app_commands.command(name="trade", description="Trade resources with another player")
    async def trade(
        self,
        interaction: discord.Interaction,
        recipient: discord.Member,
        send_or_receive_money: Literal["send", "receive"] = "send",
        amount: int = 0,
    ):
        if await check_player_exists(interaction) is False:
            return
        if recipient not in data.players:
            await interaction.response.send_message("The recipient doesn't have an account.", ephemeral=True)
            return

        sender = data.players[interaction.user]
        recipiant_player = data.players[recipient]
        if sender == recipiant_player:
            await interaction.response.send_message("You can't trade with yourself.", ephemeral=True)
            return

        if amount < 0:
            await interaction.response.send_message("Please provide a positive amount of money.", ephemeral=True)
            return

        if send_or_receive_money == "receive":
            amount = -amount

        if amount < 0:
            if data.players[recipiant_player.id].money < abs(amount):
                await interaction.response.send_message(
                    "The recipiant doesn't have enough money to send.", ephemeral=True
                )
                return
        else:
            if data.players[interaction.user].money < abs(amount):
                await interaction.response.send_message("You don't have enough money to send.", ephemeral=True)
                return

        resources = ["Copper", "Silver", "Gold", "Uranium", "Black Matter"]
        # TODO set required to false with default values of 0
        ask_resources = {
            "title": "Resources You Ask",
            "required": True,
            "questions": resources,
        }
        give_resources = {
            "title": "Resources You Offer:",
            "required": True,
            "questions": resources,
        }
        inputs = [
            ask_resources,
            give_resources,
        ]
        paginator = TradeModal(inputs, amount, recipient, author_id=interaction.user.id)

        # ! TODO fix this, should use paginator.start() instead
        await interaction.response.send_message(
            view=paginator, ephemeral=True, content=(paginator.modals[0].title + f"\n\n1/{len(paginator.modals)}")
        )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(TradeCog(client))
