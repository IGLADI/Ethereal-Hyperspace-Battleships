import discord


class SimpleBanner(discord.ui.View):
    def __init__(self, text: str, user: discord.Member, color=discord.Color.green(), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text
        self.user = user
        self.color = color

        self.embed = discord.Embed(description=self.text, color=self.color)
        self.embed.set_author(name=f" |  {self.user.display_name}", icon_url=self.user.avatar.url)
