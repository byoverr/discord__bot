import asyncio
import json

import discord
import random
from weather_forecast import Weather
from download_audio import download_audio
import requests


class MyClient(discord.Client):
    def __init__(self):
        super().__init__()

        self.text_channels = []
        self.category_channels = []
        self.voice_channels = []

        self.connected_voice_channel = None
        self.voice_client = None
        self.music_queue = []
        self.message_interface = None
        self.music_count = 0
        self.mes_music_control = None
        self.clicked_next = False
        self.react_hints_mes_sp = []
        self.user_bot = None

        self.room_activated = False
        self.room_channel = None

    async def on_reaction_add(self, reaction, user):
        if reaction.message == self.mes_music_control:
            if user.name == 'proovie':
                self.user_bot = user
            if user.name != 'proovie':
                if reaction.emoji == '\u2753':
                    await reaction.message.remove_reaction('\u2753', user)
                    await reaction.message.remove_reaction('\u2753', self.user_bot)

                    self.react_hints_mes_sp.append(await reaction.message.channel.send(f'❔ - для подсказки\n'
                                                                                       f'❌ - для остановки потока\n'
                                                                                       f'⏸️ - для паузы\n'
                                                                                       f'▶️ - для продолжения'
                                                                                       f' воспроизведения\n'
                                                                                       f'⏭️ для пропуска трека\n'))
                elif reaction.emoji == '\u274C':
                    if len(self.react_hints_mes_sp) > 0:
                        for el in self.react_hints_mes_sp:
                            await el.delete()
                    if self.voice_client:
                        if self.voice_client.is_playing():
                            self.voice_client.stop()
                        self.music_queue = []
                        await reaction.message.delete()
                    self.react_hints_mes_sp = []

                elif reaction.emoji == '\u23F8':
                    await reaction.message.remove_reaction('\u23F8', user)
                    if self.voice_client:
                        if self.voice_client.is_playing():
                            self.voice_client.pause()
                        else:
                            self.react_hints_mes_sp.append(await reaction.message.channel.
                                                           send('Уже поставлена на паузу'))

                elif reaction.emoji == '\u25B6':
                    await reaction.message.remove_reaction('\u25B6', user)
                    if self.voice_client:
                        if self.voice_client.is_paused():
                            self.voice_client.resume()
                        else:
                            self.react_hints_mes_sp.append(await reaction.message.channel.send('Уже играет'))

                elif reaction.emoji == '\u23ED':
                    await reaction.message.remove_reaction('\u23ED', user)
                    if self.voice_client:
                        if len(self.music_queue) > 0:
                            self.voice_client.stop()
                            self.clicked_next = True
                            await self.play_audio()

    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        for guild in client.guilds:
            for channel in guild.channels:
                if str(channel) == 'general':
                    await channel.send('К работе готов')
                if str(channel.type) == 'text':
                    self.text_channels.append(channel)
                elif str(channel.type) == 'category':
                    self.category_channels.append(channel)
                elif str(channel.type) == 'voice':
                    self.voice_channels.append(channel)

    async def on_message(self, message):
        if message.author != 'proovie#3996':
            if message.content.startswith('Пруви, команды'):
                await message.channel.send('"привет", "как дела?", "создай канал", "удали канал",'
                                           ' "погода на сегодня/завтра <населённый пункт>", "отключись от меня"'
                                           ' "включи <ссылка youtube, spotify, etc> или запрос"'
                                           ' "объяви собрание", "закончи собрание", "найди/как <запрос>"'
                                           '"расскажи анекдот", "расскажи факт" "пришли фото лисы/собаки/кота"')

            elif message.content.startswith('Пруви, '):
                text = message.content.replace('Пруви, ', '')
                if text == 'привет':
                    await message.channel.send(f'Привет, {str(message.author).split("#")[0]}')
                elif text == 'как дела?' or text == 'как жизнь?' or text == 'как делишки?':
                    response = self.random_choose_phrase(self.read_file('phrases/how_everything.txt'))
                    await message.channel.send(response)

                elif text == 'кто ты?' or text == 'представься':
                    response1 = self.random_choose_phrase(self.read_file('phrases/who_are_you.txt'))
                    await message.channel.send(response1)

                elif text.startswith('кто'):
                    response = self.random_choose_phrase(self.read_file('phrases/who.txt'))
                    await message.channel.send(response)

                elif text.startswith('где'):
                    response = self.random_choose_phrase(self.read_file('phrases/where.txt'))
                    await message.channel.send(response)

                elif text.startswith('зачем'):
                    response = self.random_choose_phrase(self.read_file('phrases/why.txt'))
                    await message.channel.send(response)

                elif text.startswith('как'):
                    mes = text.split()[1:]
                    if mes:
                        await message.channel.send('Сейчас разберемся')
                        await message.channel.send(f'https://yandex.ru/search?text={"%20".join(text.split())}')
                    else:
                        response = self.random_choose_phrase(self.read_file('phrases/how.txt'))
                        await message.channel.send(response)

                elif text.startswith('найди') or text.startswith('поищи') or text.startswith('открой'):
                    mes = text.split()[1:]
                    if mes:
                        await message.channel.send('Ищу в Яндексе')
                        await message.channel.send(f'https://yandex.ru/search?text={"%20".join(mes)}')
                    else:
                        await message.channel.send('Я не расслышал запрос, повторите пожалуйста')

                elif text.startswith('создай канал'):
                    chan_to_create = text.replace('создай канал', '')[1:]
                    if chan_to_create:
                        chan = await message.guild.create_text_channel(chan_to_create)
                        self.text_channels.append(chan)
                        await message.channel.send(f'Канал {chan_to_create} успешно создан')
                    else:
                        await message.channel.send('Я не расслышал название, повторите пожалуйста')

                elif text.startswith('удали канал'):
                    chan_to_delete = text.replace('удали канал', '')[1:]
                    deleted = False
                    for elem in self.text_channels:
                        if elem.name == chan_to_delete:
                            deleted = True
                            self.text_channels.remove(elem)
                            await elem.delete()
                    if deleted:
                        await message.channel.send(f'Канал {chan_to_delete} успешно удален')
                    else:
                        await message.channel.send(f'Канал {chan_to_delete} не найден')

                elif 'погода на сегодня' in text:
                    wthr = Weather(' '.join(text.split()[3:]))
                    await message.channel.send(wthr.form_answer_today())

                elif 'погода на завтра' in text:
                    wthr = Weather(' '.join(text.split()[3:]))
                    await message.channel.send(wthr.form_answer_tomorrow())

                elif text.startswith('включи'):
                    if self.connected_voice_channel is None:
                        found = False
                        for elem in self.voice_channels:
                            if message.author in elem.members:
                                self.connected_voice_channel = elem
                                self.voice_client = await elem.connect()
                                found = True
                        if found is False:
                            await message.channel.send('А куда?')
                    if self.voice_client is None:
                        await message.channel.send('Мне некуда включать музыку')
                    else:
                        text = text.replace('включи ', '')
                        url = text
                        self.result, self.file, self.name, duration, self.uploader, self.uploader_url, \
                        self.url, self.thumbnail = download_audio(url)
                        self.duration = parse_duration(int(duration))
                        if self.result:
                            if self.voice_client.is_playing() is False:
                                self.music_queue.append([url, message.author])
                                with open('logs.txt', mode='a') as f:
                                    f.write(f'{message.author}  :  {url}\n')
                                #self.mes_music_control = await message.channel.send(f'Сейчас играет {name}')
                                embed = (discord.Embed(title='Now playing',
                                                       description='```css\n{0.name}\n```'.format(self),
                                                       color=discord.Color.blurple())
                                         .add_field(name='Duration', value=self.duration)
                                         .add_field(name='Requested by', value=message.author.mention)
                                         .add_field(name='Uploader',
                                                    value='[{0.uploader}]({0.uploader_url})'.format(self))
                                         .add_field(name='URL', value='[Click]({0.url})'.format(self))
                                         .set_thumbnail(url=self.thumbnail))
                                self.mes_music_control = await message.channel.send(embed=embed)
                                #await self.mes_music_control.pin()
                                await self.mes_music_control.add_reaction('\u2753') # ?
                                await self.mes_music_control.add_reaction('\u25B6')  # play
                                await self.mes_music_control.add_reaction('\u23F8') # pause
                                await self.mes_music_control.add_reaction('\u23ED') # next
                                await self.mes_music_control.add_reaction('\u274C')  # X
                                await self.play_audio()
                            else:
                                await message.channel.send('✅ Добавлено в очередь')
                                self.music_queue.append([url, message.author])
                                await self.mes_music_control.edit\
                                    (content=f'{self.mes_music_control.content[:-1]}{len(self.music_queue)}')

                elif text.startswith('выключи'):
                    if self.voice_client is None:
                        await message.channel.send('А я ничего и не включал')
                    else:
                        self.voice_client.stop()
                        self.music_queue = []
                        await self.mes_music_control.delete()

                elif text == 'отключись от меня':
                    if self.connected_voice_channel is None:
                        await message.channel.send('Я никуда и не подключался')
                    else:
                        self.connected_voice_channel = None
                        await self.voice_client.disconnect()

                elif text == 'объяви собрание':
                    if self.room_activated is False:
                        self.room_activated = True
                        self.room_channel = await message.guild.create_voice_channel('Комната сбора')
                        self.voice_channels.append(self.room_channel)
                        await message.channel.send(f'@everyone {message.author} объявил собрание'
                                                   f' в комнате сбора')
                    else:
                        await message.channel.send('Уже есть начатое собрание')

                elif text == 'закончи собрание':
                    if self.room_activated is True:

                        if len(self.room_channel.members) == 0:
                            self.room_activated = False
                            self.voice_channels.remove(self.room_channel)
                            await self.room_channel.delete()
                        else:
                            await message.channel.send('Не все участники покинули канал')
                    else:
                        await message.channel.send('Нет активной комнаты сбора')

                elif text == 'расскажи анекдот' or text == 'расскажи шутку' or text == 'пошути':
                    joke = self.random_choose_phrase(self.read_file('phrases/jokes.txt'))
                    await message.channel.send(joke)

                elif text == 'расскажи что-нибудь умное' or text == 'расскажи факт' or text == 'поумничай':
                    response = self.random_choose_phrase(self.read_file('phrases/facts.txt'))
                    await message.channel.send(response)

                elif text == 'пришли фото лисы':
                    response = requests.get('https://some-random-api.ml/img/Fox')
                    json_data = json.loads(response.text)

                    embed = discord.Embed(color=0xff9900, title='Лиса')
                    embed.set_image(url=json_data['link'])
                    await message.channel.send(embed=embed)

                elif text == 'пришли фото собаки':
                    response = requests.get('https://some-random-api.ml/img/Dog')
                    json_data = json.loads(response.text)

                    embed = discord.Embed(color=0xff9900, title='Собака')
                    embed.set_image(url=json_data['link'])
                    await message.channel.send(embed=embed)

                elif text == 'пришли фото кота':
                    source = requests.get(f"https://aws.random.cat/view/{random.randint(1, 1650)}").text
                    cat = source.split("src=\"")[1].split("\"")[0]
                    embed = discord.Embed(color=0xb9abc7, title='Кошка')
                    embed.set_image(url=cat)
                    await message.channel.send(embed=embed)
                else:

                    await message.channel.send('Мне неизвестна эта команда. Напишите'
                                               ' "Пруви, команды" чтобы узнать больше'
                                               'о моих способностях')

    async def play_audio(self):
        ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}
        while len(self.music_queue) > 0:
            if self.voice_client.is_playing() is False:
                a = self.music_queue.pop(0)
                self.result, self.file, self.name, duration, self.uploader, self.uploader_url, self.url, \
                self.thumbnail = download_audio(a[0])
                author = a[1]
                with open('logs.txt', mode='a') as f:
                    f.write(f'{author}  :  {self.url}\n')
                self.duration = parse_duration(int(duration))
                new_embed = (discord.Embed(title='Now playing',
                                       description='```css\n{0.name}\n```'.format(self),
                                       color=discord.Color.blurple())
                         .add_field(name='Duration', value=self.duration)
                         .add_field(name='Requested by', value=author.mention)
                         .add_field(name='Uploader',
                                    value='[{0.uploader}]({0.uploader_url})'.format(self))
                         .add_field(name='URL', value='[Click]({0.url})'.format(self))
                .set_thumbnail(url=self.thumbnail))
                await self.mes_music_control.edit(content=f'Треков в очереди: {len(self.music_queue)}')
                await self.mes_music_control.edit(embed=new_embed)
                self.voice_client.play(discord.FFmpegPCMAudio(
                    source=self.file, **ffmpeg_options))
                await asyncio.sleep(duration)
            if self.clicked_next:
                self.clicked_next = False
                break
        #await self.mes_music_control.delete()

    def read_file(self, filename):
        with open(filename, mode='r', encoding='utf-8') as fl:
            sp = fl.readlines()
        return sp

    def random_choose_phrase(self, sp):
        phrase = random.choice(sp)
        return phrase


def parse_duration(duration: int):
    minutes, seconds = divmod(duration, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    duration = []
    if days > 0:
        duration.append('{} days'.format(days))
    if hours > 0:
        duration.append('{} hours'.format(hours))
    if minutes > 0:
        duration.append('{} minutes'.format(minutes))
    if seconds > 0:
        duration.append('{} seconds'.format(seconds))

    return ', '.join(duration)

client = MyClient()
client.run(token)