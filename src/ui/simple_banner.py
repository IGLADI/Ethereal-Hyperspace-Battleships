import discord
import discord_colorize


class SimpleBanner(discord.ui.View):
    def __init__(
        self,
        user: discord.Member,
        text: str = "",
        color=discord.Color.light_gray(),
        remove_header=False,
        extra_header="",
        is_code_block=False,
        text_color=None,
        title=None,
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

        self.embed = discord.Embed(description=self.text, color=self.color, title=title)
        if remove_header:
            self.embed.set_author(name=f"{self.extra_header}", icon_url=self.user.avatar.url)
        else:
            self.embed.set_author(
                name=f" |  {self.user.display_name}{self.extra_header}", icon_url=self.user.avatar.url
            )


class ErrorBanner(SimpleBanner):
    def __init__(self, user: discord.Member, text: str = "", *args, **kwargs):
        super().__init__(user, text, color=discord.Color.red(), text_color="red", *args, **kwargs)


class NormalBanner(SimpleBanner):
    def __init__(self, user: discord.Member, text: str = "", *args, **kwargs):
        super().__init__(user, text, *args, **kwargs)


class LoadingBanner(SimpleBanner):
    def __init__(self, user: discord.Member, text: str = "", *args, **kwargs):
        super().__init__(user, text, color=discord.Color.orange(), *args, **kwargs)


class SuccessBanner(SimpleBanner):
    def __init__(self, user: discord.Member, text: str = "", *args, **kwargs):
        super().__init__(user, text, color=discord.Color.green(), *args, **kwargs)
