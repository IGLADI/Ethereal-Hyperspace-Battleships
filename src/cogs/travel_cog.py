import asyncio
from discord import app_commands
import discord
from discord.ext import commands

from typing import Literal
from player import Player
from location import Location
import asyncio
from utils import check_registered
from player import Player
from ui.simple_banner import ErrorBanner, LoadingBanner, NormalBanner, SuccessBanner

class TravelCommands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="where_am_i", description="Get your location info")
    @app_commands.check(check_registered)
    async def where_am_i(self, interaction: discord.Interaction):
        """Returns the location of the player"""
        player = Player.get(interaction.user.id)
        coordinates = (player.x_pos, player.y_pos)
        if player._is_traveling:
            await interaction.response.send_message(f"You are currently traveling. But you are at {coordinates} right now!", ephemeral=True)
        else:                                        
            location_name = Location(player.x_pos, player.y_pos).is_planet() if Location(player.x_pos, player.y_pos).is_planet() else "floating in space"
            await interaction.response.send_message(
                f"You are currently at {coordinates}, also known as {location_name}.",
                ephemeral=True,
            )

    @app_commands.command(name="travel", description="Travel to a new location")
    @app_commands.check(check_registered)
    async def travel(self, interaction: discord.Interaction, x_coordinate: int, y_coordinate: int):          
        player = Player.get(interaction.user.id)
  
        if player._is_traveling:
            await interaction.response.send_message("Wait untill you arrive before you start a new journey!", ephemeral=True)
            return
        if player._is_mining:
            await interaction.response.send_message("Wait untill you are done mining before you start travelling!", ephemeral=True)
            return
        
        try:
            sleep = player.travel(x_coordinate, y_coordinate)
            banner = LoadingBanner(
                text=f"{player.name} traveling to ({x_coordinate}, {y_coordinate}). Estimated duration = {sleep}.", user=interaction.user, extra_header=" is travelling to a new location"
            )
            await interaction.response.send_message(embed=banner.embed)
        except Exception as e:
            await interaction.response.send_message(f"Couldn't travel: {e}", ephemeral=True)
            return
        else:
            await asyncio.sleep(sleep)
            image, image_name = Location(x_coordinate, y_coordinate).get_image()
            banner = SuccessBanner(
                text=f"{player.name} arrived at {image_name}: ({x_coordinate}, {y_coordinate}).", user=interaction.user, extra_header=" arrived at a new location"
            )
            await interaction.followup.send(embed=banner.embed, file=discord.File(image))
            
    @app_commands.command(name="scan", description="Use your radar to scan the area")
    @app_commands.check(check_registered)
    async def scan(self, interaction: discord.Interaction):

        player = Player.get(interaction.user.id)

        found = player.scan(interaction.user.id)
        await interaction.response.send_message(f"Scanned the area. Found {found} .", ephemeral=True)        

async def setup(client: commands.Bot) -> None:
    await client.add_cog(TravelCommands(client))