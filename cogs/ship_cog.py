from discord import app_commands
import discord
from discord.ext import commands
from typing import Literal

import data
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
        ship_message += f"**Modules:**\n"
        modules_info = [str(module) for module in ship.modules]
        ship_message += f"{'\n'.join(modules_info)}\n"
        await interaction.response.send_message(ship_message, ephemeral=True)

    # TODO: add a check to see if the player has enough resources
    @app_commands.command(name="upgrade_ship", description="Upgrade a module")
    async def upgrade_ship(self, interaction: discord.Interaction, module_name: Literal["Travel Module", "Mining Module", "Canon", "Shield", "Fuel", "Cargo", "Radar", "Energy Generator"]):
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
                await interaction.response.send_message(f"Upgraded {module_name} to level {module.level}.", ephemeral=True)
                return
        await interaction.response.send_message(f"Couldn't find module {module_name}.", ephemeral=True)
        return
    
    #! For debugging purposes
    @app_commands.command(name="add_cargo", description="For debugging purposes")
    async def add_cargo(self, interaction: discord.Interaction, resource: Literal["Copper", "Silver", "Gold"], amount: int):
        if await check_player_exists(interaction) is False:
            return

        player = data.players[interaction.user]
        new_amount = player.ship.modules[5].add_cargo(resource, amount)
        if new_amount == 0:
            await interaction.response.send_message(f"{resource} capacity is full, could not add to your ship.", ephemeral=True)
        elif new_amount < amount:
            await interaction.response.send_message(f"You added {new_amount} tons of {resource} and left {amount - new_amount} tons behind, because you reached maximum capacity.", ephemeral=True)
        else:
            await interaction.response.send_message(f"You added {amount} tons of {resource} to your ship.", ephemeral=True)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(ShipCommands(client))