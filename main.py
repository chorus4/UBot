import discord
from discord.ext import commands
import config

client = commands.Bot( command_prefix = config.COMMAND_PREFIX)

@client.event
async def on_ready():
    print('Connected')

@client.command()
@commands.has_permissions(administrator = True)
async def kick(ctx, member: discord.Member, *, reason = None):
    await ctx.channel.purge(limit=1)
    await member.kick(reason = reason)

# RUN
client.run(config.TOKEN)
