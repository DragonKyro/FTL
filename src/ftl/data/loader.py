"""YAML content loader.

Pure I/O: discover .yaml files in a directory, parse them, validate them
against a pydantic schema. Registration into the in-memory `Registry`
happens in `registry.py`.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class ContentLoadError(Exception):
    """Raised when a YAML file fails to parse or validate."""


def load_yaml(path: Path) -> object:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_def(path: Path, schema: type[T]) -> T:
    try:
        raw = load_yaml(path)
    except yaml.YAMLError as e:
        raise ContentLoadError(f"{path}: YAML parse error: {e}") from e
    if not isinstance(raw, dict):
        raise ContentLoadError(f"{path}: top-level YAML must be a mapping")
    try:
        return schema.model_validate(raw)
    except ValidationError as e:
        raise ContentLoadError(f"{path}: schema validation failed:\n{e}") from e


def iter_yaml_files(root: Path) -> Iterator[Path]:
    if not root.exists():
        return
    yield from sorted(root.rglob("*.yaml"))
    yield from sorted(root.rglob("*.yml"))
