import discord
from Spells import Spells, SpellsEnum
import asyncio


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

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        lowercase_message = str.lower(message.content).split(">")

        if lowercase_message[0] == "":
            spell = lowercase_message[1]

            if spell in [s.value for s in SpellsEnum]:
                author_voice_channel = message.author.voice.channel
                if author_voice_channel:
                    voice_channel = self.get_channel(author_voice_channel.id)
                    self.__current_voice_channel = voice_channel

                if not self.__voice_channel_connection:
                    try:
                        voice_channel_connection = await voice_channel.connect()
                        self.__voice_channel_connection = voice_channel_connection
                    except discord.errors.ClientException:
                        await self.get_channel(message.channel.id).send("Não... não consigo")
                        pass

                match spell:
                    case SpellsEnum.POLIMORFE.value:
                        await Spells.polymorph(
                            lowercase_message[2],
                            self.__voice_channel_connection,
                            self.__current_voice_channel,
                            self.__disconnect)

                    case SpellsEnum.COMBUSTAO.value:
                        Spells.combustion(
                            self.__voice_channel_connection,
                            self.__disconnect)

                    case SpellsEnum.SILENCIO.value:
                        # após o stop irá disparar a desconeccao de qualquer forma
                        # (se estiver tocando um audio)
                        self.__voice_channel_connection.stop()
