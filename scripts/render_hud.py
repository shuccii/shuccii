#!/usr/bin/env python3
"""Regenerate every HUD panel from live repository telemetry.

Run with GITHUB_TOKEN set (the Actions token is enough). Without one the panels
still render, but the numbers fall back to zero rather than being invented.
"""
from __future__ import annotations

import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from hud import panels                                   # noqa: E402
from hud.data import ROOT, collect                       # noqa: E402

OUT = ROOT / "assets"


def main() -> int:
    login = os.environ.get("HUD_LOGIN", "shuccii")
    t = collect(login, os.environ.get("GITHUB_TOKEN"))

    print(f"login={t.login} live={t.live} contributions={t.contributions} "
          f"commits={t.commits} repos={t.repos} stars={t.stars} "
          f"weeks={len(t.weeks)} peak={t.peak_week} sha={t.sha}")

    if not t.live and (OUT / "jarvis-header.svg").exists():
        print("telemetry unavailable — leaving the committed panels untouched")
        return 0

    OUT.mkdir(parents=True, exist_ok=True)
    for name, svg in {
        "jarvis-header.svg": panels.header(t),
        "command-strip.svg": panels.command_strip(t),
        "divider.svg": panels.divider(),
        "jarvis-footer.svg": panels.footer(t),
    }.items():
        (OUT / name).write_text(svg)
        print(f"rendered {name} ({len(svg)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
