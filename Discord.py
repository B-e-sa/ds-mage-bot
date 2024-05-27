import discord
import asyncio
import google.generativeai as genai
import os
from dotenv import load_dotenv
from Interactions import Interaction


class Discord(discord.Client):
    def __init__(self, *args, **kwargs):
        super(Discord, self).__init__(*args, **kwargs)
        self.current_voice_channel = None
        self.voice_channel_connection = None

        self.already_answering = False
        self.current_chat = None

        load_dotenv()
        genai.configure(api_key=os.getenv("GEMINI_TOKEN"))
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def disconnect(self):
        asyncio.run_coroutine_threadsafe(
            self.voice_channel_connection.disconnect(),
            self.loop
        )
        self.voice_channel_connection = None
        self.__interaction = Interaction()

    async def connect_to_channel(self, channel_id):
        self.current_voice_channel = self.get_channel(int(channel_id))
        self.voice_channel_connection = await self.current_voice_channel.connect()

    async def send_message(self, channel_id, message):
        await self.get_channel(int(channel_id)).send(message)

    async def on_ready(self):
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.listening, name="ostende mihi omnia"))

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        if len(message.content) != 0:
            await self.__interaction.handle(self, message)
