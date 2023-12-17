from discord import app_commands
import discord
from discord.ext import commands
import math
import random

import data
from ui.simple_banner import ErrorBanner
from utils import check_player_exists


class MineCommands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    # Chances of getting a resource:
    # Copper: 35% | Silver: 30% |Gold: 25% | Uranium: 7% | Black Matter: 3%
    # TODO mine X times (avoid spamming /mine)
    @app_commands.command(name="mine", description="Mine a random resource")
    async def mine(self, interaction: discord.Interaction):
        if await check_player_exists(interaction) is False:
            return
        player = data.players[interaction.user]
        if player.ship.energy < 10:
            banner = ErrorBanner(text="You don't have enough energy.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        # TODO mining module changes energy efficiency
        player.ship.remove_energy(10)
        mining_bonus = player.ship.modules[1].mining_bonus
        resource = random.choices(["Copper", "Silver", "Gold", "Uranium", "Black Matter"], weights=[35, 30, 25, 7, 3])[
            0
        ]
        amount = math.floor((random.random() * mining_bonus) / 2)
        player.ship.modules[5].add_cargo(resource, amount)
        await interaction.response.send_message(f"You mined {amount} tons of {resource}.", ephemeral=True)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(MineCommands(client))
