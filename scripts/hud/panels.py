"""Draw the panels.

The centrepiece is not decoration: the ring around the core is the account's
last 12 months of contributions, one spoke per week, length and colour taken
from the real weekly totals. When the data changes the instrument changes.
"""
from __future__ import annotations

import math
from datetime import date

from .data import Telemetry
from .theme import ACCENT, HAIR, LINE, Palette, atmosphere, defs, frame

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def _pt(cx: float, cy: float, r: float, deg: float) -> tuple[float, float]:
    a = math.radians(deg - 90)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def _arc(cx: float, cy: float, r: float, a0: float, a1: float) -> str:
    x0, y0 = _pt(cx, cy, r, a0)
    x1, y1 = _pt(cx, cy, r, a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f"M{x0:.1f} {y0:.1f} A{r:.1f} {r:.1f} 0 {large} 1 {x1:.1f} {y1:.1f}"


def _level(v: int, peak: int) -> int:
    if v <= 0 or peak <= 0:
        return 0
    q = v / peak
    return 1 + min(3, int(q * 4 - 1e-9))


def _cells(p: Palette, x0: float, width: float, y_label: float, y_value: float,
           cells: list[tuple[str, str]], value_size: float = 19) -> str:
    out = []
    step = width / len(cells)
    for i, (label, value) in enumerate(cells):
        x = x0 + i * step
        if i:
            out.append(f'<line x1="{x-14:.1f}" y1="{y_label-11:.0f}" x2="{x-14:.1f}" '
                       f'y2="{y_value+5:.0f}" stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.55"/>')
        out.append(f'<text x="{x:.1f}" y="{y_label}" fill="{p.dim}" font-size="8.5" '
                   f'letter-spacing="2.2">{label}</text>')
        out.append(f'<text x="{x:.1f}" y="{y_value}" fill="{p.pale}" font-size="{value_size}" '
                   f'letter-spacing="0.4">{value}</text>')
    return "\n    ".join(out)


# --------------------------------------------------------------------------- header
def header(t: Telemetry, p: Palette) -> str:
    W, H, P = 900, 300, "h"
    CX, CY = 158, 150
    R_IN, R_MAX = 54, 116
    X0, XE = 312, 872

    weeks = t.weeks or [0] * 53
    peak = max(weeks) or 1
    n = len(weeks)

    spokes, ticks, labels = [], [], []
    seen_months: set[int] = set()
    for i, v in enumerate(weeks):
        deg = i * 360 / n
        lvl = _level(v, peak)
        # log scale: a handful of very busy weeks must not flatten the rest of
        # the year into stubs. Every week keeps a floor so the dial reads whole.
        frac = math.log1p(v) / math.log1p(peak)
        r_out = R_IN + 6 + (R_MAX - R_IN - 6) * frac
        x0, y0 = _pt(CX, CY, R_IN, deg)
        x1, y1 = _pt(CX, CY, r_out, deg)
        spokes.append(
            f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
            f'stroke="{p.ramp[lvl]}" stroke-width="2.4" stroke-linecap="round" '
            f'opacity="{0.7 if lvl == 0 else 0.95}"/>')

        if t.week_starts:
            m = date.fromisoformat(t.week_starts[i]).month
            if m not in seen_months and i > 0:
                seen_months.add(m)
                tx0, ty0 = _pt(CX, CY, R_MAX + 6, deg)
                tx1, ty1 = _pt(CX, CY, R_MAX + 11, deg)
                ticks.append(f'<line x1="{tx0:.1f}" y1="{ty0:.1f}" x2="{tx1:.1f}" y2="{ty1:.1f}" '
                             f'stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.85"/>')
                lx, ly = _pt(CX, CY, R_MAX + 19, deg)
                labels.append(f'<text x="{lx:.1f}" y="{ly+2.4:.1f}" fill="{p.dim}" font-size="6.6" '
                              f'letter-spacing="1.1" text-anchor="middle" opacity="0.9">{MONTHS[m-1]}</text>')

    fringe = "" if not p.aberration else (
        f'<text x="{X0-0.7}" y="122" fill="#ff4d4d" opacity="{p.aberration}">{t.name}</text>'
        f'<text x="{X0+0.7}" y="122" fill="#3ee6ff" opacity="{p.aberration}">{t.name}</text>')

    pi = weeks.index(peak)
    pdeg = pi * 360 / n
    px0, py0 = _pt(CX, CY, R_MAX + 4, pdeg)
    px1, py1 = _pt(CX, CY, R_MAX + 12, pdeg)
    plx, ply = _pt(CX, CY, R_MAX + 26, pdeg)
    peak_marker = (
        f'<line x1="{px0:.1f}" y1="{py0:.1f}" x2="{px1:.1f}" y2="{py1:.1f}" '
        f'stroke="{p.gold}" stroke-width="{LINE}"/>'
        f'<circle cx="{px1:.1f}" cy="{py1:.1f}" r="1.7" fill="{p.gold}"/>'
        f'<text x="{plx:.1f}" y="{ply+2.4:.1f}" fill="{p.gold}" font-size="6.6" '
        f'letter-spacing="1" text-anchor="middle">PEAK {peak}</text>')

    scale = "\n      ".join(
        f'<line x1="{XE+6}" y1="{y}" x2="{XE + 6 + (14 if i % 4 == 0 else 7)}" y2="{y}" '
        f'stroke="{p.dim}" stroke-width="{HAIR}" opacity="{0.85 if i % 4 == 0 else 0.45}"/>'
        for i, y in enumerate(range(74, 227, 9)))

    telemetry = _cells(p, X0, XE - X0, 200, 226, [
        ("COMMITS", f"{t.commits}"),
        ("PULL REQ", f"{t.prs}"),
        ("ISSUES", f"{t.issues}"),
        ("REPOS", f"{t.repos}"),
        ("STARS", f"{t.stars}"),
    ])

    live = (f'<text x="{XE}" y="272" text-anchor="end" fill="{p.cyan}" font-size="9" letter-spacing="1.8">LIVE'
            f'<animate attributeName="opacity" values="1;1;0.2;1" keyTimes="0;0.6;0.66;1" '
            f'dur="2.4s" repeatCount="indefinite"/></text>') if t.live else \
           f'<text x="{XE}" y="272" text-anchor="end" fill="{p.dim}" font-size="9" letter-spacing="1.8">CACHED</text>'

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{t.login} — {t.contributions} contributions in the last year">
<defs>{defs(P, W, H, p)}</defs>
<g clip-path="url(#{P}Clip)">
  <rect width="{W}" height="{H}" fill="url(#{P}Deep)"/>

  <!-- ============ CONTRIBUTION INSTRUMENT : one spoke per week ============ -->
  <g class="t">
    <circle cx="{CX}" cy="{CY}" r="{R_MAX+3}" fill="none" stroke="{p.faint}" stroke-width="{HAIR}" opacity="0.8"/>
    <circle cx="{CX}" cy="{CY}" r="{R_IN-4}" fill="none" stroke="{p.faint}" stroke-width="{HAIR}" opacity="0.8"/>
    <g>
      {chr(10).join("      " + s for s in spokes).strip()}
    </g>
    <g>
      {chr(10).join("      " + s for s in ticks).strip()}
    </g>
    <g>
      {chr(10).join("      " + s for s in labels).strip()}
    </g>

    <!-- busiest week of the year -->
    {peak_marker}

    <!-- read head sweeping the year -->
    <g>
      <animateTransform attributeName="transform" type="rotate" from="0 {CX} {CY}" to="360 {CX} {CY}" dur="24s" repeatCount="indefinite"/>
      <line x1="{CX}" y1="{CY-R_IN+6}" x2="{CX}" y2="{CY-R_MAX-4}" stroke="{p.cyan}" stroke-width="{LINE}" opacity="0.9" filter="url(#{P}Glow)"/>
      <circle cx="{CX}" cy="{CY-R_MAX-8}" r="1.8" fill="{p.gold}" filter="url(#{P}Glow)"/>
    </g>

    <!-- orbital planes -->
    <g opacity="0.55">
      <g><animateTransform attributeName="transform" type="rotate" from="0 {CX} {CY}" to="360 {CX} {CY}" dur="38s" repeatCount="indefinite"/>
        <ellipse cx="{CX}" cy="{CY}" rx="{R_MAX+16}" ry="34" fill="none" stroke="{p.dim}" stroke-width="{HAIR}"/></g>
      <g><animateTransform attributeName="transform" type="rotate" from="64 {CX} {CY}" to="424 {CX} {CY}" dur="52s" repeatCount="indefinite"/>
        <ellipse cx="{CX}" cy="{CY}" rx="{R_MAX+10}" ry="26" fill="none" stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.75"/></g>
    </g>

    <!-- core well -->
    <circle cx="{CX}" cy="{CY}" r="{R_IN-8}" fill="{p.bg_outer}"/>
    <circle cx="{CX}" cy="{CY}" r="{R_IN-8}" fill="none" stroke="{p.metal}" stroke-width="2.6" filter="url(#{P}Bevel)"/>
    <circle cx="{CX}" cy="{CY}" r="{R_IN-12}" fill="url(#{P}Core)" opacity="0.34">
      <animate attributeName="opacity" values="0.24;0.42;0.24" dur="4.6s" repeatCount="indefinite"/>
    </circle>
    <g fill="none" stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.85">
      <path d="{_arc(CX, CY, R_IN-15, 14, 106)}"/>
      <path d="{_arc(CX, CY, R_IN-15, 134, 226)}"/>
      <path d="{_arc(CX, CY, R_IN-15, 254, 346)}"/>
    </g>

    <text x="{CX}" y="{CY+4}" text-anchor="middle" fill="{p.ink}" font-size="27" letter-spacing="0.5">{t.contributions}</text>
    <text x="{CX}" y="{CY+19}" text-anchor="middle" fill="{p.dim}" font-size="6.8" letter-spacing="2.6">CONTRIBUTIONS</text>
    <text x="{CX}" y="{CY-24}" text-anchor="middle" fill="{p.dim}" font-size="6.4" letter-spacing="2.4">LAST 12 MONTHS</text>

  </g>

  <!-- ============ READOUT ============ -->
  <g class="t">
    <text x="{X0}" y="60" fill="{p.gold}" font-size="10.5" letter-spacing="4.2">GITHUB.COM / {t.login.upper()}</text>
    <text x="{XE}" y="60" fill="{p.dim}" font-size="10.5" letter-spacing="2.2" text-anchor="end">BRANCH {t.branch}</text>
    <line x1="{X0}" y1="70" x2="{XE}" y2="70" stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.5"/>

    <g font-size="38" letter-spacing="8.5">
      {fringe}
      <text x="{X0}" y="122" fill="{p.ink}">{t.name}</text>
    </g>

    <line x1="{X0}" y1="138" x2="{XE}" y2="138" stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.45"/>
    <line x1="{X0}" y1="138" x2="{X0+92}" y2="138" stroke="{p.gold}" stroke-width="{ACCENT}"/>

    <text x="{X0}" y="164" fill="#8ecfe6" font-size="11.5" letter-spacing="3">MATERIALS INFORMATICS &#183; MACHINE LEARNING &#183; FUSION</text>

    {telemetry}

    <line x1="{X0}" y1="248" x2="{XE}" y2="248" stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.45"/>
    <g font-size="9" letter-spacing="1.7" fill="{p.dim}">
      <text x="{X0}" y="272">SYNC {t.synced}Z</text>
      <text x="{X0+190}" y="272">HEAD {t.sha}</text>
      <text x="{X0+310}" y="272">PEAK {t.peak_week}/WK</text>
      <text x="{X0+420}" y="272">ACTIVE {t.active_weeks}/{n}</text>
    </g>
    {live}
  </g>

  <g>{scale}
    <line x1="{XE+4}" y1="74" x2="{XE+4}" y2="226" stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.6"/>
  </g>
{atmosphere(P, W, H, p)}
{frame(W, H, p)}
</g>
</svg>
'''


# --------------------------------------------------------------------------- command strip
def command_strip(t: Telemetry, p: Palette) -> str:
    """A terminal line that cycles real git/gh invocations and their answers."""
    W, H, P = 900, 54, "c"
    rows = [
        ("git remote -v", f"origin  github.com/{t.login}/{t.login}  (fetch)"),
        ("git log -1 --format=%h%d", f"{t.sha}  (HEAD -> {t.branch}, origin/{t.branch})"),
        ("git shortlog -sn --since=1.year", f"{t.commits}  {t.name.title()}"),
        ("gh api /users/{login} --jq .public_repos".replace("{login}", t.login), f"{t.repos}"),
    ]
    dur = len(rows) * 3.6
    keytimes = ";".join(f"{i/len(rows):.4f}" for i in range(len(rows)))

    lines = []
    for i, (cmd, out) in enumerate(rows):
        vals = ";".join("1" if j == i else "0" for j in range(len(rows)))
        anim = (f'<animate attributeName="opacity" dur="{dur}s" calcMode="discrete" '
                f'keyTimes="{keytimes}" values="{vals}" repeatCount="indefinite"/>')
        lines.append(
            f'<g opacity="{1 if i == 0 else 0}">{anim}'
            f'<text x="96" y="22" fill="{p.pale}" font-size="12.5" letter-spacing="0.4">{cmd}</text>'
            f'<text x="96" y="40" fill="{p.cyan_deep}" font-size="12.5" letter-spacing="0.4">{out}</text>'
            f'</g>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="git status readout">
<defs>{defs(P, W, H, p)}</defs>
<g clip-path="url(#{P}Clip)">
  <rect width="{W}" height="{H}" fill="url(#{P}Deep)"/>
  <line x1="78" y1="10" x2="78" y2="44" stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.6"/>
  <text class="t" x="24" y="22" fill="{p.gold}" font-size="10" letter-spacing="1.6">SHELL</text>
  <text class="t" x="24" y="40" fill="{p.dim}" font-size="10" letter-spacing="1.6">STDOUT</text>
  <g class="t">
    {chr(10).join("    " + l for l in lines).strip()}
  </g>
  <rect x="{W-46}" y="21" width="6" height="12" fill="{p.gold}">
    <animate attributeName="opacity" values="1;1;0.1;0.1" keyTimes="0;0.5;0.55;1" dur="1.6s" repeatCount="indefinite"/>
  </rect>
  <circle cx="{W-24}" cy="27" r="3" fill="{p.cyan}" filter="url(#{P}Glow)">
    <animate attributeName="opacity" values="0.95;0.3;0.95" dur="2.6s" repeatCount="indefinite"/>
  </circle>
{atmosphere(P, W, H, p, sweep_dur="7s")}
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="3" fill="none" stroke="{p.dim}" stroke-width="0.8" opacity="0.6"/>
</g>
</svg>
'''


# --------------------------------------------------------------------------- divider
def divider(p: Palette) -> str:
    W, H, P = 900, 22, "d"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="">
<defs>
  <linearGradient id="{P}Rail" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{p.cyan}" stop-opacity="0"/>
    <stop offset="16%" stop-color="{p.cyan}" stop-opacity="0.55"/>
    <stop offset="84%" stop-color="{p.cyan}" stop-opacity="0.55"/>
    <stop offset="100%" stop-color="{p.cyan}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="{P}Pulse" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{p.cyan}" stop-opacity="0"/>
    <stop offset="50%" stop-color="{p.pulse}" stop-opacity="1"/>
    <stop offset="100%" stop-color="{p.cyan}" stop-opacity="0"/>
  </linearGradient>
  <filter id="{P}Glow" x="-300%" y="-800%" width="700%" height="1700%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="1.6"/>
  </filter>
</defs>
  <line x1="0" y1="11" x2="{W}" y2="11" stroke="url(#{P}Rail)" stroke-width="{HAIR}"/>
  <line x1="150" y1="11" x2="410" y2="11" stroke="{p.dim}" stroke-width="4" stroke-dasharray="0.7 6" opacity="0.75"/>
  <line x1="490" y1="11" x2="750" y2="11" stroke="{p.dim}" stroke-width="4" stroke-dasharray="0.7 6" opacity="0.75"/>
  <path d="M432 11 L442 5 L458 5 L468 11 L458 17 L442 17 Z" fill="none" stroke="{p.gold}" stroke-width="{HAIR}"/>
  <circle cx="450" cy="11" r="1.6" fill="{p.cyan}" filter="url(#{P}Glow)">
    <animate attributeName="r" values="1.2;2.6;1.2" dur="2.8s" repeatCount="indefinite"/>
  </circle>
  <rect x="-130" y="10.3" width="130" height="1.4" fill="url(#{P}Pulse)" opacity="0.75">
    <animate attributeName="x" values="-130;{W}" dur="6s" repeatCount="indefinite"/>
  </rect>
</svg>
'''


# --------------------------------------------------------------------------- footer
def footer(t: Telemetry, p: Palette) -> str:
    """Hairline strip: the last 26 weeks as a sparkline plus account totals."""
    W, H, P = 900, 128, "f"
    weeks = (t.weeks or [0] * 26)[-26:]
    peak = max(weeks) or 1
    x0, x1, base, top = 66, 486, 78, 34
    step = (x1 - x0) / max(1, len(weeks) - 1)

    pts, bars = [], []
    for i, v in enumerate(weeks):
        x = x0 + i * step
        y = base - (base - top) * (v / peak) ** 0.75
        pts.append(f"{x:.1f},{y:.1f}")
        bars.append(f'<line x1="{x:.1f}" y1="{base}" x2="{x:.1f}" y2="{y:.1f}" '
                    f'stroke="{p.ramp[_level(v, peak)]}" stroke-width="1.6" opacity="0.75"/>')

    totals = _cells(p, 560, 292, 52, 74, [
        ("REPOS", f"{t.repos}"),
        ("STARS", f"{t.stars}"),
        ("FOLLOW", f"{t.followers}"),
    ], value_size=17)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="recent activity and account totals">
<defs>{defs(P, W, H, p)}</defs>
<g clip-path="url(#{P}Clip)">
  <rect width="{W}" height="{H}" fill="url(#{P}Deep)"/>

  <g class="t">
    <text x="{x0}" y="24" fill="{p.dim}" font-size="8.5" letter-spacing="2.4">LAST 26 WEEKS</text>
    <line x1="{x0}" y1="{base}" x2="{x1}" y2="{base}" stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.7"/>
    <g>{chr(10).join("      " + b for b in bars).strip()}</g>
    <polyline points="{' '.join(pts)}" fill="none" stroke="{p.cyan}" stroke-width="{LINE}" opacity="0.9"/>
    <line x1="{x0}" y1="{top-6}" x2="{x0}" y2="{base}" stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.5"/>
    <text x="{x0-6}" y="{top-1}" fill="{p.dim}" font-size="7" text-anchor="end">{peak}</text>
    <text x="{x0-6}" y="{base+3}" fill="{p.dim}" font-size="7" text-anchor="end">0</text>
    <line x1="524" y1="24" x2="524" y2="94" stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.55"/>
    {totals}
    <line x1="{x0}" y1="98" x2="{W-66}" y2="98" stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.45"/>
    <text x="{x0}" y="115" fill="{p.dim}" font-size="9" letter-spacing="1.7">{t.login}/{t.login} &#183; regenerated daily by github actions</text>
    <text x="{W-66}" y="115" fill="{p.dim}" font-size="9" letter-spacing="1.7" text-anchor="end">SYNC {t.synced}Z</text>
  </g>
{atmosphere(P, W, H, p, sweep_dur="8s")}
{frame(W, H, p, inset=10, arm=36)}
</g>
</svg>
'''
