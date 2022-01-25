import discord
from discord.ext import commands
from discord.utils import get
from discord import Activity, ActivityType
import youtube_dl
import os
import time
import datetime
import qrcode
from random import randint
from gtts import gTTS
import json
import asyncio
# from selenium import webdriver
from threading import Thread

import config

# VARIABLES
# global member_count
# member_count = 0


# Bot

client = commands.Bot(command_prefix = config.COMMAND_PREFIX)
# web = webdriver.Chrome('./chromedriver.exe')

@client.remove_command('help')

# def youtube_parser():
#     while True:
#         web.get('https://www.youtube.com/channel/UCMLajX5RcAKB1N3sRELMA2g/videos')

#         videos = web.find_elements_by_id('video-title')
#         for i in range(len(videos)):
#             print(videos[i].get_attribute('href'))

#         # web.quit()
#         time.sleep(5)

# Thread(target = youtube_parser).start()

@client.event
async def on_ready():
    # await client.create_invite(max_age = 0, max_uses = 0, unique = True, reason = None, destination = )
    print('ready')
    await client.change_presence(status = discord.Status.idle, activity = Activity(name = 'ютуб', type = ActivityType.watching, url = 'https://youtube.com'))
    for g in client.guilds:
        if g.id == 716892499779518475:
            channel = g.get_channel(767265780773421088)
            member_count = g.member_count
            # print(g.member_count)
            await channel.edit(name = f'На сервере {member_count} пользователей', bitrate = 8000, user_limit = 1, sync_permissions = True)

    await youtube_parser()

@client.event
async def on_member_join(member):
    # await member.send('Hello NewServer')
    channel = client.get_channel(767265780773421088)
    member_count += 1
    await channel.edit(name = f'На сервере {member_count} пользователей', bitrate = 8000, user_limit = 1, sync_permissions = True)
@client.event
async def on_member_remove(member):
    ch = client.get_channel(765541973997912064)
    await ch.send(f"{member.name}#{member.discriminator} покинул сервер")
    channel = client.get_channel(767265780773421088)
    member_count += 1
    await channel.edit(name = f'На сервере {member_count} пользователей', bitrate = 8000, user_limit = 1, sync_permissions = True)
@client.event
async def on_message(message):
    await client.process_commands(message)
    # rand reaction
    rand = randint(1, 10)
    if rand == 1:
        await message.add_reaction("▶")
    # bad words
    # print(message)
    for mess in config.BAD_WORDS:
        if mess in message.content:
            await message.delete()
            await message.channel.send('Не пиши плохие слова!')
    # lvl
    if message.author != client.user:
        with open('lvls.json', 'r') as f:
            users = json.load(f)

        async def update_data(users, user):
            if not user in users:
                users[user] = {}
                users[user]['exp'] = 0
                users[user]['lvl'] = 1
        await update_data(users, str(message.author.id))
        async def add_exp(users, user, exp):
            users[user]['exp'] += exp
        await add_exp(users, str(message.author.id), 0.1)
        async def add_lvl(users, user):
            exp = users[user]['exp']
            lvl = users[user]['lvl']
            if exp > lvl:
                lvl += 1
                users[user]['lvl'] = lvl
                users[user]['exp'] = 0
                await message.channel.send(f'{message.author.name}#{message.author.discriminator} у тебя уже {lvl} уровень!:partying_face:')
        await add_lvl(users, str(message.author.id))
        with open('lvls.json', 'w') as f:
            json.dump(users, f)
# @client.event
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.MissingPermissions):
#         await ctx.send(f"{ctx.author.name} у вас нет прав на использование команды!")
#     if isinstance(error, commands.CommandNotFound):
#         await ctx.send(f"{ctx.author.name} такой команды не существует! Наберите {config.COMMAND_PREFIX}help")
#     if isinstance(error, commands.MissingRequiredArgument):
#         await ctx.send(f"{ctx.author.name} не все аргументы! Попробуйте {ctx.command.usage}")
@client.event
async def on_raw_reaction_remove(payload):
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    member = get(message.guild.members, id=payload.user_id)
    if member.id == 738798948696719392:
        return
    try:
        emoji = str(payload.emoji)
        role = get(message.guild.roles, id=config.ROLES[emoji])
        await member.remove_roles(role)
    except KeyError as e:
        print('[EROR] KeyError, no role found for ' + emoji)
        return
@client.event
async def on_raw_reaction_add(payload):
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    member = get(message.guild.members, id=payload.user_id)
    if member.id == 738798948696719392:
        return False
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
        return

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
    await ctx.message.delete()
    emb = discord.Embed(title = 'Help')
    emb.add_field(name = f'{config.COMMAND_PREFIX}clear (Только для админов)', value = 'Очистка чата')
    emb.add_field(name = f'{config.COMMAND_PREFIX}qr', value = 'Создание qr кода')
    emb.add_field(name = f'{config.COMMAND_PREFIX}say', value = 'Содать аудиофайл с голосом')
    emb.add_field(name = f'{config.COMMAND_PREFIX}join', value = 'Подключение бота к голосовому каналу')
    emb.add_field(name = f'{config.COMMAND_PREFIX}leave', value = 'Отключение бота от голосового канала')
    emb.add_field(name = f'{config.COMMAND_PREFIX}members', value = 'Показать всех учасников сервера')
    emb.add_field(name = f'{config.COMMAND_PREFIX}ci', value = 'Создание приглашения на сервер')
    emb.add_field(name = f'{config.COMMAND_PREFIX}time', value = 'Посмотреть текущее время')
    await ctx.channel.send(embed = emb)
@client.command(usage = f'{config.COMMAND_PREFIX}play <youtube video url>')
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
@client.command()
async def members(ctx):
    m = ctx.guild.members
    count = 0
    for member in m:
        await ctx.send(member.name)
        count += 1
    await ctx.send(count)
@client.command()
async def qr(ctx, *, data):
    img = qrcode.make(data)
    img.save('files/qr-code.png')

    await ctx.send(file = discord.File(fp = 'files/qr-code.png'))
@client.command()
async def say(ctx, langg, *, data):
    song_there = os.path.isfile('text.mp3')
    try:
        if song_there:
            os.remove('files/text.mp3')
            print('[log] Старый файл удален!')
    except PermissionError:
        print('[log] Не удалось удалить файл!')
    voice = get(client.voice_clients, guild = ctx.guild)

    tts = gTTS(text = data, lang = langg)
    tts.save("files/text.mp3")

    await ctx.send(file = discord.File(fp = 'files/text.mp3'))
@client.command()
async def time(ctx):
    emb = discord.Embed(title = "Time", colour = discord.Color.green())
    now = datetime.datetime.now()
    emb.set_author(name = client.user.name, icon_url = client.user.avatar_url)
    emb.set_footer(text = ctx.author.name, icon_url = ctx.author.avatar_url)
    emb.add_field(name = 'Текущее время', value = f'{now.hour}:{now.minute}:{now.second}')
    emb.set_thumbnail(url = 'https://greenlanddv.ru/kernel/preview.php?file=shop/goods/10627-1.jpg&width=300&height=300&method=add')
    await ctx.channel.send(embed = emb)

# ECONOMIC
queue = []
@client.command()
async def surprize(ctx):
    with open("economic.json", "r") as file:
        money = json.load(file)

    if not str(ctx.author.id) in money:
        money[str(ctx.author.id)] = {}
        money[str(ctx.author.id)]['Money'] = 0

    if not str(ctx.author.id) in queue:
        money[str(ctx.author.id)]['Money'] += 1250
        await ctx.send(f"{ctx.author} вы получили свои 1250 монет")
        queue.append(str(ctx.author.id))
        with open("economic.json", "w") as file:
            json.dump(money, file)
        await asyncio.sleep(30)
        queue.remove(str(ctx.author.id))

    if str(ctx.author.id) in queue:
        await ctx.send(f"{ctx.author} ты уже получил монеты!")


@client.command()
async def balance(ctx, member:discord.Member = None):
    if member == ctx.author or member == None:
        with open("economic.json", "r") as file:
            money = json.load(file)

        await ctx.send(f'У {ctx.author} {money[str(ctx.author.id)]["Money"]} монет')
    else:
        with open("economic.json", "r") as file:
            money = json.load(file)

        await ctx.send(f'У *{member}* {money[str(member.id)]["Money"]} монет')

@client.command()
async def addtoshop(ctx, role: discord.Role, cost:int):
    with open("economic.json", "r") as file:
        money = json.load(file)

    if str(role.id) in money['shop']:
        await ctx.send("Эта роль уже есть в магазине!")
    elif not str(role.id) in money['shop']:
        money['shop'][str(role.id)] = {}
        money['shop'][str(role.id)]['Cost'] = cost
        money['shop'][str(role.id)]['ID'] = role.id
        await ctx.send("Роль добавлена в магазин")
    with open("economic.json", "w") as file:
        json.dump(money, file)

@client.command()
async def shop(ctx):
    with open('economic.json') as file:
        money = json.load(file)
    emb = discord.Embed(title = 'Магазин', colour = discord.Color.green())
    for role in money['shop']:
        # role = get(ctx.guild.roles, id = role_info['ID'])
        # print(ctx.message.guild.roles)
        # print(roleid)
        # print(role)
        emb.add_field(name = f'Цена: {money["shop"][role]["Cost"]}', value = f'<@&{role}>', inline = False)
    await ctx.send(embed = emb)

@client.command()
async def buy(ctx, role: discord.Role):
    with open('economic.json', 'r') as f:
        money = json.load(f)

    if str(role.id) in money['shop']:
        if money['shop'][str(role.id)]['Cost'] <= money[str(ctx.author.id)]['Money']:
            if not role in ctx.author.roles:
                for i in money['shop']:
                    if i == str(role.id):
                        buy = get(ctx.guild.roles, id = int(i))
                        await ctx.author.add_roles(buy)
                        money[str(ctx.author.id)]['Money'] -= money['shop'][str(role.id)]['Cost']
                        await ctx.send('Вы купили роль 😁!')
            else:
                await ctx.send('У вас уже есть роль 😠!!!')

    with open("economic.json", "w") as file:
        json.dump(money, file)

@client.command()
async def sell(ctx, role: discord.Role):
    with open('economic.json', 'r') as f:
        money = json.load(f)

    if role in ctx.author.roles:
        if str(role.id) in money['shop']:
            for i in money['shop']:
                if i == str(role.id):
                    buy = get(ctx.guild.roles, id = int(i))
                    await ctx.author.remove_roles(buy)
                    money[str(ctx.author.id)]['Money'] += money['shop'][str(role.id)]['Cost']
                    await ctx.send('Вы продали роль 😉!')
        else:
            await ctx.send('У вас нет роли 😒')

@client.command()
async def off(ctx):
    exit()

# async def youtube_parser():
#     web.get('https://www.youtube.com/channel/UCMLajX5RcAKB1N3sRELMA2g/videos')

#     videos = web.find_elements_by_id('video-title')
#     for i in range(len(videos)):
#         print(videos[i].get_attribute('href'))

#     web.quit()
#     await asyncio.sleep(0.1)
#     await youtube_parser()

# youtube_parser()

# RUN
if __name__ == '__main__':
    client.run(config.TOKEN)
