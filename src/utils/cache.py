from collections import OrderedDict
import time


class TTLCache:

    def __init__(self, ttl: float = 30, max_size: int = 100) -> None:
        """
        A minimal in-memory TTL cache with FIFO eviction.

        Args:
            ttl (float): Time in seconds before an entry is considered stale. Defaults to 30.
            max_size (int): Maximum number of entries to retain. Defaults to 100.
        """
        self.ttl = ttl
        self.max_size = max_size
        self._store: OrderedDict[str, tuple[float, dict]] = OrderedDict()


    def get(self, key: str) -> dict | None:
        """
        Returns the cached value for a key, or None if missing or expired.

        Args:
            key (str): The cache key.

        Returns:
            dict | None: The cached value, or None if missing/expired.
        """
        entry = self._store.get(key)
        if not entry:
            return None

        timestamp, value = entry
        if time.monotonic() - timestamp >= self.ttl:
            del self._store[key]
            return None

        return value


    def cleanup(self) -> int:
        """
        Removes all expired entries from the cache.

        Returns:
            int: The number of entries removed.
        """
        now = time.monotonic()
        expired_keys = [key for key, (timestamp, _) in self._store.items() if now - timestamp >= self.ttl]

        for key in expired_keys:
            del self._store[key]

        return len(expired_keys)


    def set(self, key: str, value: dict) -> None:
        """
        Stores a value under the given key, evicting the oldest entry if over capacity.

        Args:
            key (str): The cache key.
            value (dict): The value to store.
        """
        self._store[key] = (time.monotonic(), value)
        self._store.move_to_end(key)

        if len(self._store) > self.max_size:
            self._store.popitem(last=False)
