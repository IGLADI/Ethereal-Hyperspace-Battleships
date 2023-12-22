from uu import Error
from discord import app_commands
import discord
from discord.ext import commands

from player import Player
from location import Location, Coordinate
from ui.simple_banner import ErrorBanner, NormalBanner
from utils import check_registered, loading_animation


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
            banner = NormalBanner(text=f"You are currently traveling. Now at {coordinates}.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
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
            text = "Wait untill you arrive before you start a new journey!"
            banner = ErrorBanner(text=text, user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        if player._is_mining:
            text = "Wait untill you are done mining before you start travelling!"
            banner = ErrorBanner(text=text, user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        destination = Coordinate(x, y)

        try:
            distance = player.travel(destination)
            if distance == 0:
                banner = ErrorBanner(
                    user=interaction.user,
                    text="You are already at that location!",
                )
                await interaction.response.send_message(embed=banner.embed, ephemeral=True)
                return

            location = None
            if destination.is_location():
                location = Location.fromcoordinate(destination)
                image = location.image_path
            else:
                image = "../assets/space/space0.jpg"

            if location is None:
                location_name = "floating in space"
            else:
                location_name = location.name
            image = discord.File(image, filename="image.png")

            await loading_animation(
                interaction,
                sleep_time=distance / 10,
                loading_text=f"Traveling to ({x}, {y})",
                loaded_text=f"Arrived at ({x}, {y}) aka {location_name}",
                extra_image=image,
            )
        except Exception as e:
            await interaction.response.send_message(f"Couldn't travel: {e}", ephemeral=True)
            return

    @app_commands.command(name="scan", description="Use your radar to scan the area")
    @app_commands.check(check_registered)
    async def scan(self, interaction: discord.Interaction):
        player = Player.get(interaction.user.id)

        found = player.scan(interaction.user.id)
        await interaction.response.send_message(f"Scanned the area. Found {found} .", ephemeral=True)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(TravelCommands(client))
