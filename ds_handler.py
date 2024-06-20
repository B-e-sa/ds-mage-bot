import discord
import asyncio
import google.generativeai as genai
import os
from dotenv import load_dotenv
from channel_interactions.channel_interactions import ChannelInteractions
from Bot import Bot

class DsHandler():
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.__bot = Bot()
            self.__client = discord.Client(intents=self.__bot.get_intents())

            self._initialized = True
            load_dotenv()
            genai.configure(api_key=os.getenv("GEMINI_TOKEN"))
            self.model = genai.GenerativeModel('gemini-1.5-flash')

            self.call: discord.guild.GuildChannel = None
            self.vc: discord.VoiceClient = None

            self.already_answering: bool = False
            self.current_chat = None

            self.__client.event(self.on_ready)
            self.__client.event(self.on_message)

            self.__interaction = ChannelInteractions()

    def get_vc(self): return self.vc
    def get_call(self): return self.call
    def get_client(self): return self.__client
    def run(self): self.__client.run(self.__bot.get_token())

    def disconnect(self):
        asyncio.run_coroutine_threadsafe(
            self.vc.disconnect(),
            self.__client.loop
        )
        self.vc = None

    async def connect_to_channel(self, channel_id):
        self.call = self.__client.get_channel(int(channel_id))
        self.vc = await self.call.connect()

    async def send_message(self, channel_id, message):
        await self.__client.get_channel(int(channel_id)).send(message)

    async def on_ready(self):
        await self.__client.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="ostende mihi omnia"))

    async def on_message(self, message: discord.Message):
        if message.author == self.__client.user or message.author.id == 432610292342587392:
            return

        if len(message.content) != 0:
            await self.__interaction.handle(self, message)
