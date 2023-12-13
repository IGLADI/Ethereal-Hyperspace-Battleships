import discord
import data


def create_category_if_not_exists(func):
    async def wrapper(guild: discord.Guild, name: str):
        category = discord.utils.get(guild.categories, name=name)
        if not category:
            await guild.create_category(name)
        await func(guild, name)

    return wrapper


async def create_channels(guild: discord.Guild):
    await create_category_general(guild, "Ethereal Hyperspace Battleships General")

    for guild_temp in data.guilds:
        # have put guild_temp.name by guess because guilds are developed in the same time, should be checked
        await create_category_main_guilds(guild, guild_temp.name)


@create_category_if_not_exists
async def create_category_general(guild: discord.Guild, name: str):
    general_category = discord.utils.get(guild.categories, name=name)
    if general_category:
        if not discord.utils.get(general_category.text_channels, name="general"):
            await general_category.create_text_channel("general", position=1)
        # TODO add a announcements channel, store it in the DB to send news

        if not discord.utils.get(general_category.forums, name="questions"):
            await general_category.create_forum("questions", position=2)

        if not discord.utils.get(general_category.voice_channels, name="general"):
            await general_category.create_voice_channel("general", position=3)


@create_category_if_not_exists
async def create_category_main_guilds(guild: discord.Guild, name: str):
    guild_category = discord.utils.get(guild.categories, name=name)
    if guild_category:
        if not discord.utils.get(guild_category.text_channels, name="announcements"):
            await guild_category.create_text_channel("announcements")
        if not discord.utils.get(guild_category.text_channels, name="general"):
            await guild_category.create_text_channel("general")
        if not discord.utils.get(guild_category.text_channels, name="off-topic"):
            await guild_category.create_text_channel("off-topic")

        if not discord.utils.get(guild_category.forums, name="guides"):
            await guild_category.create_forum("guides")

        if not discord.utils.get(guild_category.voice_channels, name="quarters"):
            await guild_category.create_voice_channel("quarters")

        if not discord.utils.get(guild_category.stage_channels, name="meeting room"):
            await guild_category.create_stage_channel("meeting room")
