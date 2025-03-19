import sqlite3
import threading

conn = sqlite3.connect('videos.db', check_same_thread=False)
cursor = conn.cursor()
db_lock = threading.Lock()


def init_db():
    with db_lock:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY,
                channel TEXT,
                message_id INTEGER,
                file_path TEXT,
                size INTEGER,
                duration INTEGER,
                mime_type TEXT
            )
        ''')
        conn.commit()


def insert_video(channel, message_id, file_path, size, duration, mime_type):
    with db_lock:
        cursor.execute('''
            INSERT INTO videos (channel, message_id, file_path, size, duration, mime_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (channel, message_id, file_path, size, duration, mime_type))
        conn.commit()
