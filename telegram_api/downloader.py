import os
import logging
from telethon.tl.types import InputMessagesFilterVideo
from krauler.database.db import insert_video

logger = logging.getLogger('downloader')

SAVE_DIR = 'downloaded_videos'
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)


async def download_video(client, channel, message):
    keyword = "FPV"
    if keyword.lower() not in (message.text or "").lower():
        return

    if not message.media:
        logger.debug(f"Сообщение {message.id} не содержит медиа.")
        return

    doc = getattr(message.media, 'document', None)
    file_name = None

    if doc and doc.attributes:
        for attr in doc.attributes:
            if hasattr(attr, 'file_name') and attr.file_name:
                file_name = attr.file_name
                break

    if not file_name:
        file_name = f"{channel}_{message.id}.mp4"

    file_path = os.path.join(SAVE_DIR, file_name)
    try:
        await client.download_media(message.media, file=file_path)
        logger.info(f"Видео успешно сохранено: {file_path}")
        insert_video(channel, message.id, file_path, doc.size if doc else 0, None,
                     doc.mime_type if doc and hasattr(doc, 'mime_type') else 'video/mp4')
    except Exception as e:
        logger.error(f"Ошибка при скачивании видео {file_name}: {str(e)}")


async def process_channel(client, channel):
    try:
        logger.info(f"Начинаю обработку канала: {channel}")
        channel_entity = await client.get_entity(channel)
        message_count = 0
        async for message in client.iter_messages(channel_entity, filter=InputMessagesFilterVideo):
            message_count += 1
            await download_video(client, channel, message)
        logger.info(f"Завершена обработка канала {channel}. Обработано сообщений: {message_count}")
    except Exception as e:
        logger.error(f"Ошибка при обработке канала {channel}: {str(e)}")
