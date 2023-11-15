
import json
import datetime as dt
import time
import os
from src.shared.config import STORAGE_DIR
from src.shared.cache.domain import CacheRepository

class FileCacheRepository(CacheRepository):
    def __init__(self):
        self.base_storage = f'{STORAGE_DIR}cache'
        if not os.path.exists(self.base_storage):
            os.mkdir(self.base_storage)
    
    def get(self, key, default=None):
        cache = {"data": default}
        filepath = f"{self.base_storage}/{key}.json"
        if not os.path.exists(filepath):
            return default
        with open(f"{filepath}", newline='', encoding='UTF-8') as file:
            cache = json.loads(file.read())
        expiration_time = cache.get("expiration_time")
        if expiration_time is None or time.time() < expiration_time:
            return cache["data"]
        else:
            os.unlink(filepath)
        return default

    def set(self, key, value, ttl_seconds=None):
        filepath = f"{self.base_storage}/{key}.json"
        # ts = dt.datetime.timestamp(dt.datetime.now() + dt.timedelta(seconds=ttl_seconds))
        ts = None
        if ttl_seconds is not None:
            ts = time.time() + ttl_seconds
        cache_content = json.dumps({"expiration_time": ts, "data": value})
        with open(filepath, 'w') as content:
            content.write(cache_content)