# src/structures/hash_map.py
"""
Custom HashMap implementation for station data caching.
Provides O(1) average lookup time for station information.
"""
from typing import Generic, TypeVar, Optional, List, Tuple

K = TypeVar('K')
V = TypeVar('V')

class HashMap(Generic[K, V]):
    """
    Hash map implementation using separate chaining.
    Use case: Cache station metadata for fast O(1) lookup by station_id.
    """
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.size = 0
        # Array of buckets (lists for collision handling)
        self.buckets: List[List[Tuple[K, V]]] = [[] for _ in range(capacity)]
    
    def _hash(self, key: K) -> int:
        """Compute hash index for key."""
        return hash(key) % self.capacity
    
    def put(self, key: K, value: V) -> None:
        """Insert or update key-value pair. O(1) average"""
        index = self._hash(key)
        bucket = self.buckets[index]
        
        # Update existing key
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        
        # Add new key
        bucket.append((key, value))
        self.size += 1
    
    def get(self, key: K) -> Optional[V]:
        """Retrieve value by key. O(1) average"""
        index = self._hash(key)
        bucket = self.buckets[index]
        
        for k, v in bucket:
            if k == key:
                return v
        return None
    
    def remove(self, key: K) -> bool:
        """Remove key-value pair. O(1) average"""
        index = self._hash(key)
        bucket = self.buckets[index]
        
        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self.size -= 1
                return True
        return False
    
    def contains(self, key: K) -> bool:
        """Check if key exists."""
        return self.get(key) is not None
