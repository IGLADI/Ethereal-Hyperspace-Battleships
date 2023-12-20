from discord.ext.modal_paginator import ModalPaginator, PaginatorModal
import discord
from discord.ext.modal_paginator import CustomButton
import discord_colorize

from typing import Any, Dict, List
from tabulate import tabulate

from player import Player
from ui.simple_banner import ErrorBanner, NormalBanner, SuccessBanner
from utils import get_resource_amount


# TODO add default values for the inputs (0)
class TradeModal(ModalPaginator):
    def __init__(
        self,
        inputs: List[Dict[str, Any]],
        amount,
        recipient: discord.Member,
        *,
        author_id: int,
        **kwargs: Any,
    ) -> None:
        # TODO can reopen MODAL once completed
        buttons = {
            "FINISH": CustomButton(label="Send Offer"),
        }
        super().__init__(buttons=buttons, author_id=author_id, **kwargs)
        self.inputs = inputs
        self.amount = amount
        self.recipient = recipient

        for data_input in self.inputs:
            title: str = data_input["title"]
            required: bool = data_input["required"]
            questions: List[str] = data_input["questions"]
            modal = PaginatorModal(title=title, required=required)
            for question in questions:
                modal.add_input(
                    label=question,
                    placeholder="0",
                    default="0",
                    required=False,
                )

            self.add_modal(modal)

    @property
    def page_string(self) -> str:
        offer_table = self.get_offer_table()
        page_counter = f"\n{self.current_page + 1}/{len(self.modals)}"
        current_modal = f"\nEdditing {self.current_modal.title}\n"
        return f"{offer_table}{page_counter}{current_modal}"

    async def on_finish(self, interaction: discord.Interaction[Any]) -> None:
        answers: list[str] = []
        for modal in self.modals:
            resume = ""
            field: discord.ui.TextInput[Any]
            for field in modal.children:
                resume += f"{field.label}: {field.value}\n"

            answers.append(resume)

        total_resources = 0
        try:
            for modal in self.modals:
                for field in modal.children:
                    value = int(field.value)
                    if value < 0:
                        error_message = (
                            "You can't ask for negative resources."
                            if modal == self.modals[0]
                            else "You can't offer negative resources."
                        )
                        await interaction.response.send_message(error_message, ephemeral=True)
                        return
                    total_resources += value

        except ValueError:
            banner = ErrorBanner(text="Invalid input", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return
        else:
            if total_resources == 0:
                await interaction.response.send_message(
                    "You can't send an empty offer, if you want to send money use /pay.",
                    ephemeral=True,
                )
                return

        modal = self.modals[0]
        modal2 = self.modals[1]
        for field in modal.children:
            for field2 in modal2.children:
                if field.label == field2.label and field.value != "0" and field2.value != "0":
                    await interaction.response.send_message(
                        "You can't ask and offer the same resource.", ephemeral=True
                    )
                    return

        self.player = Player.get(self.author_id)
        self.recipient_player = Player.get(self.recipient.id)

        if await check_enough_resources(self.player, self.recipient_player, self.modals, interaction) is False:
            return

        banner = SuccessBanner(text="Offer sent", user=interaction.user)
        await interaction.response.send_message(embed=banner.embed, ephemeral=True)

        offer_paginator = OfferPaginator(
            self.player, self.recipient_player, self.modals, self.amount, self
        )

        resume_table = self.get_offer_table()
        banner = NormalBanner(text=f"You received a trade offer:\n\n{resume_table}", user=self.recipient)
        await self.recipient.send(embed=banner.embed, view=offer_paginator)

    def get_offer_table(self) -> str:
        message = f"Trade between {self.interaction.user.mention} and {self.recipient.mention}\n"
        headers = ["RESOURCE", "ASK", "OFFER"]
        values = []
        try:
            for modal in self.modals:
                if modal == self.modals[0]:
                    for field in modal.children:
                        if field.value != "0":
                            values.append([field.label, int(field.value), ""])
                else:
                    for field in modal.children:
                        if field.value != "0":
                            values.append([field.label, "", int(field.value)])
            message += f"```{tabulate(values, headers=headers)}```"
            if self.amount < 0:
                message += f"Money offered: ${abs(self.amount)}.\n"
            elif self.amount > 0:
                message += f"Money asked: ${abs(self.amount)}.\n"
        except ValueError:
            invalid_input = discord_colorize.Colors().colorize("Invalid input", fg="red")
            message += f"```ansi\n{invalid_input}\n```"
        # self.current_modal.title
        return message


class OfferPaginator(discord.ui.View):
    def __init__(self, player, recipiant_player, uppermodals, amount, upper_self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = None
        self.player = player
        self.recipient_player = recipiant_player
        self.uppermodals = uppermodals
        self.amount = amount
        self.upper_self = upper_self

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.accept_offer(interaction)
        self.stop()

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        banner = ErrorBanner(text="Offer denied", user= interaction.user)
        await interaction.response.send_message(embed=banner.embed, ephemeral=True)
        self.stop()

    async def accept_offer(self, interaction: discord.Interaction) -> None:
        if await check_enough_resources(self.player, self.recipient_player, self.uppermodals, interaction) is False:
            return
        if await check_enough_money(self.player, self.recipient_player, self.amount, interaction) is False:
            return
        self.distribute_resources()
        banner = SuccessBanner(text="Offer accepted", user=interaction.user)
        await interaction.response.send_message(embed=banner.embed, ephemeral=True)
        banner = SuccessBanner(text="Offer accepted", user=interaction.user)
        await self.recipient_player.user.send(embed=banner.embed)

    def distribute_resources(self) -> None:
        player_cargo = self.player.ship.modules["Cargo"]
        recipient_cargo = self.recipient_player.ship.modules["Cargo"]

        for modal in self.uppermodals:
            if modal == self.uppermodals[0]:
                for field in modal.children:
                    recipient_cargo.add_resource(field.label, -1 * int(field.value))
                    player_cargo.add_resource(field.label, int(field.value))
            else:
                for field in modal.children:
                    player_cargo.add_resource(field.label, -1 * int(field.value))
                    recipient_cargo.add_resource(field.label, int(field.value))

        if self.amount < 0:
            self.player.money += abs(self.amount)
            self.recipient_player.money -= abs(self.amount)
        else:
            self.player.money -= abs(self.amount)
            self.recipient_player.money += abs(self.amount)


async def check_enough_resources(
    player: Player, recipient_player: Player, modals, interaction: discord.Interaction
) -> bool:
    for modal in modals:
        if modal == modals[0]:
            if not await check_enough_resources_per_player(recipient_player, modals, interaction):
                return False
        else:
            if not await check_enough_resources_per_player(player, modals, interaction):
                return False
    return True


async def check_enough_resources_per_player(player, modals, interaction: discord.Interaction) -> bool:
    for modal in modals:
        if modal == modals[0]:
            for field in modal.children:
                player_cargo = player.ship.modules["Cargo"]
                if get_resource_amount(player_cargo, field.label) < int(field.value):
                    banner = ErrorBanner(text=f"{player.id} doesn't have enough {field.label}", user=interaction.user)
                    await interaction.response.send_message(embed=banner.embed, ephemeral=True)
                    return False
    return True


async def check_enough_money(player, recipient_player, amount, interaction: discord.Interaction) -> bool:
    if amount < 0:
        if recipient_player.money < abs(amount):
            banner = ErrorBanner(text="The recipient doesn't have enough money to send.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return False
    else:
        if player.money < abs(amount):
            banner = ErrorBanner(text="You don't have enough money to send.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return False
    return True
