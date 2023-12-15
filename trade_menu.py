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

        for data_input in inputs:
            title: str = data_input["title"]
            required: bool = data_input["required"]
            questions: List[str] = data_input["questions"]
            modal = PaginatorModal(title=title, required=required)
            for question in questions:
                modal.add_input(
                    label=question,
                )

            self.add_modal(modal)

    async def on_finish(self, interaction: discord.Interaction[Any]) -> None:
        answers: list[str] = []
        for modal in self.modals:
            resume = ""
            field: discord.ui.TextInput[Any]
            for field in modal.children:
                resume += f"{field.label}: {field.value}\n"

            answers.append(resume)

        try:
            player = data.players[interaction.user]
            recipiant_player = data.players[self.recipiant]
            for player in [player, recipiant_player]:
                for modal in self.modals:
                    for field in modal.children:
                        if player.ship.modules[5].get_resource_amount(field.label) < int(field.value):
                            await interaction.response.send_message(
                                f"{player.id} has not enough {field.label}", ephemeral=True
                            )
                            return
        except ValueError:
            await interaction.response.send_message("Invalid input", ephemeral=True)
            return

        # TODO print "ASK/OFFER", "RESOURCE_TYPE", "AMOUNT" (don't forget money) by UI dev
        resume_table = "Offer sent"
        await interaction.response.send_message(resume_table)

        offer_paginator = OfferPaginator()

        # TODO UI dev add a little resume of the transaction and who proposed you the offers (same as aboveg ig)
        await self.recipiant.send("You received a trade offer", view=offer_paginator)


class OfferPaginator(discord.ui.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = None

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        # TODO for UI dev
        await interaction.response.send_message("Offer accepted", ephemeral=True)
        await self.accept_offer(interaction)
        self.stop()

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        # TODO for UI dev
        await interaction.response.send_message("Offer denied", ephemeral=True)
        self.stop()

    async def accept_offer(self, interaction: discord.Interaction) -> None:
        await interaction.followup.send("Distributing resources", ephemeral=True)
