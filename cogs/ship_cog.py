import asyncio
from discord import app_commands
import discord
from discord.ext import commands
from typing import Literal

import asyncio
from utils import check_player_exists
from player import Player


class ShipCommands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="ship_info", description="Get info on your ship")
    async def ship_info(self, interaction: discord.Interaction):
        if await check_player_exists(interaction) is False:
            return

        player = Player.get(interaction.user.id)
        ship = player.ship
        ship_message = f"**{player.id}'s ship**\n"
        ship_message += f"**Location:** {ship.location}\n"
        ship_message += "**Modules:**\n"
        modules_info = [str(module) for module in ship.modules]
        ship_message += f"{' '.join(modules_info)}"
        ship_message += f"\nEnergy: {ship.energy}"
        await interaction.response.send_message(ship_message, ephemeral=True)

    @app_commands.command(name="inventory", description="Get info on your cargo and it's contents")
    async def cargo_info(self, interaction: discord.Interaction):
        if await check_player_exists(interaction) is False:
            return

        player = Player.get(interaction.user.id)
        ship = player.ship
        ship_message = f"**{player.id}'s ship**\n"
        ship_message += "**Cargo:**\n"
        cargo_info = [str(resource) for resource in ship.modules[5]._capacity]
        ship_message += f"{' '.join(cargo_info)}"
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

        player = Player.get(interaction.user.id)
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
          
        player = Player.get(interaction.user.id)
        ship = player.ship
        if ship.is_traveling:
            await interaction.response.send_message("Wait untill you arrive before you start a new journey!", ephemeral=True)
            return
        
        try:
            sleep = ship.travel(x_coordinate, y_coordinate)
            await interaction.response.send_message(f"{player.id} traveling to ({x_coordinate}, {y_coordinate}). Estimated duration = {sleep}.")
        except Exception as e:
            await interaction.response.send_message(f"Couldn't travel: {e}", ephemeral=True)
            return
        else:
            await asyncio.sleep(sleep)
            await interaction.followup.send(f"{player.id} arrived at ({x_coordinate}, {y_coordinate}).")

    # TODO: implement ship.scan()
    @app_commands.command(name="scan", description="Use your radar to scan the area")
    async def scan(self, interaction: discord.Interaction):
        if await check_player_exists(interaction) is False:
            return

        player = Player.get(interaction.user.id)
        ship = player.ship

        found = ship.scan()
        await interaction.response.send_message(f"Scanned the area. Found {found} .", ephemeral=True)

    @app_commands.command(name="toggle_energy_generator", description="Toggle on of the energy generator")
    async def toggle_energy_generator(self, interaction: discord.Interaction, on: bool):
        if await check_player_exists(interaction) is False:
            return

        player = Player.get(interaction.user.id)
        generator_status = player.ship.modules[7].is_on
        if player.ship.modules[7].booting:
            await interaction.response.send_message("The generator is still booting.", ephemeral=True)
            return
        if on is generator_status:
            status_message = "Generator is already " + ("on" if generator_status else "off")
            await interaction.response.send_message(status_message, ephemeral=True)
            return

        if on and not generator_status:
            player.ship.modules[7].booting = True
            await interaction.response.send_message("Booting up the generator...")
            message = await interaction.followup.send("░░░░░░░░░░ 0%")
            for percent in range(0, 100, 10):
                bar = "█" * (percent // 10) + "░" * ((100 - percent) // 10)
                await message.edit(content=f"{bar} {percent}%")
                await asyncio.sleep(0.5)
            await message.delete()

            await interaction.followup.send("Generator is now online!")
            player.ship.modules[7].turn_on()
            player.ship.modules[7].booting = False
        elif not on and generator_status:
            player.ship.modules[7].booting = True
            await interaction.response.send_message("Shutting down the generator...")
            message = await interaction.followup.send("██████████ 100%")
            for percent in range(100, 0, -10):
                bar = "█" * (percent // 10) + "░" * ((100 - percent) // 10)
                await message.edit(content=f"{bar} {percent}%")
                await asyncio.sleep(0.5)
            await message.delete()
            player.ship.modules[7].turn_off()
            await interaction.followup.send("Generator has been shut down.")
            player.ship.modules[7].booting = False

async def setup(client: commands.Bot) -> None:
    await client.add_cog(ShipCommands(client))
