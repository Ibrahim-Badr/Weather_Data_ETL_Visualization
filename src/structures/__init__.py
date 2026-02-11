# src/structures/__init__.py
"""
Custom data structures for Weather ETL project.

Structures:
- LinkedList: Chronological weather record storage (FIFO order)
- Queue: ETL job processing pipeline (station processing order)
- HashMap: Station metadata caching (O(1) lookup)
"""
from .linked_list import LinkedList
from .queue import Queue
from .hash_map import HashMap

__all__ = ['LinkedList', 'Queue', 'HashMap']
