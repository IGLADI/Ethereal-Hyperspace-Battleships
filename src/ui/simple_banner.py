import discord
import discord_colorize


class SimpleBanner(discord.ui.View):
    def __init__(
        self,
        text: str,
        user: discord.Member,
        color=discord.Color.light_gray(),
        extra_header="",
        is_code_block=False,
        text_color=None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if text_color is not None:
            colors = discord_colorize.Colors()
            self.text = f"```ansi\n{colors.colorize(f'{text}', fg=text_color)}```"
        else:
            self.text = text
        if is_code_block:
            self.text = f"```{self.text}```"

        self.user = user
        self.color = color
        self.extra_header = extra_header

        self.embed = discord.Embed(description=self.text, color=self.color)
        self.embed.set_author(name=f" |  {self.user.display_name}{self.extra_header}", icon_url=self.user.avatar.url)


class ErrorBanner(SimpleBanner):
    def __init__(self, text: str, user: discord.Member, *args, **kwargs):
        super().__init__(text, user, color=discord.Color.red(), text_color="red", *args, **kwargs)


class NormalBanner(SimpleBanner):
    def __init__(self, text: str, user: discord.Member, *args, **kwargs):
        super().__init__(text, user, *args, **kwargs)


class LoadingBanner(SimpleBanner):
    def __init__(self, text: str, user: discord.Member, *args, **kwargs):
        super().__init__(text, user, color=discord.Color.orange(), *args, **kwargs)


class SuccessBanner(SimpleBanner):
    def __init__(self, text: str, user: discord.Member, *args, **kwargs):
        super().__init__(text, user, color=discord.Color.green(), *args, **kwargs)
