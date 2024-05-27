import discord
import asyncio
from enum import Enum


class SpellsEnum(Enum):
    COMBUSTAO = "combustao"
    SILENCIO = "silencio"
    POLIMORFE = "polimorfe"


class Spells():
    @staticmethod
    def combustion(voice_connection: discord.VoiceClient, disconnect_function):
        voice_connection.play(
            discord.FFmpegPCMAudio(
                f'./sounds/{SpellsEnum.COMBUSTAO.value}.mp3'),
            after=lambda x: disconnect_function()
        )

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
            discord.FFmpegPCMAudio(
                f'./sounds/{SpellsEnum.POLIMORFE.value}.mp3'),
            after=lambda x: disconnect_function())

        for member in voice_channel.members:
            if str.lower(member.name) == member_name:
                await asyncio.gather(
                    member.edit(mute=True),
                    member.edit(deafen=True))
                await Spells.unpolymorph(member)
