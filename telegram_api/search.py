from telethon.tl.functions.contacts import SearchRequest


async def search_channels(client, keyword, limit):
    result = await client(SearchRequest(q=keyword, limit=limit))
    channels = [chat for chat in result.chats if hasattr(chat, 'username') and chat.username]
    return channels
