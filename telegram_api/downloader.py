import os
import logging
from telethon.tl.types import InputMessagesFilterVideo
from db import insert_video

logger = logging.getLogger(__name__)

SAVE_DIR = 'downloaded_videos'
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)


async def download_video(client, channel, message):

    keyword = "iphone"
    if keyword.lower() not in (message.text or "").lower():
        return

    if not message.media:
        logger.info(f"Сообщение {message.id} не содержит медиа.")
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
    await client.download_media(message.media, file=file_path)
    logger.info(f"Видео сохранено: {file_path}")
    insert_video(channel, message.id, file_path, doc.size if doc else 0, None,
                 doc.mime_type if doc and hasattr(doc, 'mime_type') else 'video/mp4')


async def process_channel(client, channel):
    try:
        channel_entity = await client.get_entity(channel)
        async for message in client.iter_messages(channel_entity, filter=InputMessagesFilterVideo):
            await download_video(client, channel, message)
    except Exception as e:
        logger.error(f"Ошибка при обработке канала {channel}: {e}")
