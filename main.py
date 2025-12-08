import os

from dotenv import load_dotenv
import logging

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from upstash_redis import Redis

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

telethon_api_id = int(os.getenv('TELETHON_API_ID'))
telethon_api_hash = os.getenv('TELETHON_API_HASH')
telethon_session_name = os.getenv('TELETHON_SESSION_NAME')

upstash_url = os.getenv('UPSTASH_REDIS_REST_URL')
upstash_token = os.getenv('UPSTASH_REDIS_REST_TOKEN')
upstash_key_words = os.getenv('UPSTASH_KEY_WORDS')
upstash_key_mentions = os.getenv('UPSTASH_KEY_MENTIONS')

session_hash = os.getenv('SESSION_HASH')

destination_channel = os.getenv('DESTINATION_CHANNEL')

client_telegram = TelegramClient(StringSession(session_hash), telethon_api_id, telethon_api_hash)

channels_listening = [
    'cmdiasyoutube',
    'setuphumilde',
    'ofertasgamer_oficial',
    'linksbrazil',
    'pcdofafapromo',
    'urubupromo',
    'tjgofertass',
]

words_listening = []
users_mentions = []

already_sent_message_empty_list_to_user = False

async def get_channel_id():
    await client_telegram.start()

    print("\nCANAIS E GRUPOS\n")

    # Lista todos os diálogos (conversas, canais, grupos)
    async for dialog in client_telegram.iter_dialogs():
        # Filtra apenas canais e supergrupos
        if dialog.is_channel or dialog.is_group:
            print(f"Nome: {dialog.name}")
            print(f"ID: {dialog.id}")
            print(f"Username: @{dialog.entity.username}" if dialog.entity.username else "Username: (privado)")
            print(f"Tipo: {'Canal' if dialog.is_channel else 'Grupo'}")
            print("-" * 50)

    await client_telegram.disconnect()

async def main():
    try:
        global words_listening
        global users_mentions

        await client_telegram.start()

        r = Redis(url=upstash_url, token=upstash_token)
        words_listening = r.smembers(upstash_key_words)
        users_mentions = r.smembers(upstash_key_mentions)

        logger.info('[UPSTASH] Initialized.')
        logger.info('[CLIENT_TELETHON] Client started successfully.')
        logger.info(f'[CLIENT_TELETHON] Listening words: {words_listening}')
        logger.info(f'[CLIENT_TELETHON] Listening channels: {channels_listening}')

        @client_telegram.on(events.NewMessage(chats=channels_listening))
        async def handler(event):
            try:
                global already_sent_message_empty_list_to_user
                if len(words_listening) == 0:
                    logger.warning("No words listening. Please add using /a <word> at your telegram saved messages.")
                    if not already_sent_message_empty_list_to_user:
                        await client_telegram.send_message(destination_channel, 'No words listening. Please add using /a <word> at your telegram saved messages.')
                        already_sent_message_empty_list_to_user = True
                    return

                text = event.raw_text

                if any(word.lower() in text.lower() for word in words_listening):
                    logger.info(f'A word matches from list. Sending message...')
                    await client_telegram.send_message(destination_channel, message=text)
                    if users_mentions:
                        mentions = ' '.join([f'@{user}' for user in users_mentions])
                        await client_telegram.send_message(destination_channel, message=mentions)
                    logger.info(f'[CLIENT_TELETHON] Message sent successfully')
            except Exception as err:
                logger.error(f'Error: {err}')

        def get_words_listening() -> str:
            words = ""
            for i, word in enumerate(words_listening, start=1):
                words += f"{i}. {word}\n"
            return f"WORDS LISTENING:\n\n{words}"

        def get_users_mention() -> str:
            mentions = ""
            for i, mention in enumerate(users_mentions, start=1):
                mentions += f"{i}. {mention}\n"
            return f"USERS TO MENTION:\n\n{mentions}"

        @client_telegram.on(events.NewMessage(from_users="me", chats=[destination_channel], pattern=r"^/l"))
        async def list_words(event):
            words = get_words_listening()
            await event.reply(words)

        @client_telegram.on(events.NewMessage(from_users="me", chats=[destination_channel], pattern=r"^/m"))
        async def list_mentions(event):
            mentions = get_users_mention()
            await event.reply(mentions)

        @client_telegram.on(events.NewMessage(from_users="me", chats=[destination_channel], pattern=r"^/a\s+(.*)"))
        async def add_word(event):
            try:
                word = event.pattern_match.group(0)[3:].strip()
                if len(word) <= 30:
                    r.sadd(upstash_key_words, word)
                    words_listening.append(word)
                    logger.info(f"Word {word} added to listener")
                    await event.reply(f"Word {word} added to listener.\n{get_words_listening()}")
                else:
                    logger.warning(f"Phrase or word too long")
                    await event.reply(f"Phrase or word too long")
            except Exception as err:
                logger.error(f'Error adding word: {err}')

        @client_telegram.on(events.NewMessage(from_users="me", chats=[destination_channel], pattern=r"^/r\s+(.*)"))
        async def remove_word(event):
            try:
                arg = event.pattern_match.group(1)
                if arg.isdigit():
                    num_item = int(arg)
                    if 1 <= num_item <= len(words_listening):
                        item = words_listening[num_item-1]
                        r.srem(upstash_key_words, item)
                        words_listening.pop(num_item-1)
                        logger.info(f"Word {item} removed from listener.")
                        await event.reply(f"Word {item} removed from listener.\n{get_words_listening()}")
                    else:
                        logger.warning(f"Item index {arg} not found in words")
                        await event.reply(f"Item index {arg} not found in words")
                else:
                    logger.warning("Error. You must pass a number from the list above. i.e: /r 2")
                    await event.reply("Error. You must pass a number from the list above. i.e: /r 2")
            except Exception as err:
                logger.error(f'Error removing word: {err}')

        @client_telegram.on(events.NewMessage(from_users="me", chats=[destination_channel], pattern=r"^/am\s+(.*)"))
        async def add_mention(event):
            try:
                user_mention = event.pattern_match.group(1).strip().lstrip('@')
                if 0 < len(user_mention) <= 32:
                    r.sadd(upstash_key_mentions, user_mention)
                    users_mentions.append(user_mention)
                    logger.info(f"User {user_mention} added to mention")
                    await event.reply(f"User {user_mention} added to mention.\n{get_users_mention()}")
                else:
                    logger.warning(f"User {user_mention} too long")
                    await event.reply(f"User {user_mention} too long")
            except Exception as err:
                logger.error(f'Error adding user to mention: {err}')

        @client_telegram.on(events.NewMessage(from_users="me", chats=[destination_channel], pattern=r"^/rm\s+(.*)"))
        async def remove_mention(event):
            try:
                arg = event.pattern_match.group(1)
                if arg.isdigit():
                    num_item = int(arg)
                    if 1 <= num_item <= len(users_mentions):
                        item = users_mentions[num_item-1]
                        r.srem(upstash_key_mentions, item)
                        users_mentions.pop(num_item-1)
                        logger.info(f"User {item} removed from mention.")
                        await event.reply(f"User {item} removed from mention.\n{get_users_mention()}")
                    else:
                        logger.warning(f"Item index {arg} not found in users to mention")
                        await event.reply(f"Item index {arg} not found in users to mention")
                else:
                    logger.warning("Error. You must pass a number from the list above. i.e: /rm 2")
                    await event.reply("Error. You must pass a number from the list above. i.e: /rm 2")
            except Exception as err:
                logger.error(f'Error removing user to mention: {err}')

        await client_telegram.run_until_disconnected()
    except Exception as e:
        logger.error(f'Error: {e}')

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
