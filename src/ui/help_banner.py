import discord
from tabulate import tabulate

from ui.simple_banner import NormalBanner


def help_guild():
    return {
        "title": "Guild Commands",
        "guild": "Get guild info",
        "guild_members": "Get guild members",
        "guild_leave": "Leave your guild",
        "guild_join {guild name}": "Join a guild",
        "guild_create {guild name}": "Create a guild",
    }


def help_resources():
    return {
        "title": "Resource Commands",
        "resources": "Get info on resources and mining",
        "mine": "Mine a random resource",
        "inventory": "Check your cargo",
        "sell {resource} {amount}": "Sell resources",
        "buy {resource} {amount}": "Buy resources",
    }


def help_travel():
    return {
        "title": "Travel Commands",
        "where_am_i": "Get your location info",
        "travel {x} {y}": "Travel to a location",
        "scan": "Scan the area for players and locations",
    }


def help_economic():
    return {
        "title": "Economic Commands",
        "balance": "Check your money",
        "pay {amount} {player}": "Give money to a player",
        "trade": "idk, i didn't write this...",
    }


def help_commands():
    return [
        {"help_guild": help_guild()},
        {"help_resources": help_resources()},
        {"help_travel": help_travel()},
        {"help_economic": help_economic()},
    ]


class HelpSelect(discord.ui.Select):
    def __init__(self):
        options = []

        help_options = [list(help_command.keys())[0] for help_command in help_commands()]

        for help_option in help_options:
            options.append(discord.SelectOption(label=help_option, value=help_option))

        super().__init__(
            placeholder="Select a category",
            max_values=1,
            min_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        selected_option = self.values[0]
        new_commands_help = {}

        for help_command in help_commands():
            if selected_option in help_command:
                new_commands_help = help_command[selected_option]
                break

        new_commands_help = {f"/{key}": value for key, value in new_commands_help.items() if key != "title"}
        # TODO set a custom title per menu

        self.table = tabulate(
            new_commands_help.items(),
            headers=["Command", "Description"],
        )

        banner = NormalBanner(text=f"```{self.table}```", user=interaction.user)
        await interaction.response.edit_message(embed=banner.embed)


class HelpBanner(NormalBanner):
    def __init__(self, user: discord.Member, *args, **kwargs):
        super().__init__(
            user=user,
            title="Choose a Category",
            *args,
            **kwargs,
        )
        self.add_item(HelpSelect())
        self.user = user

        self.embed.add_field(
            name="How to use",
            value="Select a category from the dropdown menu to see the commands in that category.",
        )
