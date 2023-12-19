from discord.ext.modal_paginator import ModalPaginator, PaginatorModal
import discord
from discord.ext.modal_paginator import CustomButton
import discord_colorize

from typing import Any, Dict, List

from tabulate import tabulate

import data


# TODO add default values for the inputs (0)
class TradeModal(ModalPaginator):
    def __init__(
        self,
        inputs: List[Dict[str, Any]],
        amount,
        recipiant: discord.Member,
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
        self.recipiant = recipiant

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
            await interaction.response.send_message("Invalid input", ephemeral=True)
            return
        else:
            if total_resources == 0:
                await interaction.response.send_message(
                    "You can't send an empty offer, if you want to send money use /pay.", ephemeral=True
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

        self.player = data.players[interaction.user]
        self.recipiant_player = data.players[self.recipiant]

        if await check_enough_resources(self.player, self.recipiant_player, self.modals, interaction) is False:
            return

        await interaction.response.send_message("Offer sent")

        offer_paginator = OfferPaginator(
            self.player, self.recipiant_player, self.modals, self.amount, interaction, self
        )

        resume_table = self.get_offer_table()
        await self.recipiant.send(f"You received a trade offer:\n\n{resume_table}", view=offer_paginator)

    def get_offer_table(self) -> str:
        message = f"Trade between {self.interaction.user.mention} and {self.recipiant.mention}:\n"
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
    def __init__(self, player, recipiant_player, uppermodals, amount, og_interaction, upper_self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = None
        self.player = player
        self.recipiant_player = recipiant_player
        self.uppermodals = uppermodals
        self.amount = amount
        self.og_interaction = og_interaction
        self.upper_self = upper_self

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.accept_offer(interaction)
        self.stop()

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Offer denied", ephemeral=True)
        self.stop()

    async def accept_offer(self, interaction: discord.Interaction) -> None:
        if await check_enough_resources(self.player, self.recipiant_player, self.uppermodals, interaction) is False:
            return
        if await check_enough_money(self.player, self.recipiant_player, self.amount, interaction) is False:
            return
        self.distribute_resources()
        await interaction.response.send_message("Offer accepted", ephemeral=True)
        await self.og_interaction.user.send(
            f"{interaction.user.mention} accepted your offer:\n\n{self.upper_self.get_offer_table()}"
        )

    def distribute_resources(self) -> None:
        for modal in self.uppermodals:
            if modal == self.uppermodals[0]:
                for field in modal.children:
                    self.recipiant_player.ship.modules[5].remove_resource(field.label, int(field.value))
                    self.player.ship.modules[5].add_resource(field.label, int(field.value))
            else:
                for field in modal.children:
                    self.player.ship.modules[5].remove_resource(field.label, int(field.value))
                    self.recipiant_player.ship.modules[5].add_resource(field.label, int(field.value))
        if self.amount < 0:
            self.player.money += abs(self.amount)
            self.recipiant_player.money -= abs(self.amount)
        else:
            self.player.money -= abs(self.amount)
            self.recipiant_player.money += abs(self.amount)


async def check_enough_resources(player, recipiant_player, modals, interaction: discord.Interaction) -> bool:
    for modal in modals:
        if modal == modals[0]:
            if not await check_enough_resources_per_player(recipiant_player, modals, interaction):
                return False
        else:
            if not await check_enough_resources_per_player(player, modals, interaction):
                return False
    return True


async def check_enough_resources_per_player(player, modals, interaction: discord.Interaction) -> bool:
    for modal in modals:
        if modal == modals[0]:
            for field in modal.children:
                if player.ship.modules[5].get_resource_amount(field.label) < int(field.value):
                    await interaction.response.send_message(
                        f"{player.id} doesn't have enough {field.label}", ephemeral=True
                    )
                    return False
    return True


async def check_enough_money(player, recipiant_player, amount, interaction: discord.Interaction) -> bool:
    if amount < 0:
        if recipiant_player.money < abs(amount):
            await interaction.response.send_message("The recipiant doesn't have enough money to send.", ephemeral=True)
            return False
    else:
        if player.money < abs(amount):
            await interaction.response.send_message("The sender doesn't have enough money to send.", ephemeral=True)
            return False
    return True
