import discord
from discord.ext import commands
import config
from discord.utils import get
import youtube_dl
import os

client = commands.Bot( command_prefix = config.COMMAND_PREFIX)

@client.remove_command('help')

@client.event
async def on_ready():
    print('Ready')
@client.event
async def on_message(message):
    await client.process_commands(message)

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
# RUN
client.run(config.TOKEN)
