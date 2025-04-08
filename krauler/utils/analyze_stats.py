import sqlite3
from datetime import datetime
import pandas as pd
from pathlib import Path

def analyze_performance():
    """Анализ производительности и статистики каналов"""
    try:
        # Подключаемся к базе данных
        db_path = Path(__file__).parent.parent.parent / 'videos.db'
        conn = sqlite3.connect(db_path)
        
        # Получаем статистику по каналам
        query = '''
        SELECT 
            channel,
            subscribers_count,
            views_count,
            posts_count,
            last_updated
        FROM channel_stats
        ORDER BY subscribers_count DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            print("Нет данных для анализа")
            return
            
        print("\n=== Статистика по каналам ===")
        print(f"Всего каналов: {len(df)}")
        print(f"Общее количество подписчиков: {df['subscribers_count'].sum():,}")
        print(f"Среднее количество подписчиков: {df['subscribers_count'].mean():,.0f}")
        print(f"Медианное количество подписчиков: {df['subscribers_count'].median():,.0f}")
        
        print("\n=== Топ-10 каналов по подписчикам ===")
        print(df[['channel', 'subscribers_count', 'views_count', 'posts_count']].head(10).to_string())
        
        print("\n=== Распределение по количеству подписчиков ===")
        print(df['subscribers_count'].describe().to_string())
        
        # Анализ времени обновления
        df['last_updated'] = pd.to_datetime(df['last_updated'])
        print("\n=== Время последнего обновления ===")
        print(f"Самое раннее обновление: {df['last_updated'].min()}")
        print(f"Самое позднее обновление: {df['last_updated'].max()}")
        
        # Корреляция между подписчиками и просмотрами
        correlation = df['subscribers_count'].corr(df['views_count'])
        print(f"\nКорреляция между подписчиками и просмотрами: {correlation:.2f}")
        
        conn.close()
        
    except Exception as e:
        print(f"Ошибка при анализе: {e}")

if __name__ == "__main__":
    analyze_performance() 