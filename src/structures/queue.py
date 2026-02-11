# src/structures/queue.py
"""
Queue implementation for ETL job processing.
FIFO structure for managing station processing order.
"""
from typing import Generic, TypeVar, Optional
from collections import deque

T = TypeVar('T')

class Queue(Generic[T]):
    """
    FIFO Queue implementation using deque.
    Use case: Process weather stations in order (First In, First Out).
    """
    def __init__(self):
        self._items: deque[T] = deque()
    
    def enqueue(self, item: T) -> None:
        """Add item to end of queue. O(1)"""
        self._items.append(item)
    
    def dequeue(self) -> Optional[T]:
        """Remove and return item from front of queue. O(1)"""
        if self.is_empty():
            return None
        return self._items.popleft()
    
    def peek(self) -> Optional[T]:
        """View front item without removing. O(1)"""
        if self.is_empty():
            return None
        return self._items[0]
    
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._items) == 0
    
    def size(self) -> int:
        """Get queue size."""
        return len(self._items)
