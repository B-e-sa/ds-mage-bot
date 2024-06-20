from discord import Message

async def ask(client, message: Message, interaction_word):
    """ comando de pergunta
    a primeira pergunta comecara com o prefixo 'loquere, '
    exemplo de pergunta mínima: loquere, oi!
    """
    lowercase_message = message.content.lower()

    if ((len(lowercase_message) > len(interaction_word) + 3)
            and not client.already_answering):
        author_message_channel = message.channel
        question = lowercase_message.split(interaction_word)[1]

        if not client.current_chat:
            chat = client.model.start_chat(history=[])
            client.current_chat = chat

            response = chat.send_message(question)
            await client.send_message(author_message_channel.id, "Hmm...")

            client.already_answering = True
            response = client.model.generate_content(question)
            await client.send_message(author_message_channel.id, response.text)
            client.already_answering = False