import discord
from discord import app_commands
from discord.ext import commands

from ui.simple_banner import NormalBanner
from utils import check_registered


class CasinoGame(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="casino_info", description="Get info on the casino commands")
    @app_commands.check(check_registered)
    async def casino_info(self, interaction: discord.Interaction):
        casino_info = "Here is a list of casino commands:\n"
        casino_info += "/casino_info - Get info on the casino commands\n"
        casino_info += "/create_race - Create a race\n"
        casino_info += "/race_info - Bet on a race\n"
        banner = NormalBanner(text=casino_info, user=interaction.user)
        await interaction.response.send_message(embed=banner.embed, ephemeral=True)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(CasinoGame(client))
