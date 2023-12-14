import data
import discord


async def create_roles(guild: discord.Guild):
    for guild_temp in data.guilds:
        if not discord.utils.get(guild.roles, name=guild_temp.name):
            await guild.create_role(name=guild_temp.name)
        if not discord.utils.get(guild.roles, name=f"{guild_temp.name} officer"):
            await guild.create_role(name=f"{guild_temp.name} officer")
