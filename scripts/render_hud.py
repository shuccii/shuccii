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

from hud import panels, widgets                          # noqa: E402
from hud.theme import PALETTES                          # noqa: E402
from hud.data import ROOT, collect                       # noqa: E402

OUT = ROOT / "assets"


def main() -> int:
    login = os.environ.get("HUD_LOGIN", "shuccii")
    t = collect(login, os.environ.get("GITHUB_TOKEN"))

    print(f"login={t.login} live={t.live} contributions={t.contributions} "
          f"commits={t.commits} repos={t.repos} stars={t.stars} "
          f"weeks={len(t.weeks)} peak={t.peak_week} sha={t.sha}")

    if not t.live and (OUT / "dark" / "header.svg").exists():
        print("telemetry unavailable — leaving the committed panels untouched")
        return 0

    # one file per palette; the README picks between them with
    # <picture><source media="(prefers-color-scheme: ...)">
    for pal in PALETTES:
        d = OUT / pal.key
        d.mkdir(parents=True, exist_ok=True)
        for name, svg in {
            "header.svg": panels.header(t, pal),
            "command-strip.svg": panels.command_strip(t, pal),
            "divider.svg": panels.divider(pal),
            "footer.svg": panels.footer(t, pal),
            "topbar.svg": widgets.topbar(t, pal),
            "system.svg": widgets.system(t, pal),
            "radar.svg": widgets.radar(t, pal),
            "globe.svg": widgets.globe(t, pal),
            "pulse.svg": widgets.pulse(t, pal),
            "languages.svg": widgets.languages(t, pal),
            "log.svg": widgets.log(t, pal),
        }.items():
            (d / name).write_text(svg)
            print(f"rendered {pal.key}/{name} ({len(svg)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
