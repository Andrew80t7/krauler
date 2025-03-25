import asyncio
from telegram_api.client import get_client
from telegram_api.search import search_channels
from recursive_search import process_channel_recursive
from config import load_config
from logger import setup_logging
from db import init_db


async def main_async():
    try:
        setup_logging()
        config = load_config('config.json')
        init_db()
        client = await get_client(config)

        keyword = "tech"
        channels = await search_channels(client, keyword, limit=500)

        if not channels:
            print("Каналы не найдены")
            return

        semaphore = asyncio.Semaphore(5)

        async def process_channel_recursive_with_semaphore(client, username):
            async with semaphore:
                await process_channel_recursive(client, username)

        tasks = []
        for channel in channels:
            print(f"Начинаю обработку канала: {channel.username}")
            task = asyncio.create_task(process_channel_recursive_with_semaphore(client, channel.username))
            tasks.append(task)

        await asyncio.gather(*tasks)
        await client.disconnect()
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main_async())