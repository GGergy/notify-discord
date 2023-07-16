import discord
from discord_bot.utils import sqlast_hope, music_api, config, yt_api
from discord.ext import commands
from discord.ui import Button

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='.', intents=intents)


@bot.event
async def on_guild_join(guild):
    sqlast_hope.create_server(guild.id)
    if guild.text_channels:
        await guild.text_channels[0].send(f'Привет, я музыкальный бот от gt3rsgy.'
                                          f' Напишите {bot.command_prefix}commands, чтобы узнать больше')


@bot.event
async def on_ready():
    print(f'Successful initialized')


@bot.command(name='play')
async def call_play(ctx):
    server, session = sqlast_hope.server(ctx.message.author.guild.id)
    q = server.get_queue()
    session.close()
    if not ctx.author.voice:
        await ctx.reply(f'Похоже, вы не в голосовом канале')
        return
    if not q:
        await ctx.reply(f'Похоже, очередь на этом сервере закончилась, используйте {bot.command_prefix}search')
        return
    await begin_play(author=ctx.message.author)
    await ctx.reply(f'Воспроизводится очередь этого сервера, введите {bot.command_prefix}review,'
                    f' чтобы узнать подробности')
    return


@bot.command(name='search')
async def search(ctx):
    if ctx.message.content.strip().count(' ') == 0:
        await ctx.reply('Похоже, вы не ввели поисковый запрос')
        return
    data = ctx.message.content[ctx.message.content.find(' ') + 1:].strip()
    res = music_api.search(data)
    view = discord.ui.View()
    for item in res:
        b = await generate_track_button(item)
        view.add_item(b)
    await ctx.reply('Вот что я нашел', view=view)


@bot.command(name='search_yt')
async def search_yt(ctx):
    if ctx.message.content.strip().count(' ') == 0:
        await ctx.reply('Похоже, вы не ввели поисковый запрос')
        return
    data = ctx.message.content[ctx.message.content.find(' ') + 1:].strip()
    res = yt_api.search(data)
    view = discord.ui.View()
    for item in res:
        b = await generate_track_button(item)
        view.add_item(b)
    await ctx.reply('Вот что я нашел', view=view)


async def generate_track_button(item):
    b = Button(label=item['name'])

    async def button_callback(interaction):
        b_play = Button(label='Играть сейчас')
        view = discord.ui.View()

        async def b_play_callback(interaction_):
            server, session = sqlast_hope.server(interaction_.user.guild.id)
            q = server.get_queue()
            q.insert(0, item['id'])
            server.pack_queue(q)
            session.commit()
            session.close()

            await interaction_.response.send_message(f'Включаю {item["name"]}')
            await begin_play(interaction_.user)

        b_play.callback = b_play_callback
        view.add_item(b_play)

        b_queue = Button(label='Добавить в очередь')

        async def b_queue_callback(interaction_):
            server, session = sqlast_hope.server(interaction_.user.guild.id)
            q = server.get_queue()
            q.append(item['id'])
            server.pack_queue(q)
            session.commit()
            session.close()

            await interaction_.response.send_message(f'{item["name"]} добавлено в очередь')

        b_queue.callback = b_queue_callback
        view.add_item(b_queue)

        b_next = Button(label='Слушать далее')

        async def b_next_callback(interaction_):
            server, session = sqlast_hope.server(interaction_.user.guild.id)
            q = server.get_queue()
            q.insert(0, item['id'])
            server.pack_queue(q)
            session.commit()
            session.close()
            await interaction_.response.send_message(f'{item["name"]} будет проиграно следующим')

        b_next.callback = b_next_callback
        view.add_item(b_next)

        await interaction.response.send_message(f'Выбран трек: {item["name"]}', view=view, ephemeral=True)

    b.callback = button_callback
    return b


async def begin_play(author):
    server, session = sqlast_hope.server(author.guild.id)
    q = server.get_queue()
    if not q:
        return
    if not author.guild.voice_client:
        if not author.voice:
            return
        await author.voice.channel.connect()
    else:
        author.guild.voice_client.stop()
    static_begin_play(author)
    session.close()


def static_begin_play(author):
    author.guild.voice_client.stop()
    server, session = sqlast_hope.server(author.guild.id)
    q = server.get_queue()
    if not q:
        server.now = 0
        return
    vc = author.guild.voice_client
    server.now = q[0]
    track = str(q[0])
    if track.isdigit():
        source = music_api.get_link(int(track))
        options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    else:
        source = False
        while q and not source:
            source = yt_api.get_link(track)
            if not source:
                q.pop(0)
        if not source:
            server.pack_queue(q)
            session.commit()
            session.close()
            return
        options = {'options': '-vn'}
    ff = discord.FFmpegPCMAudio(executable="discord_bot/assets/bin/ffmpeg.exe", source=source,
                                **options)
    q.pop(0)
    server.pack_queue(q)
    session.commit()
    session.close()
    vc.play(ff, after=lambda arg: static_begin_play(author))


@bot.command(name='pause')
async def pause(ctx):
    if ctx.message.guild.voice_client and sqlast_hope.server(ctx.message.author.guild.id)[0].now:
        ctx.message.guild.voice_client.pause()
        await ctx.reply(f'Пауза.. Введите {bot.command_prefix}resume, чтобы продолжить')
        return
    await ctx.reply(f'Похоже, ничего не играет')


@bot.command(name='resume')
async def resume(ctx):
    if ctx.message.guild.voice_client and sqlast_hope.server(ctx.message.author.guild.id)[0].now:
        ctx.message.guild.voice_client.resume()
        await ctx.reply(f'Продолжаю воспроизводить')
        return
    await ctx.reply(f'Похоже, ничего не играет')


@bot.command(name='stop')
async def stop(ctx):
    if ctx.message.guild.voice_client:
        ctx.message.guild.voice_client.stop()
        await ctx.message.guild.voice_client.disconnect()
    server, session = sqlast_hope.server(ctx.message.author.guild.id)
    server.queue = '{"queue": []}'
    server.now = 0
    session.commit()
    session.close()
    await ctx.reply(f'Воспроизведение полностью остановлено, очередь очищена')


@bot.command(name='next')
async def next_track(ctx):
    server, session = sqlast_hope.server(ctx.message.author.guild.id)
    q = server.get_queue()
    if not q:
        await ctx.reply(f'Похоже, очередь на этом сервере закончилась, используйте {bot.command_prefix}search')
        return
    session.close()
    await ctx.reply(f'Переключаю на {music_api.get_metadata(q[0])}')
    await begin_play(ctx.message.author)


@bot.command(name='review')
async def review(ctx):
    server, session = sqlast_hope.server(ctx.message.author.guild.id)
    q = server.get_queue()
    if not q and not server.now:
        await ctx.reply(f'Похоже, очередь на этом сервере закончилась, используйте {bot.command_prefix}search')
        return
    embed = discord.Embed(title=f'Очередь сервера {ctx.guild}', color=0xa35de0,
                          description=(f"```Сейчас играет: {music_api.get_metadata(server.now)}```"
                                       if server.now else "") + "\n".join([f'{index + 2}. {music_api.get_metadata(i)}'
                                                                           for index, i in enumerate(q)]))
    session.close()
    await ctx.reply(embed=embed)


@bot.command(name='now')
async def now(ctx):
    server, session = sqlast_hope.server(ctx.message.author.guild.id)
    if not server.now:
        await ctx.reply(f'Похоже, сейчас ничего не играет')
        return
    session.close()
    await ctx.reply(f"Сейчас играет: {music_api.get_metadata(server.now)}")


@bot.command(name='commands', help='write this to seen commands')
async def commands(ctx):
    p = bot.command_prefix
    embed = discord.Embed(colour=0xa35de0, title='Команды этого бота',
                          description=f'{p}search (запрос) - поиск песен по названию и автору,'
                                      f' либо ссылке на Яндекс.Музыку\n'
                                      f'{p}play - воспроизводит текущую очередь\n{p}pause - пауза\n'
                                      f'{p}resume - снятие с паузы\n{p}stop - остановка и очистка очереди,'
                                      f' бот выходит из голосового канала\n'
                                      f'{p}review - обзор очереди\n{p}now - название текущего трека\n'
                                      f'{p}next - переключение на следующий трек')
    await ctx.reply(embed=embed)


bot.run(config.discord_key)
