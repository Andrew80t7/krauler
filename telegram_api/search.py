import logging
from telethon.tl.functions.contacts import SearchRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from krauler.database.db import update_channel_stats

logger = logging.getLogger('telegram')


async def search_channels(client, keyword, limit):
    result = await client(SearchRequest(q=keyword, limit=limit))
    channels = [chat for chat in result.chats if hasattr(chat, 'username') and chat.username]
    return channels


async def get_channel_info(client, channel_username: str) -> dict:
    try:
        channel = await client.get_entity(channel_username)
        full_channel = await client(GetFullChannelRequest(channel))
        
        # Получаем количество сообщений
        messages = await client.get_messages(channel, limit=0)
        total_messages = messages.total
        
        # Получаем последние 100 сообщений для подсчета среднего количества просмотров
        messages = await client.get_messages(channel, limit=100)
        total_views = sum(msg.views or 0 for msg in messages if hasattr(msg, 'views'))
        avg_views = total_views // len(messages) if messages else 0
        
        stats = {
            'subscribers_count': getattr(full_channel.full_chat, 'participants_count', 0),
            'views_count': avg_views,
            'posts_count': total_messages
        }
        
        logger.info(f"Получена информация о канале {channel_username}: {stats}")
        update_channel_stats(channel_username, **stats)
        
        return stats
    except Exception as e:
        logger.error(f"Ошибка при получении информации о канале {channel_username}: {str(e)}")
        return None


async def process_channels_info(client, channels):
    for channel in channels:
        if hasattr(channel, 'username'):
            await get_channel_info(client, channel.username)
