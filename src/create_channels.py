import discord
import data


# TODO delete them first to prevent problems
def create_category_if_not_exists(func):
    async def wrapper(guild: discord.Guild, name: str):
        category = discord.utils.get(guild.categories, name=name)
        if not category:
            await guild.create_category(name)
        await func(guild, name)

    return wrapper


async def create_channels(guild: discord.Guild):
    await create_category_general(guild, "Ethereal Hyperspace Battleships General")

    for guild_temp_name in data.guild_names:
        # ! have put guild_temp_name by guess because guilds are developed in the same time, should be checked
        await create_category_main_guilds(guild, guild_temp_name)


@create_category_if_not_exists
async def create_category_general(guild: discord.Guild, name: str):
    general_category = discord.utils.get(guild.categories, name=name)

    for channel in data.general_channels:
        await create_channel(general_category, channel)


@create_category_if_not_exists
async def create_category_main_guilds(guild: discord.Guild, name: str):
    guild_category = discord.utils.get(guild.categories, name=name)
    await guild_category.set_permissions(guild.default_role, read_messages=False)
    guild_role = discord.utils.get(guild.roles, name=name)
    await guild_category.set_permissions(guild_role, read_messages=True)

    if guild_category:
        for channel in data.guild_channels:
            await create_channel(guild_category, channel)


async def create_channel(category, channel):
    match channel["type"]:
        case "text":
            if not discord.utils.get(category.text_channels, name=channel["name"]):
                await category.create_text_channel(channel["name"])
        case "forum":
            if not discord.utils.get(category.forums, name=channel["name"]):
                await category.create_forum(channel["name"])
        case "voice":
            if not discord.utils.get(category.voice_channels, name=channel["name"]):
                await category.create_voice_channel(channel["name"])
        case "stage":
            # ? maybe lock the stage channels to the guild officers
            if not discord.utils.get(category.stage_channels, name=channel["name"]):
                await category.create_stage_channel(channel["name"])
