from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands
from tabulate import tabulate

from player import Player
from ui.simple_banner import ErrorBanner, NormalBanner, SuccessBanner
from utils import check_registered, loading_animation


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

        modules_info = tabulate(table_data, headers=["Module", "Level"])

        ship_message = f"```{modules_info}```"
        coordinates = f"{player.x_pos}, {player.y_pos}"
        ship_message += f"```Location: {coordinates}```"
        ship_message += "```Energy: " + f"{ship.energy}```"
        ship_message += "```Armor: " + f"{ship.modules['Armor'].hp}```"
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

    @app_commands.command(name="upgrade_module", description="Upgrade a module")
    @app_commands.check(check_registered)
    async def upgrade_module(
        self,
        interaction: discord.Interaction,
        module_name: Literal[
            "TravelModule",
            "MiningModule",
            "Canon",
            "Armor",
            "Fuel",
            "Cargo",
            "Radar",
            "EnergyGenerator",
            "SolarPanel",
        ],
    ):
        player = Player.get(interaction.user.id)
        ship = player.ship
        module = ship.modules.get(module_name)

        if not module:
            banner = ErrorBanner(text=f"Couldn't find module {module_name}.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return
        
        # Free upgrade for tutorial
        if player.tutorial == 0:
            exploit = module.free_upgrade(player.id)
            if exploit:
                banner = ErrorBanner(text=f"Are you trying to make me upgrade 2 modules for you? Do you want to start a war?", user=interaction.user)
            else:
                banner = SuccessBanner(text=f"Ruebñ upgraded your {module_name} to level {module.level} free of charge!", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return
        
        try:
            module.upgrade(player.ship.modules["Cargo"])
            banner = SuccessBanner(text=f"Upgraded {module_name} to level {module.level}.", user=interaction.user)
        except Exception as e:
            banner = ErrorBanner(text=f"Couldn't upgrade {module_name}: {e}", user=interaction.user)
        finally:
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)

    @app_commands.command(name="toggle_energy_generator", description="Toggle on of the energy generator")
    @app_commands.check(check_registered)
    async def toggle_energy_generator(self, interaction: discord.Interaction, toggle: Literal["on", "off"]):
        if toggle == "on":
            toggle = True
        elif toggle == "off":
            toggle = False

        player = Player.get(interaction.user.id)
        if player.ship.modules["EnergyGenerator"].booting:
            banner = ErrorBanner(text="The generator is still booting.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        generator_status = player.ship.modules["EnergyGenerator"].is_on
        if toggle is generator_status:
            banner = ErrorBanner(
                text="Generator is already " + ("on" if generator_status else "off"), user=interaction.user
            )
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        if toggle and not generator_status:
            player.ship.modules["EnergyGenerator"].booting = True
            await loading_animation(
                loading_text="Booting up the generator...",
                loaded_text="Generator is now online!",
                interaction=interaction,
            )
            player.ship.modules["EnergyGenerator"].turn_on()
            player.ship.modules["EnergyGenerator"].booting = False
        elif not toggle and generator_status:
            player.ship.modules["EnergyGenerator"].booting = True
            await loading_animation(
                loading_text="Shutting down the generator...",
                loaded_text="Generator is now offline!",
                interaction=interaction,
                reverse=True,
            )
            player.ship.modules["EnergyGenerator"].turn_off()
            player.ship.modules["EnergyGenerator"].booting = False


async def setup(client: commands.Bot) -> None:
    await client.add_cog(ShipCommands(client))
