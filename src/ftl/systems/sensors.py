"""SensorsSystem — reveals enemy ship interior; sees own ship when ionized."""

from __future__ import annotations

from ftl.systems.system import System


class SensorsSystem(System):
    name = "sensors"
