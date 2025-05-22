import sqlite3
from datetime import datetime

DB_PATH = 'videos.db'


def init_db():
    """
    Инициализация базы данных: создаём таблицы videos и channel_stats.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Таблица для видео
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel TEXT NOT NULL,
        message_id INTEGER NOT NULL,
        file_path TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        duration INTEGER,
        mime_type TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Таблица для статистики каналов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS channel_stats (
        channel TEXT PRIMARY KEY,
        subscribers_count INTEGER,
        views_count INTEGER,
        posts_count INTEGER,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()


def update_channel_stats(channel: str,
                         subscribers_count: int = 0,
                         views_count: int = 0,
                         posts_count: int = 0):
    """
    Обновление статистики по каналу.
    Если записи нет — вставляем новую, иначе — обновляем.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO channel_stats
      (channel, subscribers_count, views_count, posts_count, last_updated)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(channel) DO UPDATE SET
      subscribers_count=excluded.subscribers_count,
      views_count=excluded.views_count,
      posts_count=excluded.posts_count,
      last_updated=excluded.last_updated
    ''', (channel, subscribers_count, views_count, posts_count, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def insert_video(channel: str,
                 message_id: int,
                 file_path: str,
                 file_size: int,
                 duration: int = None,
                 mime_type: str = None):
    """
    Вставка информации о скачанном видео.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO videos
      (channel, message_id, file_path, file_size, duration, mime_type)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (channel, message_id, file_path, file_size, duration, mime_type))

    conn.commit()
    conn.close()
