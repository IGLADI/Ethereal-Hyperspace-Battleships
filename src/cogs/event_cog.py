from discord import app_commands
import discord
from discord.ext import commands

from utils import check_registered, check_event_channel
from ui.simple_banner import ErrorBanner, LoadingBanner, NormalBanner, SuccessBanner
from player import Player
import data

class EventCommands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
    
    @app_commands.command(name="join_event", description="Join an ongoing event")
    @app_commands.check(check_registered)
    @app_commands.check(check_event_channel)
    async def event(self, interaction: discord.Interaction):
        if data.event_manager is None or data.event_manager.events == {}:
            banner = ErrorBanner(text="There is no event running right now.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return
        
        player = Player.get(interaction.user.id)
        data.event_manager.events[1].participants = player
        banner = SuccessBanner(text=f"{player.name} joined the event!\nParticipants: {[part.name for part in data.event_manager.events[1].participants]}", user=interaction.user)
        await interaction.response.send_message(embed=banner.embed)
        private_banner = SuccessBanner(text=f"Try to find Ruebñ's lost ship by scanning the search area, if you found it, use /locate [x_pos] [y_pos] to let Ruebñ know!\n", user=interaction.user)
        await interaction.followup.send(embed=private_banner.embed, ephemeral=True)

    @app_commands.command(name="locate", description="Locate something in the world")
    @app_commands.check(check_registered)
    @app_commands.check(check_event_channel)
    async def locate(self, interaction: discord.Interaction, x_pos: int, y_pos: int):
        if data.event_manager is None or data.event_manager.events == {}:
            banner = ErrorBanner(text="There is nothing lost right now. So no need to locate somthing.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return
        
        player = Player.get(interaction.user.id)
        if player not in data.event_manager.events[1].participants:
            banner = ErrorBanner(text="You are not participating in this event. Use /join_event to help searching.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        if data.event_manager.events[1].x_pos == x_pos and data.event_manager.events[1].y_pos == y_pos:
            for participant in data.event_manager.events[1].participants:
                participant.ship.modules["Cargo"].add_resource(data.event_manager.events[1].prize[0], data.event_manager.events[1].prize[1])
            banner = SuccessBanner(text=f"Congratulations, you found the lost ship!\nAll participants got {data.event_manager.events[1].prize[1]} tons of {data.event_manager.events[1].prize[0]}!", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            data.event_manager.events[1].completed = True
            return

        banner = ErrorBanner(text=f"Sorry, you didn't find the lost ship. Try again!", user=interaction.user)
        await interaction.response.send_message(embed=banner.embed, ephemeral=True)
        return


async def setup(client: commands.Bot) -> None:
    await client.add_cog(EventCommands(client))