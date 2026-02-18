"""
window.py
~~~~~~~~~
ZeXisTourWindow — the main AdwApplicationWindow that hosts the tour.

Structure
---------
AdwApplicationWindow
└── Gtk.Box (vertical)
    ├── AdwHeaderBar
    └── Gtk.Box (content, vertical, vexpand)
        ├── Gtk.Stack  ← slides rendered here with animated transitions
        ├── Gtk.Box    ← dot-style progress indicator
        └── Gtk.Box    ← Previous / Next / Start buttons

Navigation
----------
- Previous / Next navigate through the Gtk.Stack using slide-right / slide-left
  crossfade transitions (Gtk.StackTransitionType).
- On the final slide the Next button is replaced with "Start Using ZeXis".
- Clicking "Start Using ZeXis" writes the completion flag and quits the app.

First-run flag
--------------
Delegated to main.py:mark_completed(); we import and call it here on finish.
"""

from __future__ import annotations

import os
from typing import List

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib

from ui.slide_loader import SlideData, load_slides
from ui.slide_page import build_slide_page

# Import the completion helper from its own dedicated module.
# This avoids a circular import (main → window → main).
from completion import mark_completed as _mark_completed


TRANSITION_DURATION_MS = 350   # milliseconds for the stack slide animation
WINDOW_DEFAULT_WIDTH   = 720
WINDOW_DEFAULT_HEIGHT  = 560


class ZeXisTourWindow(Adw.ApplicationWindow):
    """
    Main tour window.

    Parameters
    ----------
    application : Adw.Application
    app_dir     : Absolute path to the project root (used to locate assets/).
    """

    def __init__(self, application: Adw.Application, app_dir: str, **kwargs):
        super().__init__(application=application, **kwargs)

        self._app_dir = app_dir
        self._current_index: int = 0

        # ── Load slides ──────────────────────────────────────────────────
        slides_json = os.path.join(app_dir, "slides.json")
        assets_dir  = os.path.join(app_dir, "assets")
        self._slides: List[SlideData] = load_slides(slides_json, assets_dir)

        # ── Window properties ────────────────────────────────────────────
        self.set_title("ZeXis Tour")
        self.set_default_size(WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT)
        self.set_resizable(True)
        # Prevent the window from being smaller than a comfortable minimum.
        self.set_size_request(480, 420)

        # ── Build UI ─────────────────────────────────────────────────────
        self._build_ui()
        self._update_navigation()

    # ──────────────────────────────────────────────────────────────────────
    # UI construction
    # ──────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        """Assemble the complete widget hierarchy."""

        # Root box — stacks header + content vertically.
        root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # ── Header bar ───────────────────────────────────────────────────
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(True)
        header.set_show_start_title_buttons(True)
        # Keep the header title-less; slide titles live in the slide itself.
        header.set_title_widget(Gtk.Label())
        root_box.append(header)

        # ── Content area ─────────────────────────────────────────────────
        content_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=0,
            vexpand=True,
        )
        root_box.append(content_box)

        # ── Gtk.Stack (the slide carousel) ───────────────────────────────
        self._stack = Gtk.Stack()
        self._stack.set_transition_duration(TRANSITION_DURATION_MS)
        self._stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
        self._stack.set_vexpand(True)
        self._stack.set_hexpand(True)
        content_box.append(self._stack)

        # Populate the stack with one child per slide.
        for slide in self._slides:
            page_widget = build_slide_page(slide)
            self._stack.add_named(page_widget, slide.id)

        # ── Progress dots ─────────────────────────────────────────────────
        dots_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
            halign=Gtk.Align.CENTER,
        )
        dots_box.set_margin_top(12)
        dots_box.set_margin_bottom(12)
        self._dots: List[Gtk.Widget] = []
        for i, _ in enumerate(self._slides):
            dot = Gtk.Label(label="●")
            dot.add_css_class("dim-label")
            dots_box.append(dot)
            self._dots.append(dot)
        content_box.append(dots_box)

        # ── Navigation bar ────────────────────────────────────────────────
        nav_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12,
            halign=Gtk.Align.CENTER,
        )
        nav_box.set_margin_top(0)
        nav_box.set_margin_bottom(32)
        nav_box.set_margin_start(24)
        nav_box.set_margin_end(24)

        # Previous button
        self._btn_prev = Gtk.Button(label="Previous")
        self._btn_prev.add_css_class("pill")
        self._btn_prev.connect("clicked", self._on_prev_clicked)
        nav_box.append(self._btn_prev)

        # Spacer
        spacer = Gtk.Box(hexpand=True)
        nav_box.append(spacer)

        # Next button (hidden on final slide)
        self._btn_next = Gtk.Button(label="Next")
        self._btn_next.add_css_class("pill")
        self._btn_next.add_css_class("suggested-action")
        self._btn_next.connect("clicked", self._on_next_clicked)
        nav_box.append(self._btn_next)

        # Finish button (visible only on final slide)
        self._btn_finish = Gtk.Button(label="Start Using ZeXis")
        self._btn_finish.add_css_class("pill")
        self._btn_finish.add_css_class("suggested-action")
        self._btn_finish.connect("clicked", self._on_finish_clicked)
        self._btn_finish.set_visible(False)
        nav_box.append(self._btn_finish)

        content_box.append(nav_box)

        # ── Set root content ──────────────────────────────────────────────
        self.set_content(root_box)

    # ──────────────────────────────────────────────────────────────────────
    # Navigation helpers
    # ──────────────────────────────────────────────────────────────────────

    def _go_to(self, index: int, direction: str = "forward") -> None:
        """
        Switch the stack to the slide at *index*.

        Parameters
        ----------
        direction : "forward" or "backward" — controls the slide animation.
        """
        if index < 0 or index >= len(self._slides):
            return

        # Choose the appropriate slide direction for the animation.
        if direction == "forward":
            self._stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
        else:
            self._stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)

        self._current_index = index
        self._stack.set_visible_child_name(self._slides[index].id)
        self._update_navigation()

    def _update_navigation(self) -> None:
        """Sync button visibility/sensitivity and progress dots to current index."""
        idx      = self._current_index
        total    = len(self._slides)
        is_first = idx == 0
        is_last  = idx == total - 1

        # Previous button: disabled on the first slide.
        self._btn_prev.set_sensitive(not is_first)

        # Next vs Finish: swap based on whether we are on the last slide.
        self._btn_next.set_visible(not is_last)
        self._btn_finish.set_visible(is_last)

        # Update progress dots: active dot is full opacity; others are dimmed.
        for i, dot in enumerate(self._dots):
            if i == idx:
                dot.remove_css_class("dim-label")
                dot.add_css_class("accent")
            else:
                dot.remove_css_class("accent")
                dot.add_css_class("dim-label")

    # ──────────────────────────────────────────────────────────────────────
    # Signal handlers
    # ──────────────────────────────────────────────────────────────────────

    def _on_prev_clicked(self, _button: Gtk.Button) -> None:
        self._go_to(self._current_index - 1, direction="backward")

    def _on_next_clicked(self, _button: Gtk.Button) -> None:
        self._go_to(self._current_index + 1, direction="forward")

    def _on_finish_clicked(self, _button: Gtk.Button) -> None:
        """Mark the tour complete and close the application."""
        _mark_completed()
        # Use GLib.idle_add to ensure the UI has a chance to render before
        # we quit — avoids a flash of unstyled content on close.
        GLib.idle_add(self.get_application().quit)