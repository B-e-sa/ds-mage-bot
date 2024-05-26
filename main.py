import discord
import asyncio
import os
from dotenv import load_dotenv
from Spells import Spells

load_dotenv()
token = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

client = discord.Client(intents=intents)

current_voice_channel = None
voice_channel_connection = None

def quit_voice_channel():
    global voice_channel_connection
    voice_channel_connection = None

async def unpoliform(member: discord.Member):
    await asyncio.sleep(5)
    await member.edit(mute=False)
    await member.edit(deafen=False)

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
        quit_voice_channel()
    except:
        pass

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    lowercase_message = str.lower(message.content).split(">")

    if lowercase_message[0] == "":
        spell = lowercase_message[1]

        if spell in [s.value for s in Spells]:
            author_voice_channel = message.author.voice.channel
            if author_voice_channel:
                global current_voice_channel
                voice_channel = client.get_channel(author_voice_channel.id)
                current_voice_channel = voice_channel

            global voice_channel_connection
            if not voice_channel_connection:
                try:
                    voice_channel_connection = await voice_channel.connect()
                except discord.errors.ClientException:
                    await client.get_channel(message.channel.id).send("Não... não consigo")
                    pass

            match spell:
                case Spells.POLIMORFE.value:
                    voice_channel_connection.play(
                        discord.FFmpegPCMAudio(f'./sounds/{Spells.POLIMORFE.value}.mp3'),
                        after=lambda x: disconnect(
                            voice_channel_connection, client)
                    )
                    for member in current_voice_channel.members:
                        if member.name == lowercase_message[2]:
                            await member.edit(mute=True)
                            await member.edit(deafen=True)
                            await voice_channel_connection.disconnect()
                            await unpoliform(member)

                case Spells.COMBUSTAO.value:
                    voice_channel_connection.play(
                        discord.FFmpegPCMAudio(f'./sounds/{Spells.COMBUSTAO.value}.mp3'),
                        after=lambda x: disconnect(
                            voice_channel_connection, client)
                    )

                case Spells.SILENCIO.value:
                    voice_channel_connection.stop()

@client.event
async def on_ready():
    print("Bot conectado!")

client.run(token, log_handler=None)
