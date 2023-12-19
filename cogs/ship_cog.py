import asyncio
from discord import app_commands
import discord
from discord.ext import commands

from typing import Literal
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
        player = data.players[interaction.user]
        ship = player.ship
        ship_message = f"**{player.id}'s ship**\n"
        ship_message += "**Cargo:**\n"
        cargo_info = [str(resource) for resource in ship.modules[5]._capacity]
        ship_message += f"{' '.join(cargo_info)}"
        await interaction.response.send_message(ship_message, ephemeral=True)

    @app_commands.command(name="upgrade_ship", description="Upgrade a module")
    @app_commands.check(check_registered)
    async def upgrade_ship(
        self,
        interaction: discord.Interaction,
        module_name: Literal[
            "Travel Module",
            "Mining Module",
            "Canon",
            "Shield",
            "Fuel",
            "Cargo",
            "Radar",
            "Energy Generator",
        ],
    ):
        player = data.players[interaction.user]
        ship = player.ship
        for module in ship.modules:
            if module_name == module.name:
                try:
                    module.upgrade(player.ship.modules[5])
                except Exception as e:
                    await interaction.response.send_message(
                        f"Couldn't upgrade {module_name}: {e}", ephemeral=True
                    )
                    return
                await interaction.response.send_message(
                    f"Upgraded {module_name} to level {module.level}.", ephemeral=True
                )
                return
        await interaction.response.send_message(
            f"Couldn't find module {module_name}.", ephemeral=True
        )

    # ! For debugging purposes
    @app_commands.command(name="add_cargo", description="For debugging purposes")
    @app_commands.check(check_registered)
    async def add_cargo(
        self,
        interaction: discord.Interaction,
        resource: Literal["Copper", "Silver", "Gold", "Uranium"],
        amount: int,
    ):
        player = data.players[interaction.user]
        new_amount = player.ship.modules[5].add_cargo(resource, amount)
        if new_amount == 0:
            await interaction.response.send_message(
                f"{resource} capacity is full, could not add to your ship.",
                ephemeral=True,
            )
        elif new_amount < amount:
            await interaction.response.send_message(
                f"You added {new_amount} tons of {resource} and left "
                f"{amount - new_amount} tons behind, because you reached maximum capacity.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                f"You added {amount} tons of {resource} to your ship.", ephemeral=True
            )

    @app_commands.command(
        name="toggle_energy_generator", description="Toggle on of the energy generator"
    )
    @app_commands.check(check_registered)
    async def toggle_energy_generator(self, interaction: discord.Interaction, on: bool):
        player = data.players[interaction.user]
        generator_status = player.ship.modules[7].is_on
        if player.ship.modules[7].booting:
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
