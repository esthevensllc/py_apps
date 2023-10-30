import os
from src.shared.config import STORAGE_DIR
from src.shared.cache.domain import CacheRepository

class FileCacheRepository():
    def __init__(self):
        self.base_storage = f'{STORAGE_DIR}cache'
    
    def get(self, key):
        value = None
        filepath = f"{self.base_storage}/{key}"
        if not os.path.exists(filepath):
            return None
        with open(f"{filepath}", newline='', encoding='UTF-8') as file:
            value = file.read()
        return value

    def set(self, key, value):
        filepath = f"{self.base_storage}/{key}"
        with open(filepath, 'w') as content:
            content.write(value)