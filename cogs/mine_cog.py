from discord import app_commands
import discord
from discord.ext import commands
import math
import random

import data
from player import Player
from utils import check_player_exists

class MineCommands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="mine", description="Mine a random resource")
    async def mine(self, interaction: discord.Interaction):
        if await check_player_exists(interaction) is False:
            return

        player = data.players[interaction.user]
        mining_bonus = player.ship.modules[1].mining_bonus
        resource = random.choices(["Copper", "Silver", "Gold", "Uranium", "Black Matter"])[0]
        amount = math.floor((random.random() * mining_bonus) / 2)
        player.ship.modules[5].add_cargo(resource, amount)
        await interaction.response.send_message(f"You mined {amount} tons of {resource}.", ephemeral=True)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(MineCommands(client))