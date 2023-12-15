from typing import Any, Dict, List
from discord.ext.modal_paginator import ModalPaginator, PaginatorModal
import discord


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

        for data in inputs:
            title: str = data["title"]
            required: bool = data["required"]
            questions: List[str] = data["questions"]
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
            answers.append(self.amount)

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
