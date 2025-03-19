from telethon import TelegramClient
import socks


async def get_client(config):
    proxy = None
    if config.get('proxy'):
        proxy = {
            'proxy_type': socks.SOCKS5,
            'addr': config['proxy']['addr'],
            'port': config['proxy']['port']
        }
    client = TelegramClient('session_name', config['api_id'], config['api_hash'], proxy=proxy)
    await client.start(phone=config['phone'])
    return client
