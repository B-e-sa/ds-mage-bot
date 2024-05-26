import discord
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

client = discord.Client(intents=intents)

def disconnect(
        current_voice_channel_connection: discord.VoiceClient, 
        current_client: discord.Client
    ):
    coroutine = asyncio.run_coroutine_threadsafe(
        current_voice_channel_connection.disconnect(), 
        current_client.loop
    )
    try:
        coroutine.result()
    except:
        pass

current_voice_channel = None
@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    if str.lower(message.content) == "bola de fogo":
        # dispara o som se o autor estiver em um canal
        author_voice_channel = message.author.voice.channel
        if author_voice_channel:
            voice_channel = client.get_channel(author_voice_channel.id)

            try:
                voice_channel_connection = await voice_channel.connect()
                voice_channel_connection.play(
                    discord.FFmpegPCMAudio('./sound.mp3'), 
                    after=lambda x: disconnect(voice_channel_connection, client)
                )
            except discord.errors.ClientException:
                await client.get_channel(message.channel.id).send("Não... não consigo")
                pass

@client.event
async def on_ready():
    print("Bot conectado!")

client.run(token)