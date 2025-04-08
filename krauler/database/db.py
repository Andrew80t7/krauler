import sqlite3
from datetime import datetime

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect('videos.db')
    cursor = conn.cursor()
    
    # Создаем таблицу для видео
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        size INTEGER,
        file_path TEXT,
        file_size INTEGER,
        duration INTEGER,
        width INTEGER,
        height INTEGER,
        bitrate INTEGER,
        fps REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Создаем таблицу для статистики каналов
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

def update_channel_stats(channel: str, subscribers_count: int = 0, views_count: int = 0, posts_count: int = 0):
    """Обновление статистики канала"""
    conn = sqlite3.connect('videos.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR REPLACE INTO channel_stats 
    (channel, subscribers_count, views_count, posts_count, last_updated)
    VALUES (?, ?, ?, ?, ?)
    ''', (channel, subscribers_count, views_count, posts_count, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def insert_video(channel: str, message_id: int, file_path: str, file_size: int, duration: int = None, mime_type: str = None):
    """Добавление информации о видео в базу данных"""
    conn = sqlite3.connect('videos.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO videos (name, file_path, file_size, duration)
    VALUES (?, ?, ?, ?)
    ''', (f"{channel}_{message_id}", file_path, file_size, duration))
    
    conn.commit()
    conn.close() 