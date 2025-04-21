import asyncio
import os
from telegram_api.client import get_client
from telegram_api.search import search_channels, process_channels_info
from krauler.core.recursive_search import process_channel_recursive
from krauler.config.config_loader import load_config
from krauler.utils.logger import setup_logging
from krauler.utils.metrics import measure_time, time_tracker
from krauler.database.db import init_db
import logging

logger = logging.getLogger('telegram')


@measure_time('main_process')
async def main_async():
    try:
        setup_logging()
        config_path = os.path.join('krauler', 'config', 'config.json')
        config = load_config(config_path)
        init_db()
        client = await get_client(config)

        if config.get('use_keyword_search', False):
            # Поиск по ключевому слову
            keyword = config.get('search_keyword', 'tech')
            logger.info(f"Начинаю поиск каналов по ключевому слову: {keyword}")
            channels = await search_channels(client, keyword, limit=500)

        else:

            # Использование списка каналов
            channels = []
            for channel_username in config.get('channels', []):
                try:
                    channel = await client.get_entity(channel_username)
                    channels.append(channel)
                    logger.info(f"Добавлен канал: {channel_username}")


                except Exception as e:
                    logger.error(f"Ошибка при добавлении канала {channel_username}: {str(e)}")

        if not channels:
            logger.warning("Каналы не найдены")
            return

        logger.info(f"Найдено каналов: {len(channels)}")

        # Собираем статистику по каналам
        logger.info("Начинаю сбор статистики по каналам")
        await process_channels_info(client, channels)
        logger.info("=== Статистика по каналам успешно собрана! ===")
        logger.info("Теперь можно безопасно выключить программу, если нужно.")

        # Обрабатываем каналы
        semaphore = asyncio.Semaphore(5)

        async def process_channel_recursive_with_semaphore(client, username):
            async with semaphore:
                await process_channel_recursive(client, username)

        tasks = []
        for channel in channels:
            logger.info(f"Начинаю обработку канала: {channel.username}")
            task = asyncio.create_task(process_channel_recursive_with_semaphore(client, channel.username))
            tasks.append(task)

        await asyncio.gather(*tasks)
        await client.disconnect()

        # Выводим статистику времени
        stats = time_tracker.get_stats()
        logger.info("\n=== СТАТИСТИКА ВРЕМЕНИ ===")
        for operation, data in stats.items():
            logger.info(f"\nОперация: {operation}")
            logger.info(f"Всего времени: {data['total']:.2f} сек")
            logger.info(f"Среднее время: {data['avg']:.2f} сек")
            logger.info(f"Минимальное время: {data['min']:.2f} сек")
            logger.info(f"Максимальное время: {data['max']:.2f} сек")
            logger.info(f"Количество выполнений: {data['count']}")

        logger.info("\n=== Программа успешно завершила работу! ===")
        logger.info("Можно безопасно выключить программу.")

    except Exception as e:
        logger.error(f"Произошла ошибка: {str(e)}")
        logger.info("=== Программа завершилась с ошибкой. Можно безопасно выключить. ===")


if __name__ == "__main__":
    asyncio.run(main_async())
