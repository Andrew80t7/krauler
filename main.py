import asyncio
import os
import logging

from model.infer_debug import load_model
from model.neuro_model import predict_video
# from krauler.neuro_model import load_model, predict_video
from telegram_api.client import get_client
from telegram_api.search import search_channels, process_channels_info
from krauler.config.config_loader import load_config
from krauler.utils.logger import setup_logging
from krauler.utils.metrics import measure_time, time_tracker
from krauler.database.db import init_db, insert_video
from torchvision import transforms

# Уровень логирования Telethon — только WARN/ERROR
logging.getLogger("telethon").setLevel(logging.WARNING)

logger = logging.getLogger('telegram')

# Параметры
NUM_FRAMES = 10
MAX_MSG = 1000

# Предобработка кадров для нейросети
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# Загружаем модель один раз
MODEL_CKPT = os.path.join('model', 'checkpoints', 'best_model.pth')
model = load_model(MODEL_CKPT, num_classes=2)

@measure_time('main_process')
async def main_async():
    setup_logging()
    config = load_config(os.path.join('krauler', 'config', 'config.json'))
    init_db()
    client = await get_client(config)

    # 1) Получаем список каналов
    if config.get('use_keyword_search', False):
        keyword = config.get('search_keyword', 'tech')
        logger.info(f"Поиск каналов по ключевому слову: {keyword}")
        channels = await search_channels(client, keyword, limit=500)
    else:
        channels = []
        for uname in config.get('channels', []):
            try:
                ch = await client.get_entity(uname)
                channels.append(ch)
                logger.info(f"Добавлен канал: {uname}")
            except Exception as ex:
                logger.error(f"Ошибка добавления канала {uname}: {ex}")

    if not channels:
        logger.warning("Каналы не найдены, выходим.")
        await client.disconnect()
        return

    # 2) Сбор статистики (опционально)
    logger.info("Сбор статистики по каналам")
    await process_channels_info(client, channels)

    # 3) Прямой обход сообщений и фильтрация нейросетью
    os.makedirs('downloaded_videos', exist_ok=True)
    # --- Новый способ: прямой обход сообщений и классификация ---
    for channel in channels:
        logger.info(f"Обрабатываем канал: {channel.username}")
        async for msg in client.iter_messages(channel, limit=config.get('max_messages', MAX_MSG)):
            if not msg.media:
                continue

            tmp = f"tmp_{msg.id}.mp4"
            await client.download_media(msg.media, file=tmp)

            # запускаем predict_video без лишних аргументов
            pred = predict_video(tmp, model, transform)
            os.remove(tmp)

            if pred == 1:
                out_path = os.path.join('downloaded_videos', f"{channel.username}_{msg.id}.mp4")
                await client.download_media(msg.media, file=out_path)
                # insert_video(channel.username, msg.id, out_path,
                #              getattr(msg, 'file', {}).get('size', 0))
                file_size = msg.file.size if getattr(msg, 'file', None) and hasattr(msg.file, 'size') else 0
                insert_video(channel.username, msg.id, out_path, file_size)
                logger.info(f"Сохранено: {out_path}")
            else:
                logger.debug(f"Пропущено сетью: {channel.username}/{msg.id}")

    # 4) Отключаем клиента
    await client.disconnect()

    # 5) Логируем метрики времени
    stats = time_tracker.get_stats()
    logger.info("=== СТАТИСТИКА ВРЕМЕНИ ===")
    for op, d in stats.items():
        logger.info(f"{op}: total={d['total']:.2f}s, avg={d['avg']:.2f}s over {d['count']} runs")

    logger.info("Программа завершена успешно.")

if __name__ == "__main__":
    asyncio.run(main_async())
