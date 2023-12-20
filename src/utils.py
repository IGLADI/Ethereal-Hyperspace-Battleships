import discord

import data
from database import Database

import database
_db = database.Database()

async def check_registered(interaction: discord.Interaction) -> bool:
    """Check if a player is registered, if not sends an error message. Else run the function."""

async def check_player_exists(interaction):
    if _db.player_exists(interaction.user.id):
        return True

    await interaction.response.send_message("You are not registered as a player.", ephemeral=True)
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
