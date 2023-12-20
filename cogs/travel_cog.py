import asyncio
from discord import app_commands
import discord
from discord.ext import commands

from typing import Literal
from player import Player
from location import Location
import asyncio
from utils import check_player_exists
from player import Player

async def check_registered(interaction: discord.Interaction) -> bool:
    """Check if a player is registered, if not sends an error message. Else run the function."""
    if not Player.exists(interaction.user.id):
        await interaction.response.send_message(
            "You are not registered as a player.", ephemeral=True
        )
        return False
    return True

class TravelCommands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="travel", description="Travel to a new location")
    @app_commands.check(check_registered)
    async def travel(self, interaction: discord.Interaction, x_coordinate: int, y_coordinate: int):          
        player = Player.get(interaction.user.id)
  
        if player._is_traveling:
            await interaction.response.send_message("Wait untill you arrive before you start a new journey!", ephemeral=True)
            return
        
        try:
            sleep = player.travel(x_coordinate, y_coordinate)
            await interaction.response.send_message(f"{player.id} traveling to ({x_coordinate}, {y_coordinate}). Estimated duration = {sleep}.")
        except Exception as e:
            await interaction.response.send_message(f"Couldn't travel: {e}", ephemeral=True)
            return
        else:
            await asyncio.sleep(sleep)
            image, image_name = Location(x_coordinate, y_coordinate).get_image()
            await interaction.followup.send(f"{player.id} arrived at {image_name}: ({x_coordinate}, {y_coordinate}).\n", file=discord.File(image))
            
    @app_commands.command(name="scan", description="Use your radar to scan the area")
    @app_commands.check(check_registered)
    async def scan(self, interaction: discord.Interaction):

        player = Player.get(interaction.user.id)

        found = player.scan(interaction.user.id)
        await interaction.response.send_message(f"Scanned the area. Found {found} .", ephemeral=True)        

async def setup(client: commands.Bot) -> None:
    await client.add_cog(TravelCommands(client))