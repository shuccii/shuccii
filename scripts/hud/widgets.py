"""The dashboard tiles.

Each tile owns a *different* kind of motion, so the board reads as several
instruments running at once rather than one effect repeated:

  topbar    horizontal ticker
  system    bars filling (stroke-dashoffset)
  radar     rotating sweep with a decaying trail
  globe     meridians drifting behind a clip (apparent rotation)
  pulse     a playhead scrubbing across real daily data
  languages donut segments drawing on, then a counter-rotating collar
  log       vertical scroll

All values come from Telemetry; nothing here invents a number.
"""
from __future__ import annotations

import math

from datetime import date

from .data import Telemetry
from .theme import (BAR, HAIR, LINE, PAD, Palette, atmosphere, chrome,
                    chrome_defs, defs)


def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def _clip(s: str, n: int) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


def _shell(prefix: str, w: int, h: int, p: Palette, title: str, right: str,
           body: str, label: str, sweep: str = "11s") -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{_esc(label)}">
<defs>{defs(prefix, w, h, p)}{chrome_defs(prefix, p)}
  <clipPath id="{prefix}Inner"><rect x="{PAD}" y="{PAD+BAR}" width="{w-2*PAD}" height="{h-2*PAD-BAR}"/></clipPath>
</defs>
{chrome(prefix, w, h, p, title, right)}
<g clip-path="url(#{prefix}Inner)">
{body}
  <rect x="{PAD}" y="{PAD+BAR}" width="{w-2*PAD}" height="{h-2*PAD-BAR}" fill="url(#{prefix}Scan)" opacity="0.3"/>
  <rect x="{PAD}" y="{PAD+BAR}" width="{w-2*PAD}" height="{h-2*PAD-BAR}" filter="url(#{prefix}Grain)" opacity="{p.grain_opacity*0.8:.2f}"/>
</g>
</svg>
'''


# ---------------------------------------------------------------- topbar
def topbar(t: Telemetry, p: Palette) -> str:
    """Motion: a ticker sliding right to left."""
    W, H, P = 900, 44, "tb"
    items = [f"REPO {t.login}/{t.login}", f"BRANCH {t.branch}", f"HEAD {t.sha}",
             f"CONTRIB {t.contributions}", f"COMMITS {t.commits}",
             f"PEAK {t.peak_week}/WK", f"LANG {t.top_language.upper()}",
             f"SYNC {t.synced}Z"]
    strip = "   •   ".join(items) + "   •   "
    run = _esc(strip * 2)
    width = len(strip) * 6.98

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="status bar">
<defs>{defs(P, W, H, p)}{chrome_defs(P, p)}
  <clipPath id="{P}Tick"><rect x="246" y="8" width="{W-356}" height="{H-16}"/></clipPath>
  <linearGradient id="{P}Fade" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{p.bg_mid}"/><stop offset="6%" stop-color="{p.bg_mid}" stop-opacity="0"/>
    <stop offset="94%" stop-color="{p.bg_mid}" stop-opacity="0"/><stop offset="100%" stop-color="{p.bg_mid}"/>
  </linearGradient>
</defs>
  <g filter="url(#{P}Drop)">
    <rect x="{PAD}" y="{PAD}" width="{W-2*PAD}" height="{H-2*PAD}" rx="4" fill="url(#{P}Body)"/>
  </g>
  <rect x="{PAD+6}" y="{PAD+0.5}" width="{W-2*PAD-12}" height="0.9" fill="url(#{P}Lip)"/>
  <rect x="{PAD+0.4}" y="{PAD+0.4}" width="{W-2*PAD-0.8}" height="{H-2*PAD-0.8}" rx="4" fill="none"
        stroke="{p.dim}" stroke-width="0.7" opacity="0.65"/>
  <g class="t">
    <text x="22" y="25.6" fill="{p.ink}" font-size="9.5" letter-spacing="4.6">S / T A N I</text>
    <circle cx="176" cy="22" r="2.8" fill="{p.cyan}" filter="url(#{P}Glow)">
      <animate attributeName="opacity" values="1;0.25;1" dur="2.6s" repeatCount="indefinite"/>
    </circle>
    <text x="185" y="24.6" fill="{p.cyan}" font-size="7.2" letter-spacing="2.4">{'LIVE' if t.live else 'CACHED'}</text>
    <line x1="234" y1="12" x2="234" y2="32" stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.6"/>
    <g clip-path="url(#{P}Tick)">
      <text y="24.6" fill="{p.dim}" font-size="6.8" letter-spacing="2.4" xml:space="preserve">
        <animate attributeName="x" values="246;{246-width:.0f}" dur="42s" repeatCount="indefinite"/>
        {run}
      </text>
    </g>
    <rect x="246" y="8" width="{W-356}" height="{H-16}" fill="url(#{P}Fade)"/>
    <line x1="{W-104}" y1="12" x2="{W-104}" y2="32" stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.6"/>
    <text x="{W-24}" y="25" fill="{p.pale}" font-size="8.1" letter-spacing="1.8" text-anchor="end">{t.since} &#8594; NOW</text>
  </g>
</svg>
'''


# ---------------------------------------------------------------- index
def system(t: Telemetry, p: Palette) -> str:
    """Motion: recency bars filling, staggered."""
    W, H, P = 292, 196, "sy"
    rows = t.repos_detail[:6]
    y0, gap = PAD + BAR + 17, 20.5
    bar_x, bar_w = PAD + 12, W - 2 * PAD - 24

    newest = max((r["pushed"] for r in rows), default="")
    oldest = min((r["pushed"] for r in rows), default="")

    def recency(d: str) -> float:
        # newest repo fills the bar, oldest keeps a visible stub
        if not d or newest == oldest:
            return 1.0
        span = (date.fromisoformat(newest) - date.fromisoformat(oldest)).days or 1
        age = (date.fromisoformat(newest) - date.fromisoformat(d)).days
        return max(0.12, 1 - age / span)

    clips, body = [], []
    for i, r in enumerate(rows):
        y = y0 + i * gap
        fill = bar_w * recency(r["pushed"])
        clips.append(f'<clipPath id="{P}Bar{i}"><rect x="{bar_x}" y="{y}" width="{max(fill, 3):.1f}" height="3" rx="1.5"/></clipPath>')
        body.append(f'''
    <text x="{bar_x}" y="{y-4}" fill="{p.pale}" font-size="6.8" letter-spacing="0.6">{_esc(_clip(r["name"], 22))}</text>
    <text x="{bar_x+bar_w}" y="{y-4}" fill="{p.dim}" font-size="6.1" text-anchor="end">{r["pushed"][5:]}</text>
    <rect x="{bar_x}" y="{y}" width="{bar_w}" height="3" rx="1.5" fill="{p.faint}" opacity="0.75"/>
    <rect x="{bar_x}" y="{y}" width="{max(fill, 3):.1f}" height="3" rx="1.5" fill="{p.cyan}" opacity="0.85"/>
    <rect x="{bar_x}" y="{y}" width="{max(fill, 3):.1f}" height="0.9" rx="0.5" fill="#ffffff" opacity="0.22"/>
    <g clip-path="url(#{P}Bar{i})">
      <rect y="{y}" width="26" height="3" rx="1.5" fill="{p.pulse}" opacity="0.5">
        <animate attributeName="x" values="{bar_x-26};{bar_x+max(fill, 3):.1f}" dur="2.6s"
                 begin="{i*0.42:.2f}s" repeatCount="indefinite"/>
      </rect>
    </g>''')

    return _shell(P, W, H, p, "REPOSITORY INDEX", f"{t.repos} PUBLIC", f'''
  <defs>{"".join(clips)}</defs>
  <g class="t">{"".join(body)}
    <text x="{bar_x}" y="{H-PAD-10}" fill="{p.dim}" font-size="5.8" letter-spacing="1.6">BAR LENGTH = RECENCY OF LAST PUSH</text>
  </g>''', "repositories by last push")


# ---------------------------------------------------------------- rhythm
DAYS = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
DAYS_SHORT = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
              "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def radar(t: Telemetry, p: Palette) -> str:
    """Motion: a sweep arm rotating, lighting each weekday sector as it passes."""
    W, H, P = 292, 196, "rd"
    cx, cy = W / 2, PAD + BAR + (H - PAD * 2 - BAR) / 2 + 4
    R = 58
    counts = t.weekday or [0] * 7
    peak = max(counts) or 1
    step = 360 / 7

    rings = "".join(
        f'<circle cx="{cx}" cy="{cy}" r="{R*f:.1f}" fill="none" stroke="{p.dim}" '
        f'stroke-width="{HAIR}" opacity="{0.7 if i % 2 else 0.4}"/>'
        for i, f in enumerate((0.34, 0.56, 0.78, 1.0)))

    wedges, labels = [], []
    for i, v in enumerate(counts):
        a0 = i * step - 90 - step / 2 + 1.2
        a1 = a0 + step - 2.4
        rr = R * (0.16 + 0.84 * (v / peak))
        x0, y0 = cx + rr*math.cos(math.radians(a0)), cy + rr*math.sin(math.radians(a0))
        x1, y1 = cx + rr*math.cos(math.radians(a1)), cy + rr*math.sin(math.radians(a1))
        wedges.append(
            f'<path d="M{cx} {cy} L{x0:.1f} {y0:.1f} A{rr:.1f} {rr:.1f} 0 0 1 {x1:.1f} {y1:.1f} Z" '
            f'fill="{p.cyan}" opacity="{0.14 + 0.4*(v/peak):.2f}" stroke="{p.cyan}" '
            f'stroke-width="{HAIR}"/>')
        am = math.radians(i * step - 90)
        lx, ly = cx + (R + 13)*math.cos(am), cy + (R + 13)*math.sin(am)
        big = v == peak
        labels.append(
            f'<text x="{lx:.1f}" y="{ly+2.2:.1f}" fill="{p.gold if big else p.dim}" font-size="5.8" '
            f'letter-spacing="1" text-anchor="middle">{DAYS[i]}</text>'
            f'<text x="{lx:.1f}" y="{ly+9.6:.1f}" fill="{p.pale if big else p.dim}" font-size="5.9" '
            f'text-anchor="middle">{v}</text>')

    return _shell(P, W, H, p, "WEEKLY RHYTHM", f"PEAK {DAYS[counts.index(peak)]}", f'''
  <defs>
    <radialGradient id="{P}Wedge" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{p.cyan}" stop-opacity="{0.34 if p.key=='dark' else 0.24}"/>
      <stop offset="100%" stop-color="{p.cyan}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <g class="t">
    {rings}
    {"".join(wedges)}
    <g>
      <animateTransform attributeName="transform" type="rotate" from="-90 {cx} {cy}" to="270 {cx} {cy}" dur="7s" repeatCount="indefinite"/>
      <path d="M{cx} {cy} L{cx+R} {cy} A{R} {R} 0 0 0 {cx + R*math.cos(math.radians(-46)):.1f} {cy + R*math.sin(math.radians(-46)):.1f} Z" fill="url(#{P}Wedge)"/>
      <line x1="{cx}" y1="{cy}" x2="{cx+R}" y2="{cy}" stroke="{p.cyan}" stroke-width="{LINE}" filter="url(#{P}Glow)"/>
    </g>
    {"".join(labels)}
    <circle cx="{cx}" cy="{cy}" r="1.8" fill="{p.gold}"/>
  </g>''', "contributions by weekday")


# ---------------------------------------------------------------- globe
def globe(t: Telemetry, p: Palette) -> str:
    """Motion: meridians drifting behind a circular clip — apparent rotation."""
    W, H, P = 292, 196, "gl"
    cx, cy = W / 2, PAD + BAR + (H - PAD * 2 - BAR) / 2 + 2
    R = 58

    lats = "".join(
        f'<ellipse cx="{cx}" cy="{cy + R*math.sin(math.radians(a)):.1f}" '
        f'rx="{R*math.cos(math.radians(a)):.1f}" ry="{R*math.cos(math.radians(a))*0.17:.1f}" '
        f'fill="none" stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.55"/>'
        for a in (-60, -35, -12, 12, 35, 60))
    # meridians are ellipses whose rx cycles, which is what a rotating sphere does
    meridians = "".join(f'''
      <ellipse cx="{cx}" cy="{cy}" ry="{R}" fill="none" stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.7">
        <animate attributeName="rx" values="{R};0;{R}" dur="16s" begin="{-i*16/6:.2f}s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0.16;0.75;0.16" dur="16s" begin="{-i*16/6:.2f}s" repeatCount="indefinite"/>
      </ellipse>''' for i in range(6))

    return _shell(P, W, H, p, "UPLINK", "GRAPHQL/V4", f'''
  <defs>
    <radialGradient id="{P}Limb" cx="38%" cy="32%" r="72%">
      <stop offset="0%" stop-color="{p.cyan}" stop-opacity="{0.2 if p.key=='dark' else 0.14}"/>
      <stop offset="70%" stop-color="{p.cyan}" stop-opacity="0.04"/>
      <stop offset="100%" stop-color="{p.cyan}" stop-opacity="{0.34 if p.key=='dark' else 0.18}"/>
    </radialGradient>
  </defs>
  <g class="t">
    <circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#{P}Limb)"/>
    <circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{p.cyan}" stroke-width="{LINE}" opacity="0.8"/>
    {lats}{meridians}
    <circle cx="{cx}" cy="{cy}" r="{R+9}" fill="none" stroke="{p.dim}" stroke-width="{HAIR}"
            stroke-dasharray="1 6" opacity="0.8">
      <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="-360 {cx} {cy}" dur="34s" repeatCount="indefinite"/>
    </circle>
    <g>
      <circle cx="{cx}" cy="{cy-R-9}" r="2" fill="{p.gold}" filter="url(#{P}Glow)"/>
      <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="11s" repeatCount="indefinite"/>
    </g>
    <text x="{PAD+11}" y="{PAD+BAR+14}" fill="{p.dim}" font-size="5.8" letter-spacing="1.6">ENDPOINT</text>
    <text x="{PAD+11}" y="{PAD+BAR+24}" fill="{p.pale}" font-size="6.8">api.github.com</text>
    <text x="{W-PAD-12}" y="{H-PAD-22}" fill="{p.dim}" font-size="6.5" letter-spacing="1.6" text-anchor="end">SYNC</text>
    <text x="{W-PAD-12}" y="{H-PAD-11}" fill="{p.pale}" font-size="7.2" text-anchor="end">{t.synced[-5:]}Z</text>
  </g>''', "telemetry uplink")


# ---------------------------------------------------------------- pulse
def pulse(t: Telemetry, p: Palette) -> str:
    """Motion: a playhead scrubbing left to right across real daily data."""
    W, H, P = 444, 176, "pu"
    days = (t.days or [0] * 120)[-120:]
    peak = max(days) or 1
    x0, x1 = PAD + 16, W - PAD - 16
    base, top = H - PAD - 26, PAD + BAR + 16
    step = (x1 - x0) / max(1, len(days) - 1)

    bars = "".join(
        f'<line x1="{x0+i*step:.1f}" y1="{base}" x2="{x0+i*step:.1f}" '
        f'y2="{base - (base-top)*(math.log1p(v)/math.log1p(peak)):.1f}" '
        f'stroke="{p.ramp[min(4, 1+int(v/peak*3.99)) if v else 0]}" stroke-width="2.2" '
        f'stroke-linecap="round" opacity="{0.55 if not v else 0.95}"/>'
        for i, v in enumerate(days))

    grid = "".join(
        f'<line x1="{x0}" y1="{base-(base-top)*f:.1f}" x2="{x1}" y2="{base-(base-top)*f:.1f}" '
        f'stroke="{p.dim}" stroke-width="{HAIR}" stroke-dasharray="1 5" opacity="0.4"/>'
        for f in (0.33, 0.66, 1.0))

    return _shell(P, W, H, p, "DAILY PULSE", f"{len(days)} DAYS", f'''
  <g class="t">
    {grid}
    <line x1="{x0}" y1="{base}" x2="{x1}" y2="{base}" stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.8"/>
    {bars}
    <text x="{x0-4}" y="{top+3}" fill="{p.dim}" font-size="6.3" text-anchor="end">{peak}</text>
    <text x="{x0-4}" y="{base+3}" fill="{p.dim}" font-size="6.3" text-anchor="end">0</text>
    <g>
      <animateTransform attributeName="transform" type="translate"
                        values="0 0;{x1-x0:.0f} 0;0 0" dur="18s"
                        calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1" keyTimes="0;0.5;1"
                        repeatCount="indefinite"/>
      <line x1="{x0}" y1="{top-8}" x2="{x0}" y2="{base+5}" stroke="{p.gold}" stroke-width="{LINE}" opacity="0.9"/>
      <path d="M{x0-3.5} {top-8} L{x0+3.5} {top-8} L{x0} {top-3} Z" fill="{p.gold}"/>
    </g>
    <text x="{x1}" y="{H-PAD-10}" fill="{p.dim}" font-size="6.5" letter-spacing="1.6" text-anchor="end">CONTRIBUTIONS PER DAY</text>
    <text x="{x0}" y="{H-PAD-10}" fill="{p.dim}" font-size="6.5" letter-spacing="1.6">TOTAL {t.contributions}</text>
  </g>''', "daily contribution pulse")


# ---------------------------------------------------------------- log
def log(t: Telemetry, p: Palette) -> str:
    """Motion: the list scrolling upward, newest at the top."""
    W, H, P = 900, 186, "lg"
    rows = t.commits_log or [("--:--", "—", "awaiting telemetry")]
    lh = 17
    span = len(rows) * lh

    def line(i, row, offset):
        clock, repo, msg = row
        y = PAD + BAR + 16 + i * lh + offset
        return (f'<text x="{PAD+16}" y="{y}" fill="{p.dim}" font-size="8.1">{clock}</text>'
                f'<text x="{PAD+62}" y="{y}" fill="{p.gold}" font-size="8.1">{_esc(_clip(repo, 22))}</text>'
                f'<text x="{PAD+230}" y="{y}" fill="{p.pale}" font-size="8.1">{_esc(_clip(msg, 88))}</text>'
                f'<rect x="{PAD+10}" y="{y-8}" width="2" height="10" fill="{p.cyan}" opacity="{0.9 if i == 0 else 0.25}"/>')

    stack = "".join(line(i, r, 0) for i, r in enumerate(rows)) + \
            "".join(line(i, r, span) for i, r in enumerate(rows))

    return _shell(P, W, H, p, "COMMIT STREAM", f"{len(rows)} RECENT", f'''
  <g class="t">
    <g>
      <animateTransform attributeName="transform" type="translate" values="0 0;0 {-span}"
                        dur="{len(rows)*2.6:.0f}s" calcMode="linear" repeatCount="indefinite"/>
      {stack}
    </g>
  </g>''', "recent commits")


# ---------------------------------------------------------------- languages
def languages(t: Telemetry, p: Palette) -> str:
    """Motion: donut segments drawing on, then a counter-rotating collar."""
    W, H, P = 444, 176, "ln"
    cx = PAD + 92
    cy = PAD + BAR + (H - PAD * 2 - BAR) / 2
    R, sw = 46, 13
    total = sum(b for _, b, _ in t.lang_bytes) or 1
    circ = 2 * math.pi * R

    segs, legend, off = [], [], 0.0
    for i, (name, size, colour) in enumerate(t.lang_bytes[:6]):
        frac = size / total
        arc = circ * frac
        segs.append(f'''
    <circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{colour}" stroke-width="{sw}"
            stroke-dasharray="{arc:.2f} {circ-arc:.2f}" stroke-dashoffset="{-off:.2f}"
            transform="rotate(-90 {cx} {cy})" opacity="0.92"/>''')
        ly = PAD + BAR + 22 + i * 18
        legend.append(
            f'<rect x="{PAD+206}" y="{ly-7}" width="7" height="7" rx="1.5" fill="{colour}"/>'
            f'<text x="{PAD+220}" y="{ly}" fill="{p.pale}" font-size="7.7">{_esc(_clip(name, 20))}</text>'
            f'<text x="{W-PAD-14}" y="{ly}" fill="{p.dim}" font-size="7.7" text-anchor="end">{frac*100:.1f}%</text>')
        off += arc

    ticks = "".join(
        f'<line x1="{cx + (R+11)*math.cos(math.radians(a)):.1f}" y1="{cy + (R+11)*math.sin(math.radians(a)):.1f}" '
        f'x2="{cx + (R+15)*math.cos(math.radians(a)):.1f}" y2="{cy + (R+15)*math.sin(math.radians(a)):.1f}" '
        f'stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.7"/>' for a in range(0, 360, 15))

    return _shell(P, W, H, p, "LANGUAGE MIX", f"{total/1048576:.1f} MB", f'''
  <defs>
    <clipPath id="{P}Ring"><circle cx="{cx}" cy="{cy}" r="{R+sw/2:.1f}"/></clipPath>
  </defs>
  <g class="t">
    <circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{p.faint}" stroke-width="{sw}" opacity="0.8"/>
    {''.join(segs)}
    <circle cx="{cx}" cy="{cy}" r="{R-sw/2-1.5:.1f}" fill="none" stroke="{p.bg_outer}" stroke-width="1.4" opacity="0.7"/>
    <g>
      <animateTransform attributeName="transform" type="rotate" from="360 {cx} {cy}" to="0 {cx} {cy}" dur="40s" repeatCount="indefinite"/>
      {ticks}
    </g>
    <g clip-path="url(#{P}Ring)">
      <g>
        <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="6.5s" repeatCount="indefinite"/>
        <rect x="{cx}" y="{cy-1.6}" width="{R+sw}" height="3.2" fill="#ffffff" opacity="0.3"/>
      </g>
    </g>
    <text x="{cx}" y="{cy+1}" fill="{p.ink}" font-size="13.5" text-anchor="middle">{len(t.lang_bytes)}</text>
    <text x="{cx}" y="{cy+13}" fill="{p.dim}" font-size="5.8" letter-spacing="1.8" text-anchor="middle">LANGUAGES</text>
    {''.join(legend)}
  </g>''', "language mix by bytes")


# ---------------------------------------------------------------- summary
def summary(t: Telemetry, p: Palette) -> str:
    """Motion: a tracer running along the year curve (animateMotion)."""
    W, H, P = 900, 178, "sm"
    weeks = t.weeks or [0] * 53
    peak = max(weeks) or 1
    x0, x1 = 372, W - PAD - 34
    base, top = H - PAD - 34, PAD + BAR + 22
    step = (x1 - x0) / max(1, len(weeks) - 1)

    pts = [(x0 + i * step, base - (base - top) * (v / peak)) for i, v in enumerate(weeks)]
    line = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    area = line + f" L{pts[-1][0]:.1f} {base} L{pts[0][0]:.1f} {base} Z"

    months, seen = [], set()
    for i, d in enumerate(t.day_dates[::7][:len(weeks)] or []):
        m = int(d[5:7])
        if m not in seen:
            seen.add(m)
            if len(seen) % 2 == 0:      # label every other month
                continue
            mx = x0 + i * step
            months.append(f'<line x1="{mx:.1f}" y1="{base}" x2="{mx:.1f}" y2="{base+4}" '
                          f'stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.7"/>'
                          f'<text x="{mx:.1f}" y="{base+13}" fill="{p.dim}" font-size="5.8" '
                          f'letter-spacing="0.8" text-anchor="middle">{d[:7].replace("-", "/")[2:]}</text>')

    facts = [("CONTRIBUTIONS", f"{t.contributions}"), ("PUBLIC REPOS", f"{t.repos}"),
             ("ON GITHUB", f"{t.years_on_github} YR"), ("FOLLOWERS", f"{t.followers}")]
    rows = "".join(
        f'<text x="{PAD+22}" y="{PAD+BAR+26+i*26}" fill="{p.dim}" font-size="6.4" letter-spacing="2">{lbl}</text>'
        f'<text x="{PAD+22}" y="{PAD+BAR+40+i*26}" fill="{p.pale}" font-size="14">{val}</text>'
        f'<line x1="{PAD+16}" y1="{PAD+BAR+18+i*26}" x2="{PAD+16}" y2="{PAD+BAR+42+i*26}" '
        f'stroke="{p.cyan if i == 0 else p.dim}" stroke-width="{LINE}" opacity="{0.9 if i == 0 else 0.4}"/>'
        for i, (lbl, val) in enumerate(facts))

    return _shell(P, W, H, p, "ACCOUNT SUMMARY", f"{t.login.upper()} &#183; SINCE {t.since}", f'''
  <defs>
    <linearGradient id="{P}Fill" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{p.cyan}" stop-opacity="{0.3 if p.key=='dark' else 0.22}"/>
      <stop offset="100%" stop-color="{p.cyan}" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <g class="t">
    {rows}
    <line x1="{PAD+180}" y1="{PAD+BAR+12}" x2="{PAD+180}" y2="{H-PAD-14}" stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.45"/>
    <text x="{PAD+200}" y="{PAD+BAR+26}" fill="{p.dim}" font-size="6.4" letter-spacing="2">IDENTITY</text>
    <text x="{PAD+200}" y="{PAD+BAR+44}" fill="{p.ink}" font-size="15" letter-spacing="1.4">{_esc(t.name)}</text>
    <text x="{PAD+200}" y="{PAD+BAR+60}" fill="{p.dim}" font-size="7.4" letter-spacing="1.4">github.com/{t.login}</text>
    <text x="{PAD+200}" y="{PAD+BAR+84}" fill="{p.dim}" font-size="6.4" letter-spacing="2">PRIMARY LANGUAGE</text>
    <text x="{PAD+200}" y="{PAD+BAR+100}" fill="{p.pale}" font-size="10">{_esc(t.top_language)}</text>

    <line x1="{PAD+352}" y1="{PAD+BAR+12}" x2="{PAD+352}" y2="{H-PAD-14}" stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.45"/>
    <text x="{x1}" y="{top-8}" fill="{p.dim}" font-size="6.4" letter-spacing="2" text-anchor="end">CONTRIBUTIONS PER WEEK</text>
    <path d="{area}" fill="url(#{P}Fill)"/>
    <path id="{P}Curve" d="{line}" fill="none" stroke="{p.cyan}" stroke-width="{LINE}" opacity="0.95"/>
    <line x1="{x0}" y1="{base}" x2="{x1}" y2="{base}" stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.7"/>
    <text x="{x0-6}" y="{top+3}" fill="{p.dim}" font-size="5.8" text-anchor="end">{peak}</text>
    <text x="{x0-6}" y="{base+2}" fill="{p.dim}" font-size="5.8" text-anchor="end">0</text>
    {"".join(months)}
    <circle r="2.6" fill="{p.gold}" filter="url(#{P}Glow)">
      <animateMotion dur="13s" repeatCount="indefinite" rotate="auto" keyPoints="0;1" keyTimes="0;1" calcMode="linear">
        <mpath href="#{P}Curve"/>
      </animateMotion>
    </circle>
  </g>''', "account summary")


# ---------------------------------------------------------------- ledger
def ledger(t: Telemetry, p: Palette) -> str:
    """Motion: a caliper stepping down the rows, one at a time."""
    W, H, P = 444, 178, "ld"
    rows = [("TOTAL COMMITS", t.commits), ("PULL REQUESTS", t.prs), ("ISSUES", t.issues),
            ("STARS EARNED", t.stars), ("REPOS TOUCHED", t.repos)]
    top = PAD + BAR + 22
    gap = 24
    peak = max((v for _, v in rows), default=1) or 1
    gx, gw = PAD + 190, W - PAD - 200 - 46

    body = []
    for i, (label, value) in enumerate(rows):
        y = top + i * gap
        w = gw * (value / peak)
        body.append(
            f'<text x="{PAD+18}" y="{y}" fill="{p.dim}" font-size="7.4" letter-spacing="1.6">{label}</text>'
            f'<line x1="{gx}" y1="{y-3}" x2="{gx+gw}" y2="{y-3}" stroke="{p.faint}" stroke-width="2" opacity="0.7"/>'
            f'<line x1="{gx}" y1="{y-3}" x2="{gx+max(w, 1.5):.1f}" y2="{y-3}" stroke="{p.cyan}" stroke-width="2" opacity="0.9"/>'
            f'<text x="{W-PAD-18}" y="{y}" fill="{p.pale}" font-size="10.5" text-anchor="end">{value}</text>')

    stops = ";".join(f"0 {i*gap}" for i in range(len(rows)))
    keytimes = ";".join(f"{i/len(rows):.4f}" for i in range(len(rows)))

    return _shell(P, W, H, p, "LEDGER", "LAST 12 MONTHS", f'''
  <g class="t">
    {"".join(body)}
    <g>
      <animateTransform attributeName="transform" type="translate" values="{stops}"
                        keyTimes="{keytimes}" dur="{len(rows)*1.6:.1f}s" calcMode="discrete" repeatCount="indefinite"/>
      <path d="M{PAD+11} {top-9} L{PAD+15} {top-6} L{PAD+11} {top-3} Z" fill="{p.gold}"/>
      <line x1="{PAD+11}" y1="{top-12}" x2="{PAD+11}" y2="{top}" stroke="{p.gold}" stroke-width="{HAIR}" opacity="0.8"/>
      <line x1="{W-PAD-10}" y1="{top-12}" x2="{W-PAD-10}" y2="{top}" stroke="{p.gold}" stroke-width="{HAIR}" opacity="0.8"/>
    </g>
    <text x="{PAD+18}" y="{H-PAD-9}" fill="{p.dim}" font-size="5.8" letter-spacing="1.6">BARS SCALED TO THE LARGEST FIGURE</text>
  </g>''', "activity ledger")


# ---------------------------------------------------------------- hours
def hours(t: Telemetry, p: Palette) -> str:
    """Motion: a shimmer travelling through the fill — the gradient moves, not the shape."""
    W, H, P = 444, 178, "hr"
    counts = t.hours or [0] * 24
    peak = max(counts) or 1
    x0, x1 = PAD + 26, W - PAD - 18
    mid = PAD + BAR + (H - PAD * 2 - BAR) / 2 - 6
    amp = 40
    step = (x1 - x0) / 24

    top_pts, bot_pts = [], []
    for i, v in enumerate(counts):
        x = x0 + (i + 0.5) * step
        a = amp * (v / peak)
        top_pts.append(f"{x:.1f} {mid-a:.1f}")
        bot_pts.append(f"{x:.1f} {mid+a:.1f}")
    silhouette = (f"M{x0} {mid} L" + " L".join(top_pts) + f" L{x1} {mid} L" +
                  " L".join(reversed(bot_pts)) + " Z")

    bars = "".join(
        f'<rect x="{x0+i*step+step*0.24:.1f}" y="{mid-amp*(v/peak):.1f}" '
        f'width="{step*0.52:.1f}" height="{2*amp*(v/peak):.1f}" rx="1" '
        f'fill="{p.cyan}" opacity="{0.12 if v else 0.05}"/>' for i, v in enumerate(counts))

    ticks = "".join(
        f'<line x1="{x0+(h+0.5)*step:.1f}" y1="{mid+amp+6}" x2="{x0+(h+0.5)*step:.1f}" y2="{mid+amp+10}" '
        f'stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.7"/>'
        f'<text x="{x0+(h+0.5)*step:.1f}" y="{mid+amp+19}" fill="{p.dim}" font-size="5.8" '
        f'text-anchor="middle">{h:02d}</text>' for h in (0, 6, 12, 18, 23))

    ph = t.peak_hour
    return _shell(P, W, H, p, "COMMIT HOURS", f"JST &#183; PEAK {ph:02d}:00", f'''
  <defs>
    <linearGradient id="{P}Shimmer" gradientUnits="userSpaceOnUse"
                    x1="{x0}" y1="0" x2="{x0+130}" y2="0">
      <stop offset="0%" stop-color="{p.cyan}" stop-opacity="0.35"/>
      <stop offset="42%" stop-color="{p.pulse}" stop-opacity="0.95"/>
      <stop offset="58%" stop-color="{p.pulse}" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="{p.cyan}" stop-opacity="0.35"/>
      <animateTransform attributeName="gradientTransform" type="translate"
                        values="{-120};{W}" dur="6.5s" repeatCount="indefinite"/>
    </linearGradient>
  </defs>
  <g class="t">
    {bars}
    <line x1="{x0}" y1="{mid}" x2="{x1}" y2="{mid}" stroke="{p.dim}" stroke-width="{HAIR}" opacity="0.6"/>
    <path d="{silhouette}" fill="url(#{P}Shimmer)" stroke="{p.cyan}" stroke-width="{HAIR}" opacity="0.95"/>
    <line x1="{x0+(ph+0.5)*step:.1f}" y1="{mid-amp-8}" x2="{x0+(ph+0.5)*step:.1f}" y2="{mid+amp+4}"
          stroke="{p.gold}" stroke-width="{HAIR}" opacity="0.85"/>
    <text x="{x0+(ph+0.5)*step:.1f}" y="{mid-amp-11}" fill="{p.gold}" font-size="5.8"
          text-anchor="middle" letter-spacing="0.8">PEAK</text>
    {ticks}
    <text x="{PAD+18}" y="{H-PAD-9}" fill="{p.dim}" font-size="5.8" letter-spacing="1.6">{sum(counts)} COMMITS BY HOUR OF DAY</text>
  </g>''', "commits by hour")


# ---------------------------------------------------------------- grid
def grid(t: Telemetry, p: Palette) -> str:
    """Motion: a diagonal wave of brightness propagating across the calendar."""
    W, H, P = 900, 190, "gr"
    days = t.days or [0] * 371
    dates = t.day_dates or [""] * len(days)
    peak = max(days) or 1
    cols = math.ceil(len(days) / 7)
    gx, right = PAD + 26, PAD + 16
    pitch = (W - gx - right) / cols
    gapc = 2.6
    cell = pitch - gapc
    gy = PAD + BAR + 24

    cells, months, seen = [], [], set()
    for i, v in enumerate(days):
        c, r = divmod(i, 7)
        x = gx + c * pitch
        y = gy + r * pitch
        lvl = 0 if not v else min(4, 1 + int(v / peak * 3.999))
        phase = (c * 0.055 + r * 0.09) % 3.2
        cells.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="2.4" '
            f'fill="{p.ramp[lvl]}" opacity="{0.55 if not lvl else 0.95}">'
            f'<animate attributeName="opacity" '
            f'values="{0.55 if not lvl else 0.95};{0.8 if not lvl else 1};{0.55 if not lvl else 0.95}" '
            f'dur="3.2s" begin="-{phase:.2f}s" repeatCount="indefinite"/></rect>')
        if r == 0 and dates[i]:
            m = int(dates[i][5:7])
            if m not in seen:
                seen.add(m)
                months.append(f'<text x="{x:.1f}" y="{gy-6}" fill="{p.dim}" font-size="5.8" '
                              f'letter-spacing="0.8">{DAYS_SHORT[m-1]}</text>')

    wd = "".join(f'<text x="{gx-6}" y="{gy+r*pitch+cell*0.78:.1f}" fill="{p.dim}" '
                 f'font-size="5.4" text-anchor="end">{d}</text>'
                 for r, d in ((1, "M"), (3, "W"), (5, "F")))

    legend = "".join(
        f'<rect x="{W-PAD-118+i*14:.1f}" y="{H-PAD-20}" width="9" height="9" rx="1.8" fill="{c}" opacity="0.95"/>'
        for i, c in enumerate(p.ramp))

    return _shell(P, W, H, p, "CONTRIBUTION CALENDAR",
                  f"{t.contributions} IN {len(days)} DAYS", f'''
  <g class="t">
    {"".join(months)}{wd}
    {"".join(cells)}
    <text x="{W-PAD-132}" y="{H-PAD-12}" fill="{p.dim}" font-size="5.8" letter-spacing="1.4" text-anchor="end">LESS</text>
    {legend}
    <text x="{W-PAD-14}" y="{H-PAD-12}" fill="{p.dim}" font-size="5.8" letter-spacing="1.4" text-anchor="end">MORE</text>
  </g>''', "contribution calendar")
