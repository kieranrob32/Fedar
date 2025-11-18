from collections import OrderedDict
from time import time
from src.preferences import get_pref


class SearchCache:
    def __init__(self, max_size=50, ttl=300):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl
        self.enabled = get_pref('enable_cache', 'true') == 'true'
    
    def get(self, key):
        if not self.enabled:
            return None
        
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        if time() - entry['timestamp'] > self.ttl:
            del self.cache[key]
            return None
        
        self.cache.move_to_end(key)
        return entry['data']
    
    def set(self, key, value):
        if not self.enabled:
            return
        
        if key in self.cache:
            self.cache.move_to_end(key)
        elif len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
        
        self.cache[key] = {'data': value, 'timestamp': time()}
    
    def clear(self):
        self.cache.clear()


cache = SearchCache()
