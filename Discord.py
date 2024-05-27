import discord
from Spells import Spells, SpellsEnum
import asyncio
import re


class Discord(discord.Client):
    def __init__(self, *args, **kwargs):
        super(Discord, self).__init__(*args, **kwargs)
        self.__current_voice_channel = None
        self.__voice_channel_connection = None

    def __disconnect(self):
        asyncio.run_coroutine_threadsafe(
            self.__voice_channel_connection.disconnect(),
            self.loop
        )
        self.__voice_channel_connection = None

    async def __connect(self, channel_id):
        self.__current_voice_channel = self.get_channel(int(channel_id))
        self.__voice_channel_connection = await self.__current_voice_channel.connect()

    async def __send_message(self, channel_id, message):
        await self.get_channel(int(channel_id)).send(message)

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        
        if message.content[0] == ">":
            """
            exemplo de entradas:
                >combustao                              # conjura combustao no canal atual
                >combustao:1228907192753717329          # conjura combustao no canal de id provido

                >poliforme<b_e_sa                       # conjura poliforme em b_e_sa no canal atual
                >poliforme<b_e_sa:1228907192753717329   # conjura poliforme em b_e_sa, que esta no canal de id provido
            """
            pattern = r">(\w+)(?:<(\w+))?(?::(\d+))?"

            lowercase_message = str.lower(message.content)
            match = re.search(pattern, lowercase_message)

            if match:
                spell = match.group(1)
                target = match.group(2)
                channel_id = match.group(3)

                author_message_channel = message.channel
                if spell in [s.value for s in SpellsEnum]:
                    """
                    o discord ja trata quando o bot tenta entrar
                    em uma call em que ja esta
                    """
                    try:
                        if target:
                            """
                            se o feitico possuir um alvo e tambem o id do canal dele,
                            o bot entrara no canal especificdo
                            """
                            if channel_id:
                                await self.__connect(channel_id)
                            else:
                                """
                                caso nao, o bot entrara no canal do autor
                                """
                                author_channel = message.author.voice.channel
                                if author_channel:
                                    await self.__connect(author_channel.id)
                        else:
                            if spell != SpellsEnum.SILENCIO.value:
                                """
                                caso nao, o bot entrara no canal do autor
                                """
                                author_channel = message.author.voice.channel
                                if author_channel:
                                    await self.__connect(author_channel.id)

                        if self.__current_voice_channel:
                            match spell:
                                case SpellsEnum.POLIMORFE.value:
                                    await Spells.polymorph(
                                        target,
                                        self.__voice_channel_connection,
                                        self.__current_voice_channel,
                                        self.__disconnect)

                                case SpellsEnum.COMBUSTAO.value:
                                    Spells.combustion(
                                        self.__voice_channel_connection,
                                        self.__disconnect)

                                case SpellsEnum.SILENCIO.value:
                                    """
                                    após o stop irá disparar a desconeccao de qualquer forma
                                    (se estiver tocando um audio)
                                    """
                                    self.__voice_channel_connection.stop()
                        else:
                            await self.__send_message(
                                author_message_channel.id, 
                                "Não estou em um canal de voz ou você não me direcionou")
                    except:
                        await self.__send_message(
                            author_message_channel.id, 
                            "Já estou usando um feitiço longo no momento")
                else:
                    await self.__send_message(
                        author_message_channel.id, 
                        "Este feitiço... não o conheço")
