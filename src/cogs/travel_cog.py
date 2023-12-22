import asyncio
from discord import app_commands
import discord
from discord.ext import commands

from typing import Literal
from player import Player
from location import Location, Coordinate
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
            await interaction.response.send_message(
                f"You are currently traveling. But you are at {coordinates} right now!", ephemeral=True
            )
            return

        pos = Coordinate(x=player.x_pos, y=player.y_pos)
        if pos.is_location():
            location_name = Location(x_pos=player.x_pos, y_pos=player.y_pos).name
            text = f"You are currently at {coordinates}, also known as {location_name}."
        else:
            text = f"floating in space at {coordinates}"

        banner = NormalBanner(text=text, user=interaction.user)
        await interaction.response.send_message(embed=banner.embed, ephemeral=True)

    @app_commands.command(name="travel", description="Travel to a new location")
    @app_commands.check(check_registered)
    async def travel(self, interaction: discord.Interaction, x: int, y: int):
        player = Player.get(interaction.user.id)

        if player._is_traveling:
            await interaction.response.send_message(
                "Wait untill you arrive before you start a new journey!", ephemeral=True
            )
            return
        if player._is_mining:
            await interaction.response.send_message(
                "Wait untill you are done mining before you start travelling!", ephemeral=True
            )
            return

        destination = Coordinate(x, y)

        try:
            distance = player.travel(destination)
            banner = LoadingBanner(
                text=f"{player.name} traveling to ({x}, {y}). Estimated duration = {distance}.",
                user=interaction.user,
                extra_header=" is travelling to a new location",
            )
            await interaction.response.send_message(embed=banner.embed)
        except Exception as e:
            await interaction.response.send_message(f"Couldn't travel: {e}", ephemeral=True)
            return
        else:
            await asyncio.sleep(distance * 1)

            if destination.is_location():
                l = Location.fromcoordinate(destination)
                image = l.image_path
                text = f"{player.name} arrived at {l.name}: ({x}, {y})."
            else:
                image = "../assets/space/space0.jpg"
                text = f"{player.name} floating in space at ({x}, {y})."

            banner = SuccessBanner(
                text=text,
                user=interaction.user,
                extra_header=" arrived at a new location",
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
