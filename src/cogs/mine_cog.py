from discord import app_commands
import discord
from discord.ext import commands

import math
import random

from data import RESOURCE_NAMES
from player import Player
from utils import check_registered


class MineCommands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    # Chances of getting a resource:
    # Copper: 35% | Silver: 30% |Gold: 25% | Uranium: 7% | Black Matter: 3%
    # TODO mine X times (avoid spamming /mine)
    @app_commands.command(name="mine", description="Mine a random resource")
    @app_commands.check(check_registered)
    async def mine(self, interaction: discord.Interaction, mining_sessions: int = 1):
        player = Player.get(interaction.user.id)
        
        if player.ship.energy < 10 * mining_sessions:
            await interaction.response.send_message(
                "You don't have enough energy.", ephemeral=True
            )
            return
        
        await interaction.response.send_message(
                f"You started mining.", ephemeral=True
            )
        for _ in range(mining_sessions):
            # TODO mining module changes energy efficiency
            player.ship.energy -= 10
            mining_bonus = player.ship.modules["MiningModule"].mining_bonus
            resource_name = random.choices(RESOURCE_NAMES, weights=[45, 30, 20, 3, 2, 1])[0]
            amount = math.floor((random.random() * mining_bonus) / 2)
            player.ship.modules["Cargo"].add_resource(resource_name, amount)
            await interaction.followup.send(
                f"You mined {amount} tons of {resource_name}.", ephemeral=True
            )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(MineCommands(client))
