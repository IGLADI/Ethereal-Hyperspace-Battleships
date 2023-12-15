import discord
import random



# Define a function to initiate a vote
def initiate_vote(message, building_name):
    # Send a notification to the 'announcements' channel
    announcements_channel = client.get_channel(announcements_channel_id)
    announcement = f"An officer has initiated a vote to create a new build: {building_name}"
    announcements_channel.send(announcement)

    # Track yes and no votes
    yes_votes = 0
    no_votes = 0

    # Notify players to vote
    for member in message.guild.members:
        if member.bot:
            continue

        vote_message = f"**Vote:** Should we create the new build '{building_name}'?"
        action_button = discord.ActionRow([
            discord.Button(
                emoji='✅',
                style=discord.ButtonStyle.success,
                label='Yes',
                on_click=lambda: cast_vote('yes')
            ),
            discord.Button(
                emoji='❌',
                style=discord.ButtonStyle.danger,
                label='No',
                on_click=lambda: cast_vote('no')
            )
        ])

        vote_embed = discord.Embed(
            title=f"Vote for {building_name}",
            description=vote_message,
            colour=discord.Color.blue
        )
        vote_embed.add_field(name='**Results:**', value=f'{yes_votes} yes, {no_votes} no')
        vote_embed.set_footer(text=f'Cast your vote until {vote_time} seconds from now')
        vote_embed.set_timestamp(seconds=time.time())

        vote_message = await member.send(embed=vote_embed, components=[action_button])

        # Cancel the vote after the specified time
        await asyncio.sleep(vote_time)
        await vote_message.delete()

        # Announce the vote results
        if yes_votes > no_votes:
            announcement = f"The vote to create the new build '{building_name}' has passed!"
        elif yes_votes < no_votes:
            announcement = f"The vote to create the new build '{building_name}' has failed."
        else:
            announcement = f"The vote to create the new build '{building_name}' has tied. It will not be created."

        announcements_channel.send(announcement)

# Define a function to cast a vote
def cast_vote(vote_type):
    if vote_type == 'yes':
        global yes_votes
        yes_votes += 1
    elif vote_type == 'no':
        global no_votes
        no_votes += 1
    else:
        raise ValueError("Invalid vote type")

