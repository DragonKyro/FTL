"""Factory: build an `Augment` instance from an `AugmentDef`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ftl.augments.augment import Augment, AugmentStats
from ftl.augments.effects import effect_for

if TYPE_CHECKING:
    from ftl.data.schemas import AugmentDef


def augment_from_def(definition: AugmentDef) -> Augment | None:
    effect = effect_for(definition.effect_id, definition.value)
    if effect is None:
        return None
    stats = AugmentStats(
        id=definition.id,
        name=definition.name,
        effect_id=definition.effect_id,
        value=definition.value,
        rarity=definition.rarity,
    )
    return Augment(stats=stats, effect=effect)
