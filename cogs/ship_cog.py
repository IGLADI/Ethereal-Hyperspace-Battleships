import asyncio
from discord import app_commands
import discord
from discord.ext import commands

from ui.simple_banner import ErrorBanner, LoadingBanner, NormalBanner, SuccessBanner
from utils import check_player_exists
from typing import Literal
from player import Player

from tabulate import tabulate

async def check_registered(interaction: discord.Interaction) -> bool:
    """Check if a player is registered, if not sends an error message. Else run the function."""
    if not Player.exists(interaction.user.id):
        banner = ErrorBanner(text="You are not registered as a player.", user=interaction.user)
        await interaction.response.send_message(embed=banner.embed, ephemeral=True)
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
        header = "'s Ship"
        table_data = []
        for module in ship.modules.values():
            table_data.append([module.name, module.level])

        modules_info = tabulate(table_data, headers=['Module', 'Level'])

        ship_message = f"```{modules_info}```"
        coordinates = f"{player.x_pos}, {player.y_pos}"
        ship_message += f"```Location: {coordinates}```"
        ship_message += "```Energy: " + f"{ship.energy}```"
        banner = NormalBanner(text=ship_message, user=interaction.user, extra_header=header)
        await interaction.response.send_message(embed=banner.embed, ephemeral=True)

    @app_commands.command(name="inventory", description="Get info on your cargo and it's contents")
    @app_commands.check(check_registered)
    async def cargo_info(self, interaction: discord.Interaction):
        player = Player.get(interaction.user.id)
        ship = player.ship
        ship_message = ""
        ship_message += "".join(
            f"\n- {resource}" for resource in ship.modules["Cargo"].resources.values() if resource.amount > 0
        )
        banner = NormalBanner(
            text=ship_message, user=interaction.user, extra_header="'s Inventory", is_code_block=True
        )
        await interaction.response.send_message(embed=banner.embed, ephemeral=True)

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
            banner = ErrorBanner(text=f"Couldn't find module {module_name}.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        try:
            module.upgrade(player.ship.modules["Cargo"])
        except Exception as e:
            banner = ErrorBanner(text=f"Couldn't upgrade {module_name}: {e}", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        banner = SuccessBanner(f"Upgraded {module_name} to level {module.level}.", user=interaction.user)
        await interaction.response.send_message(embed=banner.embed, ephemeral=True)

    # ! For debugging purposes
    @app_commands.command(name="add_cargo", description="For debugging purposes")
    @app_commands.check(check_registered)
    async def add_cargo(
        self,
        interaction: discord.Interaction,
        resource: Literal["Rock", "Copper", "Silver", "Gold", "Uranium", "Black Matter"],
        amount: int,
    ):
        if await check_player_exists(interaction) is False:
            return

        player = Player.get(interaction.user.id)
        resource_name = resource.lower()
        new_amount = player.ship.modules["Cargo"].add_resource(resource_name, amount)
        
        if new_amount == 0:
            banner = ErrorBanner(
                text=f"{resource} capacity is full, could not add to your ship.", user=interaction.user
            )
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
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
    async def toggle_energy_generator(self, interaction: discord.Interaction, on: Literal["on", "off"]):
        if await check_player_exists(interaction) is False:
            return

        if on == "on":
            on = True
        elif on == "off":
            on = False

        player = Player.get(interaction.user.id)
        if  player.ship.modules["EnergyGenerator"].booting:
            banner = ErrorBanner(text="The generator is still booting.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return
        
        generator_status = player.ship.modules["EnergyGenerator"].is_on
        if on is generator_status:
            banner = ErrorBanner(
                text="Generator is already " + ("on" if generator_status else "off"), user=interaction.user
            )
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        if on and not generator_status:
            player.ship.modules["EnergyGenerator"].booting = True
            banner = LoadingBanner(text="Booting up the generator...\n\n░░░░░░░░░░ 0%", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed)
            for percent in range(0, 101, 10):
                bar = "█" * (percent // 10) + "░" * ((100 - percent) // 10)
                banner = LoadingBanner(
                    text=f"Booting up the generator...\n\n{bar} {percent}%",
                    user=interaction.user,
                )
                await interaction.edit_original_response(embed=banner.embed)
                await asyncio.sleep(0.5)

            banner = SuccessBanner(text="Generator is now online!", user=interaction.user)
            await interaction.edit_original_response(embed=banner.embed)
            player.ship.modules["EnergyGenerator"].turn_on()
            player.ship.modules["EnergyGenerator"].booting = False
        elif not on and generator_status:
            player.ship.modules["EnergyGenerator"].booting = True
            banner = LoadingBanner(
                text="Shutting down the generator...\n\n██████████ 100%",
                user=interaction.user,
            )
            await interaction.response.send_message(embed=banner.embed)
            for percent in range(100, 0, -10):
                bar = "█" * (percent // 10) + "░" * ((100 - percent) // 10)
                banner = LoadingBanner(
                    text=f"Shutting down the generator...\n\n{bar} {percent}%",
                    user=interaction.user,
                )
                await interaction.edit_original_response(embed=banner.embed)
                await asyncio.sleep(0.5)
            player.ship.modules["EnergyGenerator"].turn_off()
            banner = SuccessBanner(text="Generator is now offline!", user=interaction.user)
            await interaction.edit_original_response(embed=banner.embed)
            player.ship.modules["EnergyGenerator"].booting = False


async def setup(client: commands.Bot) -> None:
    await client.add_cog(ShipCommands(client))
