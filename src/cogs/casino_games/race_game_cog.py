import discord
from discord import app_commands
from discord.ext import commands

from typing import Literal

import asyncio
import random
from tabulate import tabulate

import data
from races import Racer
from utils import check_registered


# TODO add imgs (AI/start w hardcoded)
# TODO add casino info
class RaceGame(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.race_details = {
            "blob": {"distance": 10, "min_speed": 0, "max_speed": 1},
            "swoop": {"distance": 1000, "min_speed": 10, "max_speed": 50},
            "ratts": {"distance": 100, "min_speed": 0, "max_speed": 10},
            "pod": {"distance": 10000, "min_speed": 25, "max_speed": 100},
        }
        # TODO rename variables and store them simply in the class to then use them and write them back

    @app_commands.command(name="race_info", description="Get info on the different races types to bet on")
    @app_commands.check(check_registered)
    async def race_info(self, interaction: discord.Interaction):
        race_info_text = "Race Details:\n"
        for race, details in self.race_details.items():
            race_info_text += f"\n{race.capitalize()}:\n"
            race_info_text += f"Distance: {details['distance']} m\n"
            race_info_text += f"Minimum Speed: {details['min_speed']*10} m/sec\n"
            race_info_text += f"Maximum Speed: {details['max_speed']*10} m/sec\n"
        await interaction.response.send_message(race_info_text)

    # TODO maybe make a discord thread for the race?
    # TODO split this command into multiple functions (this is a temporary solution just to demonstrate cogs)
    @app_commands.command(
        name="create_race",
        description="creates a racing game if you provide the right arguments such as type and racers amount",
    )
    @app_commands.check(check_registered)
    async def create_race(
        self,
        interaction: discord.Interaction,
        race_type: Literal["blob", "swoop", "ratts", "pod"],
        amount_of_racers: int,
    ):
        race_info = self.race_details.get(race_type.lower())
        race_distance = race_info["distance"]
        min_speed = race_info["min_speed"]
        max_speed = race_info["max_speed"]

        if amount_of_racers < 2:
            await interaction.response.send_message("You need at least 2 racers.", ephemeral=True)
            return
        if amount_of_racers > 64:
            await interaction.response.send_message("You can't have more than 64 racers.", ephemeral=True)
            return
        if interaction.channel_id in data.race_games:
            await interaction.response.send_message("A race is already in progress in this channel.", ephemeral=True)
            return

        data.race_games[interaction.channel_id] = {
            "racers": [],
            "bets": [],
        }

        await starting_message_and_generate_racers(interaction, amount_of_racers, race_type)

        # check if there are at least 2 different users that placed bets
        gamblers = set()
        for bet in data.race_games[interaction.channel_id].get("bets", []):
            user = bet["player"]
            gamblers.add(user)
        if len(gamblers) < 2:
            await interaction.followup.send("At least two different users need to place bets to start the race.")
            del data.race_games[interaction.channel_id]
            return

        # TODO need to lock the bets, they can now bet during the race (just add a race_started boolean)
        winner = await race(interaction, race_type, race_distance, min_speed, max_speed)

        await distribute_winnings(interaction, winner, amount_of_racers)

        del data.race_games[interaction.channel_id]

    # ? maybe change this to use discord drop down menus? (to choose on which racer to bet on)
    # TODO add a command to modify/remove betts
    # this need to be checked before betting
    @app_commands.command(
        name="bet_on_race", description="Bet on a racer! To bet on his loss, bet with a negative amount"
    )
    @app_commands.check(check_registered)
    async def bet_on_race(self, interaction: discord.Interaction, betamount: int, racer_to_bet_on: str):
        if interaction.channel_id not in data.race_games:
            await interaction.response.send_message(
                "No race game is currently in progress in this channel.", ephemeral=True
            )
            return
        if betamount == 0:
            await interaction.response.send_message("You can't bet $0.", ephemeral=True)
            return
        # TODO change negative bets to take in account the multiplier
        # (so if thereare 5 racers and you bet -10 you lose 50)
        # TODO add a check to not bet 0$
        # TODO add a custom message for negative bets
        if data.players[interaction.user].money < abs(betamount):
            await interaction.response.send_message("You don't have enough money.", ephemeral=True)
            return
        # TODO this works but also need to be implemented in get betted amount
        amount_of_racers = len(data.race_games[interaction.channel_id]["racers"])
        if betamount < 0:
            if data.players[interaction.user].money < abs(betamount * (amount_of_racers - 1)):
                await interaction.response.send_message("You don't have enough to bet on a lost.", ephemeral=True)
                return
        if any(
            bet["player"] == interaction.user
            and bet["racer_to_bet_on"].strip().lower().split(" ")[0] == racer_to_bet_on.strip().lower().split(" ")[0]
            for bet in data.race_games[interaction.channel_id]["bets"]
        ):
            # TODO modify the message once the ... commands are implemented
            await interaction.response.send_message(
                f"You have already bet on {racer_to_bet_on.capitalize()} for this race.\n use ... to change your bets",
                ephemeral=True,
            )
            return
        racers_in_channel = data.race_games[interaction.channel_id]["racers"]
        if not any(
            racer.name.strip().lower().split(" ")[0] == racer_to_bet_on.strip().lower().split(" ")[0]
            for racer in racers_in_channel
        ):
            racer_names = "\n".join([racer.name for racer in racers_in_channel])
            await interaction.response.send_message(
                f"This racer isn't in the race!\nPlease pick one of the following racers:\n{racer_names}",
                ephemeral=True,
            )
            return

        data.race_games[interaction.channel_id]["bets"].append(
            {"player": interaction.user, "bet_amount": betamount, "racer_to_bet_on": racer_to_bet_on}
        )
        # ? maybe always display first+last name?
        if betamount > 0:
            await interaction.response.send_message(f"You have bet ${betamount} on {racer_to_bet_on.capitalize()}.")
        else:
            cost = -betamount * (amount_of_racers - 1)
            await interaction.response.send_message(
                f"You have bet ${-betamount} on {racer_to_bet_on.capitalize()} to lose, which costs ${cost}."
            )


# TODO should be added to the class and use self instead of passing arguments
async def starting_message_and_generate_racers(interaction, amount_of_racers, race_type="pod"):
    # create the racers & send the intro msg
    racers = []
    intro = f"Welcome to this {race_type} race! \nGive a warm applause for our racers:"
    for _ in range(amount_of_racers):
        new_racer = Racer()
        # don't create 2 racers with the same first name
        while any(racer.name.split(" ")[0] == new_racer.name.split(" ")[0] for racer in racers):
            new_racer = Racer()
        racers.append(new_racer)
        intro += f"\n{new_racer.name}"
    await interaction.response.send_message(intro)

    # initialize & send the join msg to eddit
    message_to_send = f"A new race game will begin in {60} seconds! \n"
    message_to_send += "Type `/bet_on_race <bet_amount> <player_to_bet_on>` to participate."
    message = await interaction.followup.send(message_to_send, wait=True)
    data.race_games[interaction.channel_id]["racers"] = racers

    # edit the join message every second to show the timer
    timer = 60
    while True:
        if timer <= 0:
            break
        message_to_send = f"A new race game will begin in {timer} seconds! \n"
        message_to_send += "Type `/bet_on_race <bet_amount> <player_to_bet_on>` to participate."
        timer -= 1
        await message.edit(content=message_to_send)
        await asyncio.sleep(1)
    await message.delete()


# TODO add a cool animation under each racer (like a progress bar with custom emojis)
async def race(interaction, race_type, race_distance, min_speed, max_speed):
    # send a table with the bets
    start_message = f"The {race_type} race is starting now!"
    start_message += "\nHere are the bets:"
    bet_table = []
    headers = ["Player", "Bet Amount", "Racer"]
    for bet in data.race_games[interaction.channel_id].get("bets", []):
        bet_table.append([bet["player"], bet["bet_amount"], bet["racer_to_bet_on"]])
    table = tabulate(bet_table, headers=headers)
    await interaction.followup.send(f"{start_message}\n```{table}```")

    # create the table with the racers
    racers_list = data.race_games[interaction.channel_id]["racers"]
    distances = [racer.distance for racer in racers_list]
    race_status = []
    for racer in racers_list:
        distance = 0
        race_status.append([racer.name, f"{distance}m"])
    race_table = tabulate(race_status, headers=["Racer", "Distance"])
    message = await interaction.followup.send(f"```\n{race_table}\n```", wait=True)

    # update the racers table with distances
    while max(distances) < race_distance:
        race_data = []
        for racer in racers_list:
            racer.distance += random.randint(min_speed, max_speed)
            distance = race_distance if racer.distance > race_distance else racer.distance
            # ? maybe add 0000.. so that amount of numbers dont change
            race_data.append([racer.name, f"{distance}m"])

        race_table = tabulate(race_data, headers=["Racer", "Distance"])
        await message.edit(content=f"```\n{race_table}\n```")
        distances = [racer.distance for racer in racers_list]
        asyncio.sleep(0.1)

    # print the winner of the race
    winner = max(data.race_games[interaction.channel_id]["racers"], key=lambda racer: racer.distance)
    winner_message = f"The winner is {winner.name}!"
    await interaction.followup.send(content=winner_message)
    return winner


async def distribute_winnings(interaction, winner, amount_of_racers):
    player_winnings = {}
    for bet in data.race_games[interaction.channel_id].get("bets", []):
        player_winnings[bet["player"]] = 0
    for bet in data.race_games[interaction.channel_id].get("bets", []):
        if bet["racer_to_bet_on"].strip().lower().split(" ")[0] == winner.name.strip().lower().split(" ")[0]:
            player_winnings[bet["player"]] += bet["bet_amount"] * (amount_of_racers - 1)
        else:
            player_winnings[bet["player"]] -= bet["bet_amount"]

    for player, amount in player_winnings.items():
        if amount > 0:
            await interaction.followup.send(f"{player.name} won ${amount}!")
        elif amount < 0:
            await interaction.followup.send(f"{player.name} lost ${-amount}!")
    for player, amount in player_winnings.items():
        data.players[player].money += amount


async def setup(client: commands.Bot) -> None:
    await client.add_cog(RaceGame(client))
