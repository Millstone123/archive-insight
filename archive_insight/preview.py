from __future__ import annotations

import webbrowser
from pathlib import Path


def warm_preview_profile(path: Path) -> int:
    link = path.read_text(encoding="ascii").strip()
    if "://" not in link:
        raise ValueError("preview link must be a URI")
    return 0 if webbrowser.open(link, new=0, autoraise=True) else 1
