import discord


class SimpleBanner(discord.ui.View):
    def __init__(
        self,
        text: str,
        user: discord.Member,
        color=discord.Color.green(),
        extra_header="",
        is_code_block=False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.text = text
        if is_code_block:
            self.text = f"```{self.text}```"
        self.user = user
        self.color = color
        self.extra_header = extra_header

        self.embed = discord.Embed(description=self.text, color=self.color)
        self.embed.set_author(name=f" |  {self.user.display_name}{self.extra_header}", icon_url=self.user.avatar.url)
