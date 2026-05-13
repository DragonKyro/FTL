"""Story event runtime.

An Event is a text encounter with one or more Choices. Each Choice resolves
to an Outcome that applies effects (scrap, fuel, hull damage, combat
start, story flags). Authoring lives in YAML under `story/events/`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ftl.events.choice import Choice
from ftl.events.outcome import Outcome


@dataclass
class Event:
    id: str
    text: str
    choices: list[Choice] = field(default_factory=list)
    outcomes: dict[str, Outcome] = field(default_factory=dict)

    def resolve(self, choice_index: int) -> Outcome | None:
        if choice_index < 0 or choice_index >= len(self.choices):
            return None
        chosen = self.choices[choice_index]
        if chosen.outcome_id is None:
            return None
        return self.outcomes.get(chosen.outcome_id)
