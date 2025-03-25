import re
import asyncio
from telegram_api.downloader import process_channel as original_process_channel


async def find_channel_links(text):
    if not text:
        return []
    pattern = r'(?:https?://)?t\.me/([a-zA-Z0-9_]+)|@([a-zA-Z0-9_]+)'
    matches = re.findall(pattern, text)
    return [f'@{match[0] or match[1]}' for match in matches]


async def process_channel_recursive(client, channel, visited=None, max_depth=3, current_depth=0):
    if visited is None:
        visited = set()
    if channel in visited or current_depth >= max_depth:
        return
    visited.add(channel)
    print(f"Обрабатываю канал: {channel} (глубина: {current_depth})")
    try:

        await original_process_channel(client, channel)

        channel_entity = await client.get_entity(channel)
        async for message in client.iter_messages(channel_entity):
            related_channels = await find_channel_links(message.text)
            for related in related_channels:
                asyncio.create_task(process_channel_recursive(client, related, visited, max_depth, current_depth + 1))
    except Exception as e:
        print(f"Ошибка при обработке канала {channel}: {e}")
