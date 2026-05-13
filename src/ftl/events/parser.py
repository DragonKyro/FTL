"""Parse story event YAML into runtime Event objects.

Phase-0 stub: takes an `EventDef` (from `data.schemas`) and produces an
`Event`. Outcome references and quest chaining will be richer in Phase 4.
"""

from __future__ import annotations

from ftl.data.schemas import EventDef
from ftl.events.choice import Choice
from ftl.events.event import Event


def event_from_def(definition: EventDef) -> Event:
    choices = [
        Choice(text=c.text, outcome_id=c.outcome_id) for c in definition.choices
    ]
    return Event(id=definition.id, text=definition.text, choices=choices)
