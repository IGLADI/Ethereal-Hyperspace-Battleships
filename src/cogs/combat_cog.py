import asyncio
import random
from uu import Error
import discord
from discord.ext import commands
from discord import app_commands
from location import Coordinate
from player import Player
from ui.simple_banner import ErrorBanner, SuccessBanner

from utils import check_registered


class CombatCommands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="target", description="Target a player")
    @app_commands.check(check_registered)
    async def target(self, interaction: discord.Interaction, target: discord.User):
        player = Player.get(interaction.user.id)

        if not Player.exists(target.id):
            banner = ErrorBanner(text="The recipient doesn't have an account.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return
        target_player = Player.get(target.id)

        # TODO add a ranging module changing the targetting range
        if self.distance_to_player(interaction.user, player, target_player) > 10:
            banner = ErrorBanner(text="You can only target players within 10 units.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        player.target = target_player
        player.bonus_hit_chance = 0

        banner = SuccessBanner(text=f"You are now targeting {target_player.name}.", user=interaction.user)
        await interaction.response.send_message(embed=banner.embed)

    def distance_to_player(self, user: discord.User, player: Player, target: Player) -> float:
        player_coordinate = Coordinate(x=player.x_pos, y=player.y_pos)
        target_coordinate = Coordinate(x=target.x_pos, y=target.y_pos)
        return player_coordinate.distance_to(target_coordinate)

    @app_commands.command(name="lock", description="Increase your hit chance")
    @app_commands.check(check_registered)
    async def lock(self, interaction: discord.Interaction):
        player = Player.get(interaction.user.id)
        if player.target is None:
            banner = ErrorBanner(text="You need to target a player first.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        if player.bonus_hit_chance >= 20:
            banner = ErrorBanner(text="You can't lock on anymore.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        player.bonus_hit_chance += 10
        banner = SuccessBanner(
            text=f"Your hit chance increased, your bonus is now {player.bonus_hit_chance}.", user=interaction.user
        )
        await interaction.response.send_message(embed=banner.embed)

        for _ in range(10):
            player.bonus_hit_chance -= 1
            await asyncio.sleep(10)

    # TODO when different weopons will exist add a toggle on&off for the weopons
    @app_commands.command(name="attack", description="Attack a player")
    @app_commands.check(check_registered)
    async def attack(self, interaction: discord.Interaction):
        player = Player.get(interaction.user.id)
        if player.target is None:
            banner = ErrorBanner(text="You need to target a player first.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        player = Player.get(interaction.user.id)
        target_player = Player.get(player.target.id)

        if self.distance_to_player(interaction.user, player, target_player) > 10:
            banner = ErrorBanner(text="You can only attack players within 10 units.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        if player.ship.energy < 10:
            banner = ErrorBanner(text="You don't have enough energy.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return
        player.ship.energy -= 10

        if random.random() * 100 > player.bonus_hit_chance + player.ship.modules["Canon"].hit_chance:
            banner = ErrorBanner(text="You missed!", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed)
            return

        damage = player.ship.modules["Canon"].strength
        target_player.ship.modules["Armor"].hp -= damage

        
        banner = SuccessBanner(text=f"You hit {target_player.name} for {damage} damage!", user=interaction.user)
        await interaction.response.send_message(embed=banner.embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(CombatCommands(client))
