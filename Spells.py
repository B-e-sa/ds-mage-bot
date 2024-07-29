import discord
import asyncio
import gtts
from yt_dlp import YoutubeDL
from enum import Enum
from discord import FFmpegPCMAudio


class SpellsEnum(Enum):
    COMBUSTAO = "combustao"
    MISSILE = "missile"

    SILENCIO = "silencio"
    POLIMORFE = "polimorfe"
    ESCUDO = "escudo"
    MUSICA = "canto"
    REVERBERAR = "reverberare"

class Spells():
    @staticmethod
    def combustion(voice_connection: discord.VoiceClient, disconnect_function):
        voice_connection.play(
            discord.FFmpegPCMAudio(
                f'./sounds/{SpellsEnum.COMBUSTAO.value}.mp3'),
            after=lambda _: disconnect_function())

    @staticmethod
    def missile(voice_connection: discord.VoiceClient, disconnect_function):
        voice_connection.play(
            discord.FFmpegPCMAudio(
                f'./sounds/{SpellsEnum.MISSILE.value}.mp3'),
            after=lambda _: disconnect_function())

    @staticmethod
    async def unpolymorph(member: discord.Member):
        await asyncio.sleep(5)
        await asyncio.gather(
            member.edit(mute=False),
            member.edit(deafen=False))
        
    @staticmethod
    async def polymorph(
            member_name: str,
            voice_connection: discord.VoiceClient,
            voice_channel: discord.VoiceChannel,
            disconnect_function
    ):
        voice_connection.play(
            FFmpegPCMAudio(f'./sounds/{SpellsEnum.POLIMORFE.value}.mp3'),
            after=lambda _: disconnect_function())

        for member in voice_channel.members:
            if str.lower(member.name) == member_name:
                await asyncio.gather(
                    member.edit(mute=True),
                    member.edit(deafen=True))
                await Spells.unpolymorph(member)

    @staticmethod
    def sing(client, message, disconnect_function):
        FFMPEG_OPTIONS = {
            'before_options':
            '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -probesize 200M',
            'options': '-vn'
        }

        YDL_OPTIONS = {
            'format': 'bestaudio/best',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    
        video_url = message.content.split("<")[1]
        voice = client.vc
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(video_url, download=False)
            url2 = info['url']
            source = FFmpegPCMAudio(url2, **FFMPEG_OPTIONS)
            voice.play(source, after=lambda _: disconnect_function())
            
    @staticmethod
    async def reverb(client, message, disconnect_function):
        translated = message.content.split("<")[1]
        voice = client.vc

        translated = gtts.gTTS(translated, lang="pt")
        translated.save("som.mp3")
        source = FFmpegPCMAudio("som.mp3")
        voice.play(source, after=lambda _: disconnect_function())