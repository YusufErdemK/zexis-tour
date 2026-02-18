"""
slide_page.py
~~~~~~~~~~~~~
Builds a single slide widget from a SlideData instance.

Layout (vertical, centred):
  ┌─────────────────────────────┐
  │  [icon or image — large]    │
  │  Title                      │
  │  Description (wrapping)     │
  └─────────────────────────────┘
"""

from __future__ import annotations

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GdkPixbuf, Gio

from ui.slide_loader import SlideData


def build_slide_page(slide: SlideData) -> Gtk.Widget:
    """
    Return a Gtk.Box containing all visual elements for *slide*.

    The widget is intentionally stateless and side-effect-free so that it can
    be recreated or placed inside any container.
    """

    # Outer container — vertically stacked, centred, with comfortable padding.
    page_box = Gtk.Box(
        orientation=Gtk.Orientation.VERTICAL,
        spacing=24,
        halign=Gtk.Align.CENTER,
        valign=Gtk.Align.CENTER,
        hexpand=True,
        vexpand=True,
    )
    page_box.set_margin_top(48)
    page_box.set_margin_bottom(48)
    page_box.set_margin_start(48)
    page_box.set_margin_end(48)

    # ── Illustration / icon ───────────────────────────────────────────────
    if slide.image_path:
        # Prefer a raster image from the assets directory.
        picture = Gtk.Picture.new_for_filename(slide.image_path)
        picture.set_size_request(200, 200)
        picture.set_can_shrink(True)
        picture.set_content_fit(Gtk.ContentFit.CONTAIN)
        picture.set_halign(Gtk.Align.CENTER)
        page_box.append(picture)
    elif slide.icon:
        # Fall back to a themed icon rendered at a large pixel size.
        icon_image = Gtk.Image.new_from_icon_name(slide.icon)
        icon_image.set_pixel_size(96)
        icon_image.set_halign(Gtk.Align.CENTER)
        # Add the "dim-label" style so the icon inherits the accent colour
        # from the active theme rather than being plain grey.
        icon_image.add_css_class("accent")
        page_box.append(icon_image)

    # ── Title ─────────────────────────────────────────────────────────────
    title_label = Gtk.Label(label=slide.title)
    title_label.set_halign(Gtk.Align.CENTER)
    title_label.set_justify(Gtk.Justification.CENTER)
    title_label.set_wrap(True)
    title_label.set_max_width_chars(40)
    # Use the Adwaita display heading style for visual weight.
    title_label.add_css_class("title-1")
    page_box.append(title_label)

    # ── Description ───────────────────────────────────────────────────────
    desc_label = Gtk.Label(label=slide.description)
    desc_label.set_halign(Gtk.Align.CENTER)
    desc_label.set_justify(Gtk.Justification.CENTER)
    desc_label.set_wrap(True)
    desc_label.set_max_width_chars(52)
    desc_label.add_css_class("body")
    # Slightly muted colour so description reads as secondary vs the title.
    desc_label.add_css_class("dim-label")
    page_box.append(desc_label)

    return page_box
