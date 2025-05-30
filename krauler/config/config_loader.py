import json
import os


def load_config(config_path):
    """
    Загрузка конфигурации
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Конфигурационный файл не найден: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f) 