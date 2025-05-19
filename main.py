import asyncio
import os
import logging

from model.infer_debug import load_model
from model.neuro_model import predict_video
from telegram_api.client import get_client
from telegram_api.search import search_channels, process_channels_info
# from krauler.core.recursive_search import process_channel_recursive
from krauler.config.config_loader import load_config
from krauler.utils.logger import setup_logging
from krauler.utils.metrics import measure_time, time_tracker
from krauler.database.db import init_db, insert_video
from torchvision import transforms

logger = logging.getLogger('telegram')

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
    try:
        setup_logging()
        config_path = os.path.join('krauler', 'config', 'config.json')
        config = load_config(config_path)
        init_db()
        client = await get_client(config)

        # --- Выбор каналов ---
        if config.get('use_keyword_search', False):
            keyword = config.get('search_keyword', 'tech')
            logger.info(f"Поиск каналов по ключевому слову: {keyword}")
            channels = await search_channels(client, keyword, limit=500)
        else:
            channels = []
            for username in config.get('channels', []):
                try:
                    ch = await client.get_entity(username)
                    channels.append(ch)
                    logger.info(f"Добавлен канал: {username}")
                except Exception as e:
                    logger.error(f"Ошибка добавления канала {username}: {e}")

        if not channels:
            logger.warning("Каналы не найдены")
            return

        logger.info(f"Найдено каналов: {len(channels)}")

        # --- Сбор статистики ---
        logger.info("Сбор статистики по каналам")
        await process_channels_info(client, channels)

        # --- Новый способ: прямой обход сообщений и классификация ---
        for channel in channels:
            logger.info(f"Обрабатываем канал: {channel.username}")
            async for msg in client.iter_messages(channel, limit=config.get('max_messages', 1000)):
                if not msg.media:
                    continue
                # сохраняем временно в tmp.mp4
                tmp_path = f'tmp_{msg.id}.mp4'
                await client.download_media(msg.media, file=tmp_path)

                # прогоняем через модель
                pred = predict_video(tmp_path, model, transform)
                os.remove(tmp_path)

                if pred == 1:
                    # если модель решила скачать — сохраняем и логируем
                    file_path = os.path.join('downloaded_videos', f"{channel.username}_{msg.id}.mp4")
                    await client.download_media(msg.media, file=file_path)
                    insert_video(channel.username, msg.id, file_path, msg.file.size if hasattr(msg, 'file') else 0)
                    logger.info(f"Видео сохранено: {file_path}")
                else:
                    logger.debug(f"Видео пропущено моделью: {channel.username}/{msg.id}")

        # --- Закомментированная старая логика для сравнения ---
        # semaphore = asyncio.Semaphore(5)
        # async def rec_with_sem(client, username):
        #     async with semaphore:
        #         await process_channel_recursive(client, username)
        # tasks = [asyncio.create_task(rec_with_sem(client, ch.username)) for ch in channels]
        # await asyncio.gather(*tasks)

        await client.disconnect()

        # --- Логирование метрик времени ---
        stats = time_tracker.get_stats()
        logger.info("=== СТАТИСТИКА ВРЕМЕНИ ===")
        for op, d in stats.items():
            logger.info(f"{op}: total={d['total']:.2f}s, avg={d['avg']:.2f}s over {d['count']} runs")

        logger.info("Работа программы завершена.")

    except Exception as e:
        logger.error(f"Ошибка в main: {e}")
        logger.info("Завершение с ошибкой.")

if __name__ == "__main__":
    asyncio.run(main_async())
