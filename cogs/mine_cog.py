from discord import app_commands
import discord
from discord.ext import commands
import math
import random

import data
from utils import check_player_exists


class MineCommands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    # Chances of getting a resource:
    # Copper: 35% | Silver: 30% |Gold: 25% | Uranium: 7% | Black Matter: 3%
    @app_commands.command(name="mine", description="Mine a random resource")
    async def mine(self, interaction: discord.Interaction, amount: int = 1):
        if await check_player_exists(interaction) is False:
            return
        if data.players[interaction.user].ship.is_traveling:
            await interaction.response.send_message("You can't mine while traveling!", ephemeral=True)
            return
        
        player = data.players[interaction.user]
        mining_bonus = player.ship.modules[1].mining_bonus
        for i in range(amount):
            resource = random.choices(["Copper", "Silver", "Gold", "Uranium", "Black Matter"], weights=[35, 30, 25, 7, 3])[
                0
            ]
            amount = math.floor((random.random() * mining_bonus) / 2)
            player.ship.modules[5].add_cargo(resource, amount)
            if i == 0:
                await interaction.response.send_message(f"You mined {amount} tons of {resource}.", ephemeral=True)
            else:
                await interaction.followup.send(f"You mined {amount} tons of {resource}.", ephemeral=True)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(MineCommands(client))
