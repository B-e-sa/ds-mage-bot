async def spells(client, message):
    command = ">[Invocatio]<[Nomen]:[Locus]"
    resume = "\n\nLocatio et nomen, nome e localização optionales sunt; sed incantationem necessarium, o feitiço é necessário e eu devo conhece-lô"
    phrase = f"{command}{resume}"
    await client.send_message(message.channel.id, phrase)