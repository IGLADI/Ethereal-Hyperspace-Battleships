import data


async def check_player_exists(interaction):
    if interaction.user not in data.players:
        await interaction.response.send_message("You are not registered as a player.", ephemeral=True)
        return False
    return True


# TODO make this work with negative betts (with the multiplier)
def get_betted_amount(interaction):
    if interaction.channel_id not in data.race_games:
        return 0

    betted_amount = 0
    amount_of_racers = len(data.race_games[interaction.channel_id]["racers"])
    for bet in data.race_games[interaction.channel_id]["bets"]:
        if interaction.user == bet["player"]:
            if bet["bet_amount"] > 0:
                betted_amount += bet["bet_amount"]
            else:
                betted_amount += -bet["bet_amount"] * (amount_of_racers - 1)
    return betted_amount
