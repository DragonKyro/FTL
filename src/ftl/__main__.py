"""`python -m ftl` entry point."""

from __future__ import annotations

import arcade

from ftl.app import FTLApp


def main() -> None:
    app = FTLApp()
    app.setup()
    arcade.run()


if __name__ == "__main__":
    main()
