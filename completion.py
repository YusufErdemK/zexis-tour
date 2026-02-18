"""
completion.py
~~~~~~~~~~~~~
Handles the first-run flag file.
Kept in its own module so both main.py and ui/window.py can import it
without creating a circular dependency.
"""

import os

FLAG_FILE = os.path.expanduser("~/.config/.zexis_tour_completed")


def already_completed() -> bool:
    """Return True if the user has already completed the tour."""
    return os.path.isfile(FLAG_FILE)


def mark_completed() -> None:
    """Write the flag file so the tour won't launch again."""
    os.makedirs(os.path.dirname(FLAG_FILE), exist_ok=True)
    with open(FLAG_FILE, "w") as fh:
        fh.write("completed\n")