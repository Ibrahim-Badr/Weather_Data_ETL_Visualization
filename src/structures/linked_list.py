# src/structures/linked_list.py
"""
Linked List implementation for storing weather records chronologically.
Useful for maintaining insertion order and efficient insertion/deletion.
"""
from typing import Optional, Generic, TypeVar
from dataclasses import dataclass

T = TypeVar('T')


@dataclass
class Node(Generic[T]):
    """Node in a linked list."""
    data: T
    next: Optional['Node[T]'] = None


class LinkedList(Generic[T]):
    """
    Singly linked list implementation.
    Use case: Store weather records in chronological order.
    """

    def __init__(self):
        self.head: Optional[Node[T]] = None
        self.size: int = 0

    def append(self, data: T) -> None:
        """Add element to end of list. O(n)"""
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self.size += 1

    def prepend(self, data: T) -> None:
        """Add element to beginning of list. O(1)"""
        new_node = Node(data, self.head)
        self.head = new_node
        self.size += 1

    def to_list(self) -> list[T]:
        """Convert to Python list."""
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result
