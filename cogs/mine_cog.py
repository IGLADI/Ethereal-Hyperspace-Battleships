from discord import app_commands
import discord
from discord.ext import commands

import math
import random

from data import RESOURCE_NAMES
from player import Player


async def check_registered(interaction: discord.Interaction) -> bool:
    """Check if a player is registered, if not sends an error message. Else run the function."""
    if not Player.exists(interaction.user.id):
        await interaction.response.send_message(
            "You are not registered as a player.", ephemeral=True
        )
        return False
    return True


class MineCommands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    # Chances of getting a resource:
    # Copper: 35% | Silver: 30% |Gold: 25% | Uranium: 7% | Black Matter: 3%
    # TODO mine X times (avoid spamming /mine)
    @app_commands.command(name="mine", description="Mine a random resource")
    @app_commands.check(check_registered)
    async def mine(self, interaction: discord.Interaction):
        player = Player.get(interaction.user.id)
        if player.ship.energy < 10:
            await interaction.response.send_message(
                "You don't have enough energy.", ephemeral=True
            )
            return

        # TODO mining module changes energy efficiency
        player.ship.energy -= 10
        mining_bonus = player.ship.modules["MiningModule"].mining_bonus
        resource_name = random.choices(RESOURCE_NAMES, weights=[45, 30, 20, 3, 2, 1])[0]
        amount = math.floor((random.random() * mining_bonus) / 2)
        player.ship.modules["Cargo"].add_resource(resource_name, amount)
        await interaction.response.send_message(
            f"You mined {amount} tons of {resource_name}.", ephemeral=True
        )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(MineCommands(client))
