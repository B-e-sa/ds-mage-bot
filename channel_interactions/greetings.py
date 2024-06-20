async def greetings(client, message):
    greating = "Quid cupis scire, o que deseja saber?\n\n"
    spells = "Incantationes? Feitiços?\n"
    questions = "Quaestiones? Perguntas?\n"
    phrase = f"{greating}{spells}{questions}"
    await client.get_channel(message.channel.id).send(phrase)