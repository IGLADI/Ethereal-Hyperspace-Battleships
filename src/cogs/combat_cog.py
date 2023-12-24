import asyncio
import random
import discord
from discord.ext import commands
from discord import app_commands
from location import Coordinate
from player import Player
from ui.simple_banner import ErrorBanner, SuccessBanner

from utils import check_registered


# TODO add combat in /help
class CombatCommands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="target", description="Target a player")
    @app_commands.check(check_registered)
    # TODO can't target around the spawn
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

        if player == target_player:
            banner = ErrorBanner(text="You can't target yourself.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        # check if your in the spawn
        if abs(target_player.x_pos) <= 20 and abs(target_player.y_pos) <= 20:
            banner = ErrorBanner(text="You can't target players within 20 units of the spawn.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        await target.send(f"{player.name} is targeting you!")

        player.target = target_player
        player.bonus_hit_chance = 0

        banner = SuccessBanner(text=f"You are now targeting {target.mention}.", user=interaction.user)
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

        if player.ship.energy < 10:
            banner = ErrorBanner(text="You don't have enough energy.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        player.ship.energy -= 10
        player.bonus_hit_chance += 10

        banner = SuccessBanner(
            text=f"Your hit chance increased, your bonus is now {player.bonus_hit_chance}.", user=interaction.user
        )
        await interaction.response.send_message(embed=banner.embed)

        for _ in range(10):
            player.bonus_hit_chance -= 1
            await asyncio.sleep(10)

    async def respawn_player(self, player: Player, killer: Player = None):
        player.x_pos = 0
        player.y_pos = 0

        player.ship.modules["Armor"].hp = player.ship.modules["Armor"].defense

        for resource in player.ship.modules["Cargo"].resources.values():
            if killer:
                killer.ship.modules["Cargo"].add_resource(resource.name, int(resource.amount * 0.5))
            resource.amount = int(resource.amount * 0.5)

        # send a dm that he died
        player_discord = self.client.get_user(player.id)
        await player_discord.send(f"Your ship has been destroyed by {killer.name}!")

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

        if abs(target_player.x_pos) <= 20 and abs(target_player.y_pos) <= 20:
            banner = ErrorBanner(text="You can't attack players within 20 units of the spawn.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

        if abs(player.x_pos) <= 20 and abs(player.y_pos) <= 20:
            banner = ErrorBanner(text="You can't attack players while you are in the spawn.", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed, ephemeral=True)
            return

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

        if target_player.ship.modules["Armor"].hp <= 0:
            # TODO add an image of an exploded ship
            banner = SuccessBanner(
                text=f"You hit {target_player.name} for {damage} damage and destroyed their ship!",
                user=interaction.user,
            )
            await interaction.response.send_message(embed=banner.embed)

            await self.respawn_player(target_player, player)

        else:
            banner = SuccessBanner(text=f"You hit {target_player.name} for {damage} damage!", user=interaction.user)
            await interaction.response.send_message(embed=banner.embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(CombatCommands(client))
