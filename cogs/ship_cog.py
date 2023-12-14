from discord import app_commands
import discord
from discord.ext import commands
from typing import Literal

import data
import asyncio
from utils import check_player_exists


class ShipCommands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="ship_info", description="Get info on your ship")
    async def ship_info(self, interaction: discord.Interaction):
        if await check_player_exists(interaction) is False:
            return

        player = data.players[interaction.user]
        ship = player.ship
        ship_message = f"**{player.id}'s ship**\n"
        ship_message += f"**Location:** {ship.location}\n"
        ship_message += "**Modules:**\n"
        modules_info = [str(module) for module in ship.modules]
        ship_message += f"{' '.join(modules_info)}\n"
        await interaction.response.send_message(ship_message, ephemeral=True)

    @app_commands.command(name="upgrade_ship", description="Upgrade a module")
    async def upgrade_ship(
        self,
        interaction: discord.Interaction,
        module_name: Literal[
            "Travel Module", "Mining Module", "Canon", "Shield", "Fuel", "Cargo", "Radar", "Energy Generator"
        ],
    ):
        if await check_player_exists(interaction) is False:
            return

        player = data.players[interaction.user]
        ship = player.ship
        for module in ship.modules:
            if module_name == module.name:
                try:
                    module.upgrade(player.ship.modules[5])
                except Exception as e:
                    await interaction.response.send_message(f"Couldn't upgrade {module_name}: {e}", ephemeral=True)
                    return
                await interaction.response.send_message(
                    f"Upgraded {module_name} to level {module.level}.", ephemeral=True
                )
                return
        await interaction.response.send_message(f"Couldn't find module {module_name}.", ephemeral=True)

    @app_commands.command(name="travel", description="Travel to a new location")
    async def travel(self, interaction: discord.Interaction, x_coordinate: int, y_coordinate: int):
        if await check_player_exists(interaction) is False:
            return

        player = data.players[interaction.user]
        ship = player.ship
        try:
            sleep = ship.travel(x_coordinate, y_coordinate)
            await interaction.response.send_message(f"{player.id} traveling to ({x_coordinate}, {y_coordinate}). Estimated duration = {sleep}.")
        except Exception as e:
            await interaction.response.send_message(f"Couldn't travel: {e}", ephemeral=True)
            return
        else:
            await asyncio.sleep(sleep)
            await interaction.followup.send(f"{player.id} arrived at ({x_coordinate}, {y_coordinate}).")
        

async def setup(client: commands.Bot) -> None:
    await client.add_cog(ShipCommands(client))
