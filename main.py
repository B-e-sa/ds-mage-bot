from Bot import Bot
from Discord import Discord

BOT = Bot()
DISCORD = Discord(intents=BOT.get_intents())
DISCORD.run(BOT.get_token())