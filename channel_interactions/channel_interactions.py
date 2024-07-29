import re
from discord import Message
from asyncio import sleep
from db_instance import DbInstance

from channel_interactions import ask, greetings, erase, default, spells
from shared import ChannelInteractionsEnum

"""
comandos que possuem parametros sempre terao
um espaco apos o prefixo
"""


class ChannelInteractions():
    def __init__(self):
        self.db = DbInstance()

        interactions_length = len(ChannelInteractionsEnum) - 1

        self.__regex = r"("
        for i, interaction in enumerate(ChannelInteractionsEnum):
            self.__regex += interaction.value + \
                ("|" if i != interactions_length else "")
        self.__regex += r")"

        self.__shielded_users = []

    async def __remove_shield(self, user_name):
        await sleep(300)
        self.__shielded_users.remove(user_name)

    async def handle(self, ds_handler, message: Message):
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
            if (ds_handler.current_chat and lowercase_message[-1] in ["?", "!", ".", ","]
                    and not ds_handler.already_answering):
                if lowercase_message == "obrigado!" or lowercase_message == "agradeço!" or lowercase_message == "gratias ago!":
                    await ds_handler.send_message(author_message_channel.id, "Mutua benevolentia")
                    ds_handler.current_chat = None
                    ds_handler.already_answering = False
                else:
                    ds_handler.already_answering = True
                    response = ds_handler.current_chat.send_message(
                        lowercase_message)
                    await ds_handler.send_message(author_message_channel.id, response.text)
                    ds_handler.already_answering = False
        else:
            match interaction_word:
                case ChannelInteractionsEnum.GREETINGS.value:
                    await greetings.greetings(ds_handler, message)

                case ChannelInteractionsEnum.QUESTIONS.value:
                    phrase = 'Diga: "loquere," e prossiga com sua pergunta, libenter tibi respondebo, lhe responderei com prazer'
                    await ds_handler.send_message(message.channel.id, phrase)

                case ChannelInteractionsEnum.DEFAULT.value:
                    await default.default(ds_handler,
                                          message,
                                          self.__shielded_users,
                                          self.__remove_shield)

                case ChannelInteractionsEnum.SPELLS.value:
                    await spells.spells(ds_handler, message)

                case ChannelInteractionsEnum.ERASE.value:
                    await erase.erase(ds_handler, message)

                case ChannelInteractionsEnum.ASK.value:
                    await ask.ask(ds_handler, message, interaction_word)

                case ChannelInteractionsEnum.SHOP.value:
                    message_content = message.content.split(" ")
                    message_author = message.author.name

                    """
                    exemplo: 
                        venda:
                            mercatus vendere Reiner-Braun 200
                        remocao:
                            mercatus removere Reiner-Braun
                    """

                    if len(message_content) < 3:
                        pass

                    function = message_content[1]
                    character = message_content[2].replace("-", " ")

                    success = False
                    if function == "vendere" or function == "ven":
                        try:
                            price = int(message_content[3])
                            self.db.create_venda(character,
                                                message_author,
                                                price)
                            success = True

                        except IndexError:
                            await ds_handler.get_channel(message.channel.id).send(
                                "Preço necessário")

                    elif function == "removere" or function == "rem":
                        self.db.delete_venda(character)
                        success = True
                    else:
                        await ds_handler.get_channel(message.channel.id).send(
                            "Comando de mercado não reconhecido")

                    if success:
                        sorted_merchs = sorted(self.db.get_vendas(),
                                               key=lambda x: x[2],
                                               reverse=True)
                        merchs = {}
                        for char in sorted_merchs:
                            merch_seller = char[3]
                            merchs.setdefault(merch_seller, []).append([
                                char[1],
                                char[2]])

                        chars_on_marketplace = ""
                        chars_on_marketplace += "mercatus vendere [nome-do-personagem] [preco]\n"
                        chars_on_marketplace += "mercatus removere [nome-do-personagem]\n"

                        chars_on_marketplace += "```\n"
                        for key in merchs.keys():
                            chars_on_marketplace += f"{key}:\n"
                            for item in merchs[key]:
                                chars_on_marketplace += f"  {
                                    item[0]:<25} {item[1]:>6}\n"
                            chars_on_marketplace += "\n"
                        chars_on_marketplace += "```"

                        try:
                            global bot_message
                            async for mess in message.channel.history(oldest_first=True):
                                bot_message = mess
                                break

                            await bot_message.edit(content=chars_on_marketplace)
                        except:
                            await erase.erase(ds_handler, message)
                            await ds_handler.get_channel(message.channel.id).send(chars_on_marketplace)

                    await message.delete()
