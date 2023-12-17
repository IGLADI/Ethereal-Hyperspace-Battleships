import asyncio
from discord import app_commands
import discord
from discord.ext import commands
from typing import Literal

import tabulate

import data
from ui.simple_banner import SimpleBanner
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
        ship_message += f"{' '.join(modules_info)}"
        ship_message += f"\nEnergy: {ship.energy}"
        await interaction.response.send_message(ship_message, ephemeral=True)

    @app_commands.command(name="inventory", description="Get your ship's inventory")
    async def inventory(self, interaction: discord.Interaction):
        if await check_player_exists(interaction) is False:
            return

        player = data.players[interaction.user]
        ship = player.ship
        ship_message = []
        for resource in ship.modules[5]._capacity:
            ship_message.append({"Resource": resource.name, "Amount": str(resource.amount)})
        ship_message = tabulate.tabulate(ship_message, headers="keys")
        banner = SimpleBanner(
            text=ship_message, user=interaction.user, extra_header="'s Inventory", is_code_block=True
        )
        await interaction.response.send_message(embed=banner.embed, ephemeral=True)

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

    # ! For debugging purposes
    @app_commands.command(name="add_cargo", description="For debugging purposes")
    async def add_cargo(
        self, interaction: discord.Interaction, resource: Literal["Copper", "Silver", "Gold", "Uranium"], amount: int
    ):
        if await check_player_exists(interaction) is False:
            return

        player = data.players[interaction.user]
        new_amount = player.ship.modules[5].add_cargo(resource, amount)
        if new_amount == 0:
            await interaction.response.send_message(
                f"{resource} capacity is full, could not add to your ship.", ephemeral=True
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

    @app_commands.command(name="toggle_energy_generator", description="Toggle on of the energy generator")
    async def toggle_energy_generator(self, interaction: discord.Interaction, on: bool):
        if await check_player_exists(interaction) is False:
            return

        player = data.players[interaction.user]
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
            banner = SimpleBanner(
                text="Booting up the generator...\n\n░░░░░░░░░░ 0%", user=interaction.user, color=discord.Color.red()
            )
            await interaction.response.send_message(embed=banner.embed)
            for percent in range(0, 101, 10):
                bar = "█" * (percent // 10) + "░" * ((100 - percent) // 10)
                banner = SimpleBanner(
                    text=f"Booting up the generator...\n\n{bar} {percent}%",
                    user=interaction.user,
                    color=discord.Color.red(),
                )
                await interaction.edit_original_response(embed=banner.embed)
                await asyncio.sleep(0.5)

            banner = SimpleBanner(text="Generator is now online!", user=interaction.user)
            await interaction.edit_original_response(embed=banner.embed)
            player.ship.modules[7].turn_on()
            player.ship.modules[7].booting = False
        elif not on and generator_status:
            player.ship.modules[7].booting = True
            banner = SimpleBanner(
                text="Shutting down the generator...\n\n██████████ 100%",
                user=interaction.user,
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=banner.embed)
            for percent in range(100, -1, -10):
                bar = "█" * (percent // 10) + "░" * ((100 - percent) // 10)
                banner = SimpleBanner(
                    text=f"Shutting down the generator...\n\n{bar} {percent}%",
                    user=interaction.user,
                    color=discord.Color.red(),
                )
                await interaction.edit_original_response(embed=banner.embed)
                await asyncio.sleep(0.5)
            player.ship.modules[7].turn_off()
            banner = SimpleBanner(text="Generator is now offline!", user=interaction.user)
            await interaction.edit_original_response(embed=banner.embed)
            player.ship.modules[7].booting = False


async def setup(client: commands.Bot) -> None:
    await client.add_cog(ShipCommands(client))
