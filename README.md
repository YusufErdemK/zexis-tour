# ZeXis Tour

A native GTK4 + libadwaita onboarding application for the ZeXis Linux distribution.

## Requirements

| Dependency | Package (Debian/Ubuntu) |
|---|---|
| Python 3.10+ | `python3` |
| GTK 4 | `libgtk-4-1` |
| libadwaita 1.x | `libadwaita-1-0` |
| PyGObject | `python3-gi` |
| GObject introspection data | `gir1.2-gtk-4.0` `gir1.2-adw-1` |

Install everything at once:
```bash
sudo apt install python3 python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 libadwaita-1-0
```

## Running

```bash
cd zexis-tour
python3 main.py
```

To test the first-run gate:
```bash
# Simulate completion
touch ~/.config/.zexis_tour_completed
python3 main.py   # exits immediately, no window

# Reset so the tour shows again
rm ~/.config/.zexis_tour_completed
python3 main.py
```

## Project Structure

```
zexis-tour/
├── main.py               # Entry point; first-run detection; app lifecycle
├── slides.json           # All slide content — edit this to change the tour
├── zexis-tour.desktop    # XDG autostart file for the desktop session
├── assets/               # Optional slide images (PNG/SVG)
│   └── README            # Drop image files here; reference in slides.json
└── ui/
    ├── __init__.py
    ├── slide_loader.py   # Parses slides.json → list[SlideData]
    ├── slide_page.py     # Builds a GTK widget for one slide
    └── window.py         # AdwApplicationWindow; stack navigation; dots
```

## How First-Run Detection Works

```
Login / Session Start
        │
        ▼
XDG Autostart fires zexis-tour.desktop
        │
        ▼
main.py starts (pure Python, no GTK yet)
        │
        ├─── ~/.config/.zexis_tour_completed exists?
        │           YES → sys.exit(0)  ← ~1ms, invisible
        │           NO  ↓
        ▼
GTK / libadwaita initialised
Window presented → user clicks through tour
        │
        ▼
"Start Using ZeXis" clicked
        │
        ├── mark_completed() writes ~/.config/.zexis_tour_completed
        └── app.quit()

Next login → flag file found → silent exit
```

**Why not delete the .desktop file?**
The `.desktop` entry may live in `/etc/xdg/autostart/` (system-wide), which
requires root to modify. Writing a flag file to `~/.config/` requires only
normal user permissions and works even when the `.desktop` entry is managed by
the distro's package manager.

## Customising Slides

Edit `slides.json`. Each slide object supports:

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | ✅ | Unique identifier (used as the stack page name) |
| `title` | string | ✅ | Large heading text |
| `description` | string | ✅ | Body text, wraps automatically |
| `icon` | string | — | Freedesktop icon name (e.g. `"security-high-symbolic"`) |
| `image_path` | string | — | Path relative to `assets/` (overrides icon if present) |
| `accent` | string | — | Colour hint: `blue`, `green`, `orange`, `purple`, `teal` |
| `is_final` | boolean | — | Set `true` on the last slide to show the finish button |

Only the last slide with `"is_final": true` shows the "Start Using ZeXis" button.

## Installing the Autostart Entry

**System-wide (all new users):**
```bash
sudo cp zexis-tour.desktop /etc/xdg/autostart/
sudo cp -r . /usr/share/zexis-tour/
sudo chmod +x /usr/share/zexis-tour/main.py
```

**Per-user:**
```bash
cp zexis-tour.desktop ~/.config/autostart/
```
Then update the `Exec=` path in the `.desktop` file to point to your local copy.

## Architecture Notes

- **`main.py`** — thin entry point. Performs the O(1) flag-file check before
  any GTK import; creates `ZeXisTourApp`; runs the GLib main loop.
- **`slide_loader.py`** — pure data layer. No GTK imports. Easy to unit-test.
- **`slide_page.py`** — stateless view builder. Given a `SlideData`, returns a
  `Gtk.Widget`. Keeps rendering logic out of the window class.
- **`window.py`** — `AdwApplicationWindow` subclass that owns the `Gtk.Stack`,
  progress dots, and navigation buttons. Delegates slide construction to
  `build_slide_page()` and completion signalling to `main.mark_completed()`.
