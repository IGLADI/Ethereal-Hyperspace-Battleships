import asyncio
from discord import app_commands
import discord
from discord.ext import commands

from typing import Literal
from player import Player

import asyncio
from utils import check_player_exists
from player import Player
import data


async def check_registered(interaction: discord.Interaction) -> bool:
    """Check if a player is registered, if not sends an error message. Else run the function."""
    if not Player.exists(interaction.user.id):
        await interaction.response.send_message(
            "You are not registered as a player.", ephemeral=True
        )
        return False
    return True


class ShipCommands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="ship_info", description="Get info on your ship")
    @app_commands.check(check_registered)
    async def ship_info(self, interaction: discord.Interaction):

        player = Player.get(interaction.user.id)
        ship = player.ship
        ship_message = f"**{player.name}'s ship**\n"
        ship_message += f"**Location:** {player.location_name()}\n"
        ship_message += "**Modules:**\n"
        modules_info = [str(module) for module in ship.modules.values()]
        ship_message += f"{' '.join(modules_info)}"
        ship_message += f"\nEnergy: {ship.energy}"
        await interaction.response.send_message(ship_message, ephemeral=True)

    @app_commands.command(
        name="inventory", description="Get info on your cargo and it's contents"
    )
    @app_commands.check(check_registered)
    async def cargo_info(self, interaction: discord.Interaction):

        player = Player.get(interaction.user.id)
        ship = player.ship
        ship_message = f"**{player.name}'s ship**\n"
        ship_message += "**Cargo:**"
        ship_message += "".join(
            f"\n- {resource}"
            for resource in ship.modules["Cargo"].resources.values()
            if resource.amount > 0
        )
        await interaction.response.send_message(ship_message, ephemeral=True)

    @app_commands.command(name="upgrade_ship", description="Upgrade a module")
    @app_commands.check(check_registered)
    async def upgrade_ship(
        self,
        interaction: discord.Interaction,
        module_name: Literal[
            "TravelModule",
            "MiningModule",
            "Canon",
            "Shield",
            "Fuel",
            "Cargo",
            "Radar",
            "EnergyGenerator",
        ],
    ):
        player = Player.get(interaction.user.id)
        ship = player.ship
        module = ship.modules.get(module_name)

        if not module:
            await interaction.response.send_message(
                f"Couldn't find module {module_name}.", ephemeral=True
            )
            return
        try:
            module.upgrade(player.ship.modules["Cargo"])
        except Exception as e:
            await interaction.response.send_message(
                f"Couldn't upgrade {module_name}: {e}", ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"Upgraded {module_name} to level {module.level}.", ephemeral=True
        )

    # ! For debugging purposes
    @app_commands.command(name="add_cargo", description="For debugging purposes")
    @app_commands.check(check_registered)
    async def add_cargo(
        self,
        interaction: discord.Interaction,
        resource: Literal[
            "Rock", "Copper", "Silver", "Gold", "Uranium", "Black Matter"
        ],
        amount: int,
    ):
        player = Player.get(interaction.user.id)
        resource_name = resource.lower()
        player.ship.modules["Cargo"].add_resource(resource_name, amount)
        await interaction.response.send_message(
            f"Added {amount} {resource}.",
            ephemeral=True,
        )

    @app_commands.command(
        name="toggle_energy_generator", description="Toggle on of the energy generator"
    )
    @app_commands.check(check_registered)
    async def toggle_energy_generator(self, interaction: discord.Interaction, on: bool):
        player = Player.get(interaction.user.id)
        generator_status = player.ship.modules["EnergyGenerator"].is_on
        if player.ship.modules["EnergyGenerator"].booting:
            await interaction.response.send_message(
                "The generator is still booting.", ephemeral=True
            )

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


async def setup(client: commands.Bot) -> None:
    await client.add_cog(ShipCommands(client))
