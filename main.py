#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZeXis Tour — Onboarding application for the ZeXis Linux distribution.
Built with Python 3, GTK4, and libadwaita.

First-run detection:
  On completion, a flag file is written to ~/.config/.zexis_tour_completed.
  At startup, if this file exists, the application exits immediately without
  showing any window. This ensures the tour only runs once per user account.
"""

import sys
import os

# ---------------------------------------------------------------------------
# Ensure the project root is on sys.path so local packages are always found,
# regardless of the working directory the script is launched from.
# ---------------------------------------------------------------------------
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

# ---------------------------------------------------------------------------
# First-run check — uses completion.py, a dependency-free helper module.
# Checked before importing GTK so we exit in ~1 ms on repeat launches.
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# GTK / libadwaita imports
# ---------------------------------------------------------------------------
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio

from ui.window import ZeXisTourWindow


class ZeXisTourApp(Adw.Application):
    """Top-level application object."""

    APP_ID = "org.zexis.Tour"

    def __init__(self):
        super().__init__(
            application_id=self.APP_ID,
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self.connect("activate", self._on_activate)

    def _on_activate(self, app: "ZeXisTourApp") -> None:
        win = ZeXisTourWindow(application=app, app_dir=APP_DIR)
        win.present()


def main() -> int:
    app = ZeXisTourApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())