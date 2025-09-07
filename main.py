import os
from dotenv import load_dotenv
import logging

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from twilio.rest import Client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

telethon_api_id = int(os.getenv('TELETHON_API_ID'))
telethon_api_hash = os.getenv('TELETHON_API_HASH')
telethon_session_name = os.getenv('TELETHON_SESSION_NAME')

twilio_sid = os.getenv('TWILIO_SID')
twilio_token = os.getenv('TWILIO_TOKEN')
twilio_to_phone = os.getenv('TWILIO_TO_PHONE')
twilio_from_phone = os.getenv('TWILIO_FROM_PHONE')

session_hash = os.getenv('SESSION_HASH')

client_telegram = TelegramClient(StringSession(session_hash), telethon_api_id, telethon_api_hash)
client_twilio = Client(twilio_sid, twilio_token)

CHANNELS_LISTENING = [
    'cmdiasyoutube',
    'setuphumilde',
    'ofertasgamer_oficial',
    'linksbrazil',
    'pcdofafapromo',
    'urubupromo',
    'tjgofertass',
]

WORDS_LISTENING = []

already_sent_message_empty_list_to_user = False

async def main():
    await client_telegram.start()

    logger.info('[CLIENT_TELETHON] Client started successfully.')
    logger.info(f'[CLIENT_TELETHON] Listening words: {WORDS_LISTENING}')
    logger.info(f'[CLIENT_TELETHON] Listening channels: {CHANNELS_LISTENING}')

    def get_words_listening() -> str:
        words = ""
        for i, word in enumerate(WORDS_LISTENING, start=1):
            words += f"{i}. {word}\n"
        return f"WORDS LISTENING:\n\n{words}"

    @client_telegram.on(events.NewMessage(chats=CHANNELS_LISTENING))
    async def handler(event):
        try:
            global already_sent_message_empty_list_to_user
            if len(WORDS_LISTENING) == 0:
                logger.warning("No words listening. Please add using /a <word> at your telegram saved messages.")
                if not already_sent_message_empty_list_to_user:
                    client_twilio.messages.create(
                        to=twilio_to_phone,
                        from_=twilio_from_phone,
                        body="No words listening. Please add using /a <word> at your telegram saved messages."
                    )
                    already_sent_message_empty_list_to_user = True
                return

            text = event.raw_text
            logger.info(f'[CLIENT_TELETHON] Text: {text}')

            if any(word.lower() in text.lower() for word in WORDS_LISTENING):
                logger.info(f'[CLIENT_TELETHON] A word matches from list. Sending message to whatsapp...')
                client_twilio.messages.create(
                    to=twilio_to_phone,
                    from_=twilio_from_phone,
                    body=text
                )
        except Exception as e:
                logger.error(f'Error: {e}')

    @client_telegram.on(events.NewMessage(from_users="me", chats="me", pattern=r"^/l"))
    async def list_words(event):
        words = get_words_listening()
        await event.reply(words)

    @client_telegram.on(events.NewMessage(from_users="me", chats="me", pattern=r"^/r(?:\s+(.*))?"))
    async def remove_word(event):
        arg = event.pattern_match.group(1)
        if arg.isdigit():
            num_item = int(arg)
            if 1 <= num_item <= len(WORDS_LISTENING):
                item = WORDS_LISTENING[num_item-1]
                WORDS_LISTENING.pop(num_item-1)
                logger.info(f"Word {item} removed from listener.")
                await event.reply(f"Word {item} removed from listener.\n{get_words_listening()}")
            else:
                logger.warning(f"Item index {arg} not found in words")
                await event.reply(f"Item index {arg} not found in words")
        else:
            logger.warning(f"Item index {arg} not found in words")
            await event.reply('Error. You must pass a number from the list above. i.e: /r 2')

    @client_telegram.on(events.NewMessage(from_users="me", chats="me", pattern=r"^/a(?:\s+(.*))?"))
    async def add_word(event):
        word = event.pattern_match.group(0)[3:].strip()
        if len(word) <= 30:
            WORDS_LISTENING.append(word)
            logger.info(f"Word {word} added to listener")
            await event.reply(f"Word {word} added to listener.\n{get_words_listening()}")
        else:
            logger.warning(f"Phrase or word too long")
            await event.reply(f"Phrase or word too long")

    await client_telegram.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
