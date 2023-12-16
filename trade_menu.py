from discord.ext.modal_paginator import ModalPaginator, PaginatorModal
import discord

from typing import Any, Dict, List

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
        super().__init__(author_id=author_id, **kwargs)
        self.inputs = inputs
        self.amount = amount
        self.recipiant = recipiant

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

    # TODO can't send empty offers
    async def on_finish(self, interaction: discord.Interaction[Any]) -> None:
        # to use for UI dev
        answers: list[str] = []
        for modal in self.modals:
            resume = ""
            field: discord.ui.TextInput[Any]
            for field in modal.children:
                resume += f"{field.label}: {field.value}\n"

            answers.append(resume)

        try:
            for modal in self.modals:
                if modal == self.modals[0]:
                    for field in modal.children:
                        if int(field.value) < 0:
                            await interaction.response.send_message(
                                "You can't ask for negative resources.", ephemeral=True
                            )
                            return
                else:
                    for field in modal.children:
                        if int(field.value) < 0:
                            await interaction.response.send_message(
                                "You can't offer negative resources.", ephemeral=True
                            )
                            return
        except ValueError:
            await interaction.followup.send("Invalid input", ephemeral=True)
            return

        self.player = data.players[interaction.user]
        self.recipiant_player = data.players[self.recipiant]

        if await check_enough_resources(self.player, self.recipiant_player, self.modals, self.amount) is False:
            return

        # TODO print "ASK/OFFER", "RESOURCE_TYPE", "AMOUNT" (don't forget money) by UI dev
        resume_table = "Offer sent"
        await interaction.response.send_message(resume_table)

        offer_paginator = OfferPaginator(self.player, self.recipiant_player, self.modals, self.amount)

        # TODO UI dev add a little resume of the transaction and who proposed you the offers (same as aboveg ig)
        await self.recipiant.send("You received a trade offer", view=offer_paginator)


class OfferPaginator(discord.ui.View):
    def __init__(self, player, recipiant_player, uppermodals, amount, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = None
        self.player = player
        self.recipiant_player = recipiant_player
        self.uppermodals = uppermodals
        self.amount = amount

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        # TODO for UI dev
        await self.accept_offer(interaction)
        self.stop()

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        # TODO for UI dev
        await interaction.response.send_message("Offer denied", ephemeral=True)
        self.stop()

    async def accept_offer(self, interaction: discord.Interaction) -> None:
        if await check_enough_resources(self.player, self.recipiant_player, self.uppermodals, interaction) is False:
            return
        if await check_enough_money(self.player, self.recipiant_player, self.amount, interaction) is False:
            return
        self.distribute_resources()
        # TODO UI dev?
        await interaction.response.send_message("Offer accepted", ephemeral=True)

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
            for field in modal.children:
                if recipiant_player.ship.modules[5].get_resource_amount(field.label) < int(field.value):
                    await interaction.followup.send(
                        "The recipiant doesn't have enough resources to send.", ephemeral=True
                    )
                    return False
        else:
            for field in modal.children:
                if player.ship.modules[5].get_resource_amount(field.label) < int(field.value):
                    await interaction.followup.send("You don't have enough resources to send.", ephemeral=True)
                    return False
    return True


async def check_enough_money(player, recipiant_player, amount, interaction: discord.Interaction) -> bool:
    if amount < 0:
        if recipiant_player.money < abs(amount):
            await interaction.followup.send("The recipiant doesn't have enough money to send.", ephemeral=True)
            return False
    else:
        if player.money < abs(amount):
            await interaction.followup.send("The sender doesn't have enough money to send.", ephemeral=True)
            return False
    return True
