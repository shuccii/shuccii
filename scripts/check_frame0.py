#!/usr/bin/env python3
"""Fail if any panel would render blank where SVG animation is frozen.

Several renderers (GitHub's own mobile views, thumbnailers, anything that
rasterises an SVG once) paint frame 0 and stop. An animation that starts from
`width=0`, `opacity=0` or an empty `stroke-dasharray` then shows nothing at all
— which is how a fully drawn chart turns into an empty box. This has bitten the
profile twice, so it is checked rather than remembered.

A group that cycles between alternatives is fine as long as one of the
alternatives is visible on the first frame.
"""
from __future__ import annotations

import glob
import sys
import xml.etree.ElementTree as ET

NS = "{http://www.w3.org/2000/svg}"
HIDING = {"width", "height", "opacity", "fill-opacity", "stroke-dasharray", "stroke-opacity"}


def first_value(values: str) -> float | None:
    head = values.split(";")[0].strip().replace(",", " ").split()
    if not head:
        return None
    try:
        return float(head[0])
    except ValueError:
        return None


def audit(path: str) -> list[str]:
    tree = ET.parse(path)
    parents = {child: parent for parent in tree.iter() for child in parent}
    problems = []
    for el in tree.iter(f"{NS}animate"):
        attr, values = el.get("attributeName"), el.get("values")
        if not attr or not values or attr not in HIDING:
            continue
        if first_value(values) != 0:
            continue
        target = parents.get(el)
        if target is None:
            continue
        # one of a cycling set: fine, provided a sibling starts visible
        siblings = [s for s in parents.get(target, []) if s is not target] if target in parents else []
        if any(s.get("opacity") not in (None, "0") for s in siblings):
            continue
        problems.append(f"{path}: <{target.tag.replace(NS, '')}> animates {attr} from 0 "
                        f"with no visible alternative")
    return problems


def main() -> int:
    files = sorted(glob.glob("assets/**/*.svg", recursive=True))
    if not files:
        print("no SVGs found", file=sys.stderr)
        return 1
    problems = [p for f in files for p in audit(f)]
    print(f"frame-0 audit: {len(files)} files")
    for p in problems:
        print(f"  {p}")
    if problems:
        print(f"{len(problems)} element(s) would be invisible on a frozen first frame")
        return 1
    print("  every panel is complete on its first frame")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
