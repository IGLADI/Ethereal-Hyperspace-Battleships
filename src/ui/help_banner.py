import discord

from tabulate import tabulate


class HelpBanner(discord.ui.View):
    def __init__(self, commands: dict, user: discord.Member, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commands = commands
        self.user = user

        commands_data = []
        for command, description in self.commands.items():
            commands_data += [[f"/{command}", description]]
        
        self.table = tabulate(commands_data, headers=['Command', 'Description'])


        self.embed = discord.Embed(description=f"```{self.table}```", color=discord.Color.light_gray())
        self.embed.set_author(name=f" |  {self.user.display_name}", icon_url=self.user.avatar.url)
