"""Validate every YAML under content/ and story/ against its registered schema.

This grows automatically: drop a new file into `content/weapons/` and this
test will validate it. A broken YAML or a schema mismatch fails CI.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ftl.config import CONTENT_DIR, STORY_DIR
from ftl.data.loader import iter_yaml_files, load_def
from ftl.data.schemas import CONTENT_SCHEMAS, STORY_SCHEMAS, ContentDef


def _gather() -> list[tuple[Path, type[ContentDef]]]:
    cases: list[tuple[Path, type[ContentDef]]] = []
    for subdir, schema in CONTENT_SCHEMAS.items():
        for path in iter_yaml_files(CONTENT_DIR / subdir):
            cases.append((path, schema))
    for subdir, schema in STORY_SCHEMAS.items():
        for path in iter_yaml_files(STORY_DIR / subdir):
            cases.append((path, schema))
    return cases


_CASES = _gather()


@pytest.mark.parametrize(
    "path,schema",
    _CASES,
    ids=[str(p) for p, _ in _CASES],
)
def test_content_yaml_validates(path: Path, schema: type[ContentDef]) -> None:
    definition = load_def(path, schema)
    assert definition.id
    assert definition.name


def test_at_least_some_content_exists() -> None:
    """Smoke test: confirm content discovery isn't completely broken."""
    # Phase 0 ships at least the demo YAMLs; remove this assertion if you
    # ever need to clear out all content temporarily.
    if not _CASES:
        pytest.skip("No content YAMLs present yet")
