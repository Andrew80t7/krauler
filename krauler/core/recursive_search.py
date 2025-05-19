import re
import logging
import time
from pathlib import Path

from telegram_api.downloader import process_channel as original_process_channel

logger = logging.getLogger('recursive_search')

# Ограничения
MAX_DEPTH = 2  # Максимальная глубина рекурсии
MAX_CHANNELS = 4  # Максимальное количество каналов
MAX_MESSAGES = 10  # Максимальное количество сообщений
MAX_CONCURRENT_TASKS = 1  # Один канал за раз


processed_channels = set()  # Все обработанные каналы
current_tasks = set()  # Текущие выполняющиеся задачи
processed_videos = set()  # Обработанные видео
last_video_time = time.time()  # Время последнего видео
MAX_NO_VIDEO_TIME = 30  # Максимальное время без новых видео


async def find_channel_links(text):
    if not text:
        return []
    pattern = r'(?:https?://)?t\.me/([a-zA-Z0-9_]+)|@([a-zA-Z0-9_]+)'
    matches = re.findall(pattern, text)
    return [f'@{match[0] or match[1]}' for match in matches]


def should_stop():
    global last_video_time

    # Проверяем время без новых видео
    if time.time() - last_video_time > MAX_NO_VIDEO_TIME:
        logger.warning(f"Нет новых видео более {MAX_NO_VIDEO_TIME} сек")
        return True

    # Проверяем количество каналов
    if len(processed_channels) >= MAX_CHANNELS:
        logger.info(f"Достигнуто максимальное количество каналов {MAX_CHANNELS}")
        return True

    return False


async def process_channel_recursive(client, channel, visited=None, max_depth=MAX_DEPTH, current_depth=0):
    global processed_channels, current_tasks, last_video_time

    if visited is None:
        visited = set()
        processed_channels.clear()
        current_tasks.clear()
        processed_videos.clear()
        last_video_time = time.time()

    # Проверяем все возможные условия для пропуска канала
    if channel in visited:
        logger.debug(f"Канал {channel} уже посещен в текущем обходе")
        return
    if channel in processed_channels:
        logger.debug(f"Канал {channel} уже был обработан ранее")
        return
    if current_depth >= max_depth:
        logger.debug(f"Достигнута максимальная глубина {max_depth}")
        return
    if len(processed_channels) >= MAX_CHANNELS:
        logger.info(f"Достигнуто максимальное количество каналов {MAX_CHANNELS}")
        return
    if len(current_tasks) >= MAX_CONCURRENT_TASKS:
        logger.debug(f"Достигнут лимит одновременных задач")
        return

    # Добавляем канал в отслеживаемые множества
    visited.add(channel)
    processed_channels.add(channel)
    current_tasks.add(channel)

    logger.info(f"Обрабатываю канал: {channel} (глубина: {current_depth}, всего каналов: {len(processed_channels)})")

    try:
        # Получаем сущность канала
        channel_entity = await client.get_entity(channel)

        # Обрабатываем видео
        videos_processed = await original_process_channel(client, channel)

        if videos_processed > 0:
            last_video_time = time.time()
            processed_videos.update(range(videos_processed))
            logger.info(f"Обработано видео в канале {channel}: {videos_processed}")

        # Проверяем условия остановки
        if should_stop():
            logger.info("Программа остановлена после обработки видео")
            return

        # Обрабатываем сообщения
        message_count = 0
        async for message in client.iter_messages(channel_entity, limit=MAX_MESSAGES):
            if len(processed_channels) >= MAX_CHANNELS:
                break

            message_count += 1
            related_channels = await find_channel_links(message.text)

            # Обрабатываем новые каналы
            for related in related_channels:
                if len(processed_channels) < MAX_CHANNELS:
                    await process_channel_recursive(
                        client,
                        related,
                        visited,
                        max_depth,
                        current_depth + 1
                    )

        logger.info(f"Завершена обработка канала {channel}: {message_count} сообщений")

    except Exception as e:
        logger.error(f"Ошибка при обработке канала {channel}: {e}")
    finally:
        # Удаляем канал из текущих задач
        current_tasks.discard(channel)

        # Если это последний канал, выводим статистику
        if len(processed_channels) >= MAX_CHANNELS:
            logger.info("\n=== ФИНАЛЬНАЯ СТАТИСТИКА ===")
            logger.info(f"Обработано каналов: {len(processed_channels)}")
            logger.info(f"Список обработанных каналов: {', '.join(processed_channels)}")
