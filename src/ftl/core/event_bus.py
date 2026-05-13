"""Lightweight typed publish/subscribe for cross-system communication.

Handlers are keyed by event class. Publish dispatches to every handler
registered for the exact runtime type of the event.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")
Handler = Callable[[T], None]


class EventBus:
    """Subscribe handlers by event type; publish event instances."""

    def __init__(self) -> None:
        self._handlers: dict[type, list[Callable[[Any], None]]] = defaultdict(list)

    def subscribe(self, event_type: type[T], handler: Handler[T]) -> None:
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: type[T], handler: Handler[T]) -> None:
        handlers = self._handlers.get(event_type)
        if handlers and handler in handlers:
            handlers.remove(handler)

    def publish(self, event: object) -> None:
        for handler in list(self._handlers.get(type(event), [])):
            handler(event)

    def clear(self) -> None:
        self._handlers.clear()
