import data
import discord

# TODO delete them first to prevent problems
async def create_roles(guild: discord.Guild):
    for guild_name in data.guild_names:
        if not discord.utils.get(guild.roles, name=guild_name):
            await guild.create_role(name=guild_name)
        if not discord.utils.get(guild.roles, name=f"{guild_name} officer"):
            await guild.create_role(name=f"{guild_name} officer")
