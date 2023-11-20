import data


async def check_player_exists(interaction):
    if interaction.user not in data.players:
        await interaction.response.send_message("You are not registered as a player.", ephemeral=True)
        return False
    return True


def get_betted_amount(interaction):
    betted_amount = 0
    for channel_id in data.race_games:
        for bet in data.race_games[channel_id]["bets"]:
            if interaction.user == bet["player"]:
                betted_amount += bet["bet_amount"]
    return betted_amount
