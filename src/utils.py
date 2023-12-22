import asyncio
import discord

import data
from ui.simple_banner import ErrorBanner, LoadingBanner, SuccessBanner

import database

_db = database.Database()


async def check_registered(interaction: discord.Interaction) -> bool:
    if data.players.get(interaction.user.id):
        return True

    if _db.player_exists(interaction.user.id):
        return True

    banner = ErrorBanner(interaction.user, "You are not registered as a player.")
    await interaction.response.send_message(embed=banner.embed, ephemeral=True)
    return False


# TODO make this work with negative betts (with the multiplier)
def get_betted_amount(discord_id):
    total_bet_amount = 0
    for channel_id, channel_data in data.race_games.items():
        amount_of_racers = len(data.race_games[channel_id]["racers"])
        for bet in channel_data["bets"]:
            if bet["player"].id == discord_id:
                if bet["bet_amount"] > 0:
                    total_bet_amount += bet["bet_amount"]
                else:
                    total_bet_amount += -bet["bet_amount"] * (amount_of_racers - 1)

    return total_bet_amount


def get_resource_amount(cargo, resource_name: str) -> int:
    resource_name = resource_name.lower()
    resource = cargo.resources.get(resource_name)
    return resource.amount if resource else 0


def send_bug_report(discord_id, bug_report):
    _db.store_bug_report(discord_id, bug_report)


async def loading_animation(
    interaction: discord.Interaction,
    loading_logo="░",
    loaded_logo="█",
    loading_text="",
    loaded_text="",
    sleep_time=0.5,
    reverse=False,
    extra_image=None,
):
    banner = LoadingBanner(
        text="",
        user=interaction.user,
    )
    await interaction.response.send_message(embed=banner.embed)

    if reverse:
        steps = 100, 0, -10
    else:
        steps = 0, 100, 10

    for percent in range(*steps):
        bar = loaded_logo * (percent // 10) + loading_logo * ((100 - percent) // 10)
        banner = LoadingBanner(
            text=f"{loading_text}\n\n{bar} {percent}%",
            user=interaction.user,
        )
        await interaction.edit_original_response(embed=banner.embed)
        await asyncio.sleep(sleep_time)

    banner = SuccessBanner(text=loaded_text, user=interaction.user)
    await interaction.edit_original_response(embed=banner.embed)
    if extra_image:
        await interaction.edit_original_response(attachments=[extra_image])
