from discord import app_commands
import discord
from discord.ext import commands

import data
from player import Player
from utils import check_player_exists

class ShipCommands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="ship", description="Get info on your ship")
    async def ship(self, interaction: discord.Interaction):
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
    @app_commands.command(name="upgrade", description="upgrade a module")
    async def upgrade(self, interaction: discord.Interaction, module_name: str):
        if await check_player_exists(interaction) is False:
            return

        player = data.players[interaction.user]
        ship = player.ship
        for module in ship.modules:
            if module_name == module.name:
                try:
                    module.upgrade()
                except Exception as e:
                        await interaction.response.send_message(f"Couldn't upgrade {module_name}: {e}", ephemeral=True)
                        return
                await interaction.response.send_message(f"Upgraded {module_name} to level {module.level}.", ephemeral=True)
                return
        await interaction.response.send_message(f"Couldn't find module {module_name}.", ephemeral=True)
        return

async def setup(client: commands.Bot) -> None:
    await client.add_cog(ShipCommands(client))