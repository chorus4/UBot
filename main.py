import discord
from discord.ext import commands
from discord.utils import get
from discord import Activity, ActivityType
import youtube_dl
import os

import config

# Bot

client = commands.Bot( command_prefix = config.COMMAND_PREFIX)

@client.remove_command('help')

@client.event
async def on_ready():
    print('ready')
    # await client.create_invite(max_age = 0, max_uses = 0, unique = True, reason = None, destination = )
    await client.change_presence(status = discord.Status.idle, activity = Activity(name = 'ютуб', type = ActivityType.watching))

@client.event
async def on_message(message):
    await client.process_commands(message)
@client.event
async def on_raw_reaction_remove(payload):
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    member = get(message.guild.members, id=payload.user_id)
    try:
        emoji = str(payload.emoji)
        role = get(message.guild.roles, id=config.ROLES[emoji])
        await member.remove_roles(role)
    except KeyError as e:
        print('[EROR] KeyError, no role found for ' + emoji)
@client.event
async def on_raw_reaction_add(payload):
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    member = get(message.guild.members, id=payload.user_id)
    try:
        emoji = str(payload.emoji)
        role = get(message.guild.roles, id=config.ROLES[emoji])
        if(len([i for i in member.roles if i.id not in config.EXCROLES]) <= config.MAX_ROLES_PER_USER):
            await member.add_roles(role)
            print('[SUCCESS] User {0.display_name} has been granted with role {1.name}'.format(member, role))
        else:
            await message.remove_reaction(payload.emoji, member)
            print('[ERROR] Too many roles for user {0.display_name}'.format(member))
    except KeyError as e:
        print('[EROR] KeyError, no role found for ' + emoji)

@client.command()
async def ci(ctx):
    i = await ctx.channel.create_invite(max_age = 0, max_uses = 0, unique = True, reason = None, destination = ctx.message.channel)
    await ctx.send(i)

@client.command()
@commands.has_permissions(administrator = True)
async def kick(ctx, member: discord.Member, *, reason = None):
    await ctx.message.delete()
    await ctx.channel.send(f'{ctx.author.mention} выгнал {member.mention}')
    await member.kick(reason = reason)
@client.command()
@commands.has_permissions(administrator = True)
async def ban(ctx, member: discord.Member, *, reason = None):
    await ctx.message.delete()
    await ctx.channel.send(f'{ctx.author.mention} забанил {member.mention}, причина: {reason}')
    await member.ban(reason = reason)
@client.command()
@commands.has_permissions(administrator = True)
async def unban(ctx, *, member: discord.Member):
    await ctx.message.delete()

    banned = await ctx.guild.bans()
    author = ctx.author.mention
    for entry in banned:
        user = entry.user
        user = user.mention
        if user == member:
            await ctx.guild.unban(user)
            await ctx.channel.send(f'{ctx.author.mention} разбанил {member.mention}')
            break
@client.command()
@commands.has_permissions(administrator = True)
async def clear(ctx, limit = 9999999999):
    await ctx.channel.purge(limit = limit)
@client.command()
async def join(ctx):
    await ctx.message.delete()

    global voice
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild = ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        await ctx.send(f'Бот присоединился к каналу: {channel}')
@client.command()
async def leave(ctx):
    await ctx.message.delete()

    song_there = os.path.isfile('song.mp3')
    try:
        if song_there:
            os.remove('song.mp3')
            print('[log] Старый файл удален!')
    except PermissionError:
        print('[log] Не удалось удалить файл!')
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild = ctx.guild)
    if voice and voice.is_connected():
        await ctx.send(f'Бот покинул канал: {channel}')
        await voice.disconnect()
    else:
        voice = await channel.connect()
        await ctx.send(f'Бот покинул канал: {channel}')
@client.command()
async def help(ctx):
    ctx.message.delete()
    emb = discord.Embed(title = 'Help')
    emb.add_field(name = f'{config.COMMAND_PREFIX}clear (Только для админов)', value = 'Очистка чата')
    await ctx.channel.send(embed = emb)
@client.command()
async def play(ctx, url: str):
    song_there = os.path.isfile('song.mp3')
    try:
        if song_there:
            os.remove('song.mp3')
            print('[log] Старый файл удален!')
    except PermissionError:
        print('[log] Не удалось удалить файл!')
    await ctx.channel.send('Пожалуйста жтите')
    voice = get(client.voice_clients, guild = ctx.guild)
    ydl_op = {
        'format': 'bestaudio/besst',
        'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
        }],
    }
    with youtube_dl.YoutubeDL(ydl_op) as ydl:
        ydl.download([url])
    for file in os.listdir('./'):
        if file.endswith('.mp3'):
            name = file
            os.rename(file, 'song.mp3')
    voice.play(discord.FFmpegPCMAudio('song.mp3'))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07
    nname = name.rsplit('-', 2)
    await ctx.send(f'Сейчас играет: {nname[0]}')

@client.event
async def on_voice_state_update(member, before, after):
    if after != None:
        if after.channel.id == 763803948742082570:
            for guild in client.guilds:
                maincategory = get(guild.categories, id=763804505409978399)
                channel2 = await guild.create_voice_channel(name = f'Канал {member.display_name}', category = maincategory)
                await channel2.set_permissions(member, connect = True, mute_members = True, manage_channels = True)
                await member.move_to(channel2)
                def check(x, y, z):
                    return len(channel2.members) == 0
                await client.wait_for('voice_state_update', check = check)
                await channel2.delete()


print(client)
# RUN
client.run(config.TOKEN)
