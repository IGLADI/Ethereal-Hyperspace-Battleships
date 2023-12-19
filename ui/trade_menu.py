from discord.ext.modal_paginator import ModalPaginator, PaginatorModal
import discord

from typing import Any, Dict, List

import data
from player import Player


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
        super().__init__(author_id=author_id, **kwargs)
        self.inputs = inputs
        self.amount = amount
        self.recipient = recipient

        for data_input in self.inputs:
            title: str = data_input["title"]
            # TODO set default value to 0
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

    async def on_finish(self, interaction: discord.Interaction[Any]) -> None:
        # to use for UI dev
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
                if modal == self.modals[0]:
                    for field in modal.children:
                        total_resources += int(field.value)
                        if int(field.value) < 0:
                            await interaction.response.send_message(
                                "You can't ask for negative resources.", ephemeral=True
                            )
                            return
                else:
                    for field in modal.children:
                        total_resources += int(field.value)
                        if int(field.value) < 0:
                            await interaction.response.send_message(
                                "You can't offer negative resources.", ephemeral=True
                            )
                            return
        except ValueError:
            await interaction.response.send_message("Invalid input", ephemeral=True)
            return
        else:
            if total_resources == 0:
                await interaction.response.send_message(
                    "You can't send an empty offer, if you want to send money use /pay.",
                    ephemeral=True,
                )
                return

        player = Player.get(self.author_id)
        recipient_player = Player.get(self.recipient.id)

        if (
            await check_enough_resources(
                player, recipient_player, self.modals, interaction
            )
            is False
        ):
            return

        # TODO print "ASK/OFFER", "RESOURCE_TYPE", "AMOUNT" (don't forget money) by UI dev
        resume_table = "Offer sent"
        await interaction.response.send_message(resume_table)

        offer_paginator = OfferPaginator(
            player, self.recipient, self.modals, self.amount
        )

        # TODO UI dev add a little resume of the transaction and who proposed you the offers (same as aboveg ig)
        await self.recipient.send("You received a trade offer", view=offer_paginator)


class OfferPaginator(discord.ui.View):
    def __init__(self, player, recipient_player, uppermodals, amount, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = None
        self.player = player
        self.recipient_player = recipient_player
        self.uppermodals = uppermodals
        self.amount = amount

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        # TODO for UI dev
        await self.accept_offer(interaction)
        self.stop()

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        # TODO for UI dev
        await interaction.response.send_message("Offer denied", ephemeral=True)
        self.stop()

    async def accept_offer(self, interaction: discord.Interaction) -> None:
        if (
            await check_enough_resources(
                self.player, self.recipient_player, self.uppermodals, interaction
            )
            is False
        ):
            return
        if (
            await check_enough_money(
                self.player, self.recipient_player, self.amount, interaction
            )
            is False
        ):
            return
        self.distribute_resources()
        # TODO UI dev?
        await interaction.response.send_message("Offer accepted", ephemeral=True)

    def distribute_resources(self) -> None:
        recipient_player = Player.get(self.recipient.id)
        player_cargo = self.player.ship.modules["Cargo"]
        recipient_cargo = recipient_player.ship.modules["Cargo"]

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
            recipient_player.money -= abs(self.amount)
        else:
            self.player.money -= abs(self.amount)
            recipient_player.money += abs(self.amount)


def get_resource_amount(cargo, resource_name: str) -> int:
    resource = cargo.resources.get(resource_name)
    return resource.amount if resource else 0


async def check_enough_resources(
    player: Player, recipient_player: Player, modals, interaction: discord.Interaction
) -> bool:
    player_cargo = player.ship.modules["Cargo"]
    recipient_cargo = recipient_player.ship.modules["Cargo"]
    for modal in modals:
        if modal == modals[0]:
            for field in modal.children:
                if get_resource_amount(recipient_cargo, field.label) < int(field.value):
                    await interaction.response.send_message(
                        "The recipient doesn't have enough resources to send.",
                        ephemeral=True,
                    )
                    return False
        else:
            for field in modal.children:
                if get_resource_amount(player_cargo, field.label) < int(field.value):
                    await interaction.response.send_message(
                        "You don't have enough resources to send.", ephemeral=True
                    )
                    return False
    return True


async def check_enough_money(
    player, recipient_player, amount, interaction: discord.Interaction
) -> bool:
    if amount < 0:
        if recipient_player.money < abs(amount):
            await interaction.response.send_message(
                "The recipient doesn't have enough money to send.", ephemeral=True
            )
            return False
    else:
        if player.money < abs(amount):
            await interaction.response.send_message(
                "The sender doesn't have enough money to send.", ephemeral=True
            )
            return False
    return True
