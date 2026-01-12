import os
import pickle
import json
import hashlib

class DiskCache:
    """
    A convenient disk cache that stores key-value pairs on disk.
    Useful for querying LLM API.
    """
    def __init__(self, cache_dir='cache', load_cache=True):
        self.cache_dir = cache_dir
        self.data = {}
        self.enabled = bool(load_cache)
        
        if not self.enabled:
            return
        
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        else:
            self._load_cache()

    def _generate_filename(self, key):
        key_str = json.dumps(key, sort_keys=True)
        key_hash = hashlib.sha1(key_str.encode('utf-8')).hexdigest()
        return f"{key_hash}.pkl"

    def _load_cache(self):
        for filename in os.listdir(self.cache_dir):
            if not filename.endswith('.pkl'):
                continue
            with open(os.path.join(self.cache_dir, filename), 'rb') as file:
                try:
                    key, value = pickle.load(file)
                    self.data[json.dumps(key, sort_keys=True)] = value
                except (pickle.UnpicklingError, EOFError) as e:
                    print(f"Warning: Could not load cache file {filename}. Skipping. Error: {e}")

    def _save_to_disk(self, key, value):
        filename = self._generate_filename(key)
        with open(os.path.join(self.cache_dir, filename), 'wb') as file:
            pickle.dump((key, value), file)

    def __setitem__(self, key, value):
        if not self.enabled:
            return
        str_key = json.dumps(key, sort_keys=True)
        self.data[str_key] = value
        self._save_to_disk(key, value)

    def __getitem__(self, key):
        str_key = json.dumps(key, sort_keys=True)
        return self.data[str_key]
    
    def __contains__(self, key):
        if not self.enabled:
            return False
        str_key = json.dumps(key, sort_keys=True)
        return str_key in self.data

    def __repr__(self):
        return repr(self.data)
