async def erase(client, message, id=None):
    if message.channel.id in [1243814494057140284, 1088151111275397251, 1253200384579862619, 1237245390068387912]:
        found_messages = []
        async for message in message.channel.history():
            found_messages.append(message)

        await message.channel.delete_messages(found_messages)
    else:
        await client.send_message(
            message.channel.id,
            "Tentou apagar o canal né filha da puta")