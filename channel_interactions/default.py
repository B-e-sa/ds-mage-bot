import re
from Spells import SpellsEnum, Spells
from discord import Message

async def default(client, message: Message, shielded_users, remove_shield):
    """
    exemplo de entradas:
        >combustao                              # conjura combustao no canal atual
        >combustao:1228907192753717329          # conjura combustao no canal de id provido

        >poliforme<b_e_sa                       # conjura poliforme em b_e_sa no canal atual
        >poliforme<b_e_sa:1228907192753717329   # conjura poliforme em b_e_sa, que esta no canal de id provido
    """
    pattern = r">(\w+)(?:<(\w+))?(?::(\d+))?"
    lowercase_message = message.content.lower()

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
            #try:
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
                    author_voice = message.author.voice
                    if author_voice.channel:
                        await client.connect_to_channel(author_voice.channel.id)
            elif channel_id:
                await client.connect_to_channel(channel_id)
            else:
                if spell != SpellsEnum.SILENCIO.value:
                    """
                    caso nao, o bot entrara no canal do autor
                    """
                    author_voice = message.author.voice
                    if author_voice.channel:
                        await client.connect_to_channel(author_voice.channel.id)

            if client.call:
                match spell:
                    case SpellsEnum.POLIMORFE.value:
                        if target in shielded_users:
                            await client.send_message(author_message_channel.id,
                                                        "O usuario esta escudado")
                            client.disconnect()
                            return

                        await Spells.polymorph(
                            target,
                            client.vc,
                            client.call,
                            client.disconnect)

                    case SpellsEnum.COMBUSTAO.value:
                        Spells.combustion(
                            client.vc,
                            client.disconnect)

                    case SpellsEnum.SILENCIO.value:
                        """
                        após o stop irá disparar a desconexao de qualquer forma
                        (se estiver tocando um audio)
                        """
                        client.vc.stop()

                    case SpellsEnum.ESCUDO.value:
                        client.disconnect()
                        shielded_users.append(message.author.name)
                        await client.send_message(author_message_channel.id,
                                                    "ESCUDADO!")
                        await remove_shield(message.author.name)

                    case SpellsEnum.MUSICA.value:
                        Spells.sing(client, message, client.disconnect)

                    case SpellsEnum.REVERBERAR.value:
                        await Spells.reverb(client, message, client.disconnect)
            else:
                await client.send_message(author_message_channel.id,
                                            "Non te audivi, não te ouço, nec invocatus fui")
            #except:
            #    print(e)

             #   await client.send_message(author_message_channel.id,
            #                                "Já estou sendo invocado ou você não está em um canal")
        else:
            await client.send_message(author_message_channel.id,
                                        "Nescio... hunc incantationem, não conheço este feitiço")
