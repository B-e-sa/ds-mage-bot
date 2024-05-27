from enum import Enum
import re
from discord import Client, Message
from Spells import Spells, SpellsEnum

"""
comandos que possuem parametros sempre terao
um espaco apos o prefixo
"""


class InteractionsEnum (Enum):
    ASK = "loquere, "
    ERASE = "erasus "

    DEFAULT = ">"
    GREETINGS = "ostende mihi omnia"
    SPELLS = "incantationes"
    QUESTIONS = "quaestiones"


class Interaction():
    def __init__(self):
        interactions_length = len(InteractionsEnum) - 1

        self.__regex = r"("
        for i, interaction in enumerate(InteractionsEnum):
            self.__regex += interaction.value + \
                ("|" if i != interactions_length else "")
        self.__regex += r")"

    async def handle(self, client: Client, message: Message):
        lowercase_message = str.lower(message.content)
        author_message_channel = message.channel

        """
        ve se a mensagem é uma interacao, se nao for e o bot 
        atualmente estiver em uma conversa, ele respondera a mensagem
        """
        interaction_words = re.findall(self.__regex, lowercase_message)
        interaction_word = None

        if (len(interaction_words) != 0):
            interaction_word = interaction_words[0]

        if not interaction_word:
            """
            se uma instancia do chat ja estiver aberta e o usuario
            mandar uma mensagem com alguma pontuacao, o bot respondera

            exemplo de pergunta: como vai voce?
                                 ou
                                 nao entendi, reexplique!
            """
            if (client.current_chat and lowercase_message[-1] in ["?", "!", ".", ","]
                    and not client.already_answering):
                if lowercase_message == "obrigado!" or lowercase_message == "agradeço!" or lowercase_message == "gratias ago!":
                    await client.send_message(author_message_channel.id, "Mutua benevolentia")
                    client.current_chat = None
                    client.already_answering = False
                else:
                    client.already_answering = True
                    response = client.current_chat.send_message(
                        lowercase_message)
                    await client.send_message(author_message_channel.id, response.text)
                    client.already_answering = False
        else:
            if interaction_word == InteractionsEnum.GREETINGS.value:
                greating = "Quid cupis scire, o que deseja saber?\n\n"
                spells = "Incantationes? Feitiços?\n"
                questions = "Quaestiones? Perguntas?\n"
                phrase = f"{greating}{spells}{questions}"
                await client.get_channel(message.channel.id).send(phrase)
            
            elif interaction_word == InteractionsEnum.QUESTIONS.value:
                phrase = 'Diga: "loquere," e prossiga com sua pergunta, libenter tibi respondebo, lhe responderei com prazer'
                await client.send_message(message.channel.id, phrase)

            elif interaction_word == InteractionsEnum.DEFAULT.value:
                """
                exemplo de entradas:
                    >combustao                              # conjura combustao no canal atual
                    >combustao:1228907192753717329          # conjura combustao no canal de id provido

                    >poliforme<b_e_sa                       # conjura poliforme em b_e_sa no canal atual
                    >poliforme<b_e_sa:1228907192753717329   # conjura poliforme em b_e_sa, que esta no canal de id provido
                """
                pattern = r">(\w+)(?:<(\w+))?(?::(\d+))?"

                match = re.search(pattern, lowercase_message)

                if match:
                    spell = match.group(1)
                    target = match.group(2)
                    channel_id = match.group(3)

                    author_message_channel = message.channel
                    if spell in [s.value for s in SpellsEnum]:
                        """
                        o discord ja trata quando o bot tenta entrar
                        em uma call em que ja esta
                        """
                        try:
                            if target:
                                """
                                se o feitico possuir um alvo e tambem o id do canal dele,
                                o bot entrara no canal especificdo
                                """
                                if channel_id:
                                    await client.connect_to_channel(channel_id)
                                else:
                                    """
                                    caso nao, o bot entrara no canal do autor
                                    """
                                    author_channel = message.author.voice.channel
                                    if author_channel:
                                        await client.connect_to_channel(author_channel.id)
                            else:
                                if spell != SpellsEnum.SILENCIO.value:
                                    """
                                    caso nao, o bot entrara no canal do autor
                                    """
                                    author_channel = message.author.voice.channel
                                    if author_channel:
                                        await client.connect_to_channel(author_channel.id)

                            if client.current_voice_channel:
                                match spell:
                                    case SpellsEnum.POLIMORFE.value:
                                        await Spells.polymorph(
                                            target,
                                            client.voice_channel_connection,
                                            client.current_voice_channel,
                                            client.disconnect)

                                    case SpellsEnum.COMBUSTAO.value:
                                        Spells.combustion(
                                            client.voice_channel_connection,
                                            client.disconnect)

                                    case SpellsEnum.SILENCIO.value:
                                        """
                                        após o stop irá disparar a desconexao de qualquer forma
                                        (se estiver tocando um audio)
                                        """
                                        client.voice_channel_connection.stop()
                            else:
                                await client.send_message(author_message_channel.id,
                                                          "Non te audivi, não te ouço, nec invocatus fui")
                        except:
                            await client.send_message(author_message_channel.id,
                                                      "Iam incantationem conicio, já estou sendo invocado")
                    else:
                        await client.send_message(author_message_channel.id,
                                                  "Nescio... hunc incantationem, não conheço este feitiço")

            elif interaction_word == InteractionsEnum.SPELLS.value:
                command = ">[Invocatio]<[Nomen]:[Locus]"
                resume = "\n\nLocatio et nomen, nome e localização optionales sunt; sed incantationem necessarium, o feitiço é necessário e eu devo conhece-lô"
                phrase = f"{command}{resume}"
                await client.send_message(message.channel.id, phrase)

            elif interaction_word == InteractionsEnum.ERASE.value:
                ids = lowercase_message.split(interaction_word)[1].split(",")

                if len(ids) != 0:
                    found_messages = []
                    for id in ids:
                        message = await message.channel.fetch_message(id)
                        if not message:
                            continue
                        found_messages.append(message)
                    if (found_messages) != 0:
                        await message.channel.delete_messages(found_messages)

            elif interaction_word == InteractionsEnum.ASK.value:
                """ comando de pergunta
                a primeira pergunta comecara com o prefixo 'loquere, '
                exemplo de pergunta mínima: loquere, oi!
                """
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
