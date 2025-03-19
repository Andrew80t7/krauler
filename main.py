import asyncio
from telegram_api.client import get_client
from telegram_api.search import search_channels
from telegram_api.downloader import process_channel
from config import load_config
from logger import setup_logging
from db import init_db


async def main_async():

    setup_logging()
    config = load_config('config.json')
    init_db()

    client = await get_client(config)

    keyword = "tech"
    channels = await search_channels(client, keyword, limit=500)

    for channel in channels:
        print(channel.username)
        asyncio.create_task(process_channel(client, channel.username))

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main_async())
