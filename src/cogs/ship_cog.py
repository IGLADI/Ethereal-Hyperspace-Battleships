import asyncio
from discord import app_commands
import discord
from discord.ext import commands

from typing import Literal
from player import Player
from utils import check_player_exists

import data


class ShipCommands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="ship_info", description="Get info on your ship")
    @app_commands.check(check_player_exists)
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
    @app_commands.check(check_player_exists)
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
    @app_commands.check(check_player_exists)
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
    @app_commands.check(check_player_exists)
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
    @app_commands.check(check_player_exists)
    async def toggle_energy_generator(self, interaction: discord.Interaction, on: bool):
        player = Player.get(interaction.user.id)
        generator_status = player.ship.modules["EnergyGenerator"].is_on
        if player.ship.modules["EnergyGenerator"].booting:
            await interaction.response.send_message(
                "The generator is still booting.", ephemeral=True
            )
            return
        if on is generator_status:
            status_message = "Generator is already " + (
                "on" if generator_status else "off"
            )
            await interaction.response.send_message(status_message, ephemeral=True)
            return

        if on and not generator_status:
            player.ship.modules["EnergyGenerator"].booting = True
            await interaction.response.send_message("Booting up the generator...")
            message = await interaction.followup.send("░░░░░░░░░░ 0%")
            for percent in range(0, 100, 10):
                bar = "█" * (percent // 10) + "░" * ((100 - percent) // 10)
                await message.edit(content=f"{bar} {percent}%")
                await asyncio.sleep(0.5)
            await message.delete()

            await interaction.followup.send("Generator is now online!")
            player.ship.modules["EnergyGenerator"].turn_on()
            player.ship.modules["EnergyGenerator"].booting = False
        elif not on and generator_status:
            player.ship.modules["EnergyGenerator"].booting = True
            await interaction.response.send_message("Shutting down the generator...")
            message = await interaction.followup.send("██████████ 100%")
            for percent in range(100, 0, -10):
                bar = "█" * (percent // 10) + "░" * ((100 - percent) // 10)
                await message.edit(content=f"{bar} {percent}%")
                # await asyncio.sleep(0.5)
            await message.delete()
            player.ship.modules["EnergyGenerator"].turn_off()
            await interaction.followup.send("Generator has been shut down.")
            player.ship.modules["EnergyGenerator"].booting = False


async def setup(client: commands.Bot) -> None:
    await client.add_cog(ShipCommands(client))
