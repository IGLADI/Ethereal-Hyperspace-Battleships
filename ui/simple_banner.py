import discord


class SimpleBanner(discord.ui.View):
    def __init__(self, text: str, user: discord.Member, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text
        self.user = user

        self.embed = discord.Embed(description=self.text, color=discord.Color.green())
        self.embed.set_author(name=f" |  {self.user.display_name}", icon_url=self.user.avatar.url)
