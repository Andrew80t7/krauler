import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logging():
    # Создаем директорию для логов, если её нет
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Форматтер для логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Настройка файлового логгера с ротацией
    file_handler = RotatingFileHandler(
        f'logs/telegram_crawler_{datetime.now().strftime("%Y%m%d")}.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Настройка консольного логгера
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # Настройка корневого логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Создаем отдельные логгеры для разных компонентов
    telegram_logger = logging.getLogger('telegram')
    telegram_logger.setLevel(logging.INFO)

    downloader_logger = logging.getLogger('downloader')
    downloader_logger.setLevel(logging.INFO)

    metrics_logger = logging.getLogger('metrics')
    metrics_logger.setLevel(logging.INFO)

    return root_logger
