"""Two palettes, one geometry.

The dark panel is a lit instrument; the light panel is the same instrument
drawn as a blueprint on paper. Line weights, positions and data are identical —
only colour, glow and film grain change, so both variants stay in register.

Hairline is the rule: nothing structural is heavier than 1.2.
"""
from __future__ import annotations

from dataclasses import dataclass, field

HAIR = 0.45
LINE = 0.7
ACCENT = 1.0

MONO = '"SFMono-Regular","SF Mono",Menlo,Consolas,"DejaVu Sans Mono",monospace'


@dataclass(frozen=True)
class Palette:
    key: str
    bg_inner: str
    bg_mid: str
    bg_outer: str
    cyan: str
    cyan_deep: str
    gold: str
    dim: str
    faint: str
    pale: str
    ink: str            # strongest text
    metal: str
    core_stops: tuple[tuple[str, str, str], ...]
    ramp: list[str]
    scan_colour: str
    scan_opacity: float
    grain_alpha: float
    grain_opacity: float
    vignette: str
    vignette_opacity: float
    glow_scale: float          # 0 disables the bloom entirely
    aberration: float          # 0 disables the RGB fringe
    sweep_opacity: float
    pulse: str            # travelling highlight on the divider rail
    glass_top: float      # panel fill alpha at the lit edge
    glass_bottom: float   # ...and where it falls away
    edge: str             # border of a glass panel


DARK = Palette(
    key="dark",
    bg_inner="#123a4e", bg_mid="#0b2534", bg_outer="#05141e",
    cyan="#6fe0f7", cyan_deep="#2fb0d2", gold="#f0c069",
    dim="#63a8c0", faint="#1e5169", pale="#dcf3fd", ink="#f7feff",
    metal="#17536b",
    core_stops=(("0%", "#ffffff", "1"), ("26%", "#dff8ff", "1"),
                ("60%", "#54c8e8", "0.62"), ("100%", "#0a4b61", "0")),
    ramp=["#25596f", "#1a7592", "#28abcc", "#5fd8f2", "#b4f3ff"],
    scan_colour="#0a3242", scan_opacity=0.28,
    grain_alpha=0.18, grain_opacity=0.32,
    vignette="#000000", vignette_opacity=0.6,
    glow_scale=1.0, aberration=0.26, sweep_opacity=0.09,
    pulse="#eafcff",
    glass_top=0.66, glass_bottom=0.4, edge="#7fe4fa",
)

LIGHT = Palette(
    key="light",
    bg_inner="#ffffff", bg_mid="#eef4f8", bg_outer="#dde8ef",
    cyan="#0e7490", cyan_deep="#0b5570", gold="#9a6a10",
    dim="#5d8ba0", faint="#c2d6e0", pale="#1d4d61", ink="#062430",
    metal="#8fb3c4",
    core_stops=(("0%", "#ffffff", "1"), ("26%", "#dff2fa", "1"),
                ("60%", "#7cc6dd", "0.5"), ("100%", "#bcd9e5", "0")),
    ramp=["#d3e3ea", "#a3cddd", "#5aa8c5", "#26809f", "#0b5570"],
    scan_colour="#9dbccb", scan_opacity=0.16,
    grain_alpha=0.06, grain_opacity=0.18,
    vignette="#3d6b80", vignette_opacity=0.16,
    glow_scale=0.45, aberration=0.0, sweep_opacity=0.07,
    pulse="#0b5570",
    glass_top=0.58, glass_bottom=0.26, edge="#0e7490",
)

PALETTES = (DARK, LIGHT)


def defs(prefix: str, w: int, h: int, p: Palette, *, light=(-70, -70, 60)) -> str:
    lx, ly, lz = light
    core = "".join(
        f'<stop offset="{off}" stop-color="{col}" stop-opacity="{op}"/>'
        for off, col, op in p.core_stops)
    # the bloom is what makes the dark panel glow; on paper it would only smear,
    # so the light palette scales it down to a faint edge softening
    b1, b2 = 0.9 * p.glow_scale, 3.6 * p.glow_scale
    return f'''
  <radialGradient id="{prefix}Deep" cx="16%" cy="50%" r="88%">
    <stop offset="0%" stop-color="{p.bg_inner}" stop-opacity="{p.glass_top}"/>
    <stop offset="46%" stop-color="{p.bg_mid}" stop-opacity="{(p.glass_top+p.glass_bottom)/2:.2f}"/>
    <stop offset="100%" stop-color="{p.bg_outer}" stop-opacity="{p.glass_bottom}"/>
  </radialGradient>
  <radialGradient id="{prefix}Vig" cx="50%" cy="50%" r="74%">
    <stop offset="58%" stop-color="{p.vignette}" stop-opacity="0"/>
    <stop offset="100%" stop-color="{p.vignette}" stop-opacity="{p.vignette_opacity}"/>
  </radialGradient>
  <radialGradient id="{prefix}Core" cx="50%" cy="42%" r="58%">{core}</radialGradient>
  <linearGradient id="{prefix}Sweep" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{p.cyan}" stop-opacity="0"/>
    <stop offset="52%" stop-color="{p.cyan}" stop-opacity="0.45"/>
    <stop offset="100%" stop-color="{p.cyan}" stop-opacity="0"/>
  </linearGradient>
  <filter id="{prefix}Bevel" x="-60%" y="-60%" width="220%" height="220%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="1.4" result="hh"/>
    <feSpecularLighting in="hh" surfaceScale="3.6" specularConstant="0.85"
                        specularExponent="26" lighting-color="#dff6ff" result="s">
      <fePointLight x="{lx}" y="{ly}" z="{lz}">
        <animate attributeName="x" values="{lx};{-lx};{lx}" dur="9s" repeatCount="indefinite"/>
        <animate attributeName="y" values="{ly};{-ly};{ly}" dur="13s" repeatCount="indefinite"/>
      </fePointLight>
    </feSpecularLighting>
    <feComposite in="s" in2="SourceAlpha" operator="in" result="sc"/>
    <feComposite in="SourceGraphic" in2="sc" operator="arithmetic" k1="0" k2="1" k3="{0.9 * p.glow_scale:.2f}" k4="0"/>
  </filter>
  <filter id="{prefix}Glow" x="-200%" y="-200%" width="500%" height="500%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="{b1:.2f}" result="a"/>
    <feGaussianBlur in="SourceGraphic" stdDeviation="{b2:.2f}" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="a"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="{prefix}Grain" x="0%" y="0%" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3" seed="5" result="n">
      <animate attributeName="seed" values="5;13;21;5" dur="1.3s" calcMode="discrete" repeatCount="indefinite"/>
    </feTurbulence>
    <feColorMatrix in="n" type="matrix"
      values="0 0 0 0 0.12  0 0 0 0 0.66  0 0 0 0 0.8  0 0 0 {p.grain_alpha} 0"/>
  </filter>
  <pattern id="{prefix}Scan" width="3" height="3" patternUnits="userSpaceOnUse">
    <rect width="3" height="0.8" fill="{p.scan_colour}" opacity="{p.scan_opacity}"/>
  </pattern>
  <clipPath id="{prefix}Clip"><rect width="{w}" height="{h}" rx="3"/></clipPath>
  <style>.t{{font-family:{MONO};}}</style>'''


def atmosphere(prefix: str, w: int, h: int, p: Palette, sweep_dur: str = "9s") -> str:
    return f'''
  <rect x="{-w//3}" y="0" width="{w//3}" height="{h}" fill="url(#{prefix}Sweep)" opacity="{p.sweep_opacity}">
    <animate attributeName="x" values="{-w//3};{w}" dur="{sweep_dur}" repeatCount="indefinite"/>
  </rect>
  <rect width="{w}" height="{h}" fill="url(#{prefix}Scan)" opacity="0.34"/>
  <rect width="{w}" height="{h}" filter="url(#{prefix}Grain)" opacity="{p.grain_opacity}"/>
  <rect width="{w}" height="{h}" fill="url(#{prefix}Vig)"/>'''


def frame(w: int, h: int, p: Palette, inset: int = 10, arm: int = 42) -> str:
    return f'''
  <g stroke="{p.cyan}" stroke-width="{LINE}" fill="none" opacity="0.8">
    <path d="M{inset} {inset+24} V{inset} H{inset+arm}"/>
    <path d="M{w-inset} {inset+24} V{inset} H{w-inset-arm}"/>
    <path d="M{inset} {h-inset-24} V{h-inset} H{inset+arm}"/>
    <path d="M{w-inset} {h-inset-24} V{h-inset} H{w-inset-arm}"/>
  </g>
  <rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="3" fill="none"
        stroke="{p.edge}" stroke-width="0.5" opacity="0.5"/>'''


PAD = 7          # room inside the viewBox for the drop shadow
BAR = 21         # title bar height


def _legacy_chrome_defs(prefix: str, p: Palette) -> str:
    """Gradients and filters that give a panel physical thickness.

    A flat rectangle reads as a diagram; a panel needs a cast shadow, a lit top
    edge and a body that falls off towards the bottom before it sits *above*
    the page rather than on it.
    """
    lit = "#ffffff" if p.key == "dark" else "#ffffff"
    return f'''
  <linearGradient id="{prefix}Body" x1="0" y1="0" x2="0.3" y2="1">
    <stop offset="0%" stop-color="{p.bg_inner}" stop-opacity="{p.glass_top}"/>
    <stop offset="52%" stop-color="{p.bg_mid}" stop-opacity="{(p.glass_top+p.glass_bottom)/2:.2f}"/>
    <stop offset="100%" stop-color="{p.bg_outer}" stop-opacity="{p.glass_bottom}"/>
  </linearGradient>
  <linearGradient id="{prefix}Bar" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{p.cyan}" stop-opacity="{0.16 if p.key == 'dark' else 0.13}"/>
    <stop offset="100%" stop-color="{p.cyan}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="{prefix}Lip" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{lit}" stop-opacity="0"/>
    <stop offset="18%" stop-color="{lit}" stop-opacity="{0.42 if p.key == 'dark' else 0.9}"/>
    <stop offset="82%" stop-color="{lit}" stop-opacity="{0.42 if p.key == 'dark' else 0.9}"/>
    <stop offset="100%" stop-color="{lit}" stop-opacity="0"/>
  </linearGradient>
  <filter id="{prefix}Drop" x="-12%" y="-12%" width="124%" height="130%">
    <feDropShadow dx="0" dy="2.4" stdDeviation="3.4"
                  flood-color="{'#000000' if p.key == 'dark' else '#33586b'}"
                  flood-opacity="{0.65 if p.key == 'dark' else 0.22}"/>
  </filter>'''


def chrome(prefix: str, w: int, h: int, p: Palette, title: str,
           right: str = "", radius: float = 18) -> str:
    """A tile: one sheet of liquid glass with a title bar floated on top of it."""
    x, y = PAD, PAD
    iw, ih = w - 2 * PAD, h - 2 * PAD
    return f'''
{glass_body(prefix, x, y, iw, ih, p, radius)}
{liquid(prefix, x, y, iw, ih, p, seed=len(title))}
  <path d="M{x + radius * 0.5:.1f} {y + BAR} H{x + iw - radius * 0.5:.1f}"
        stroke="{p.edge}" stroke-width="0.5" opacity="0.4"/>
  <g class="t">
    <circle cx="{x+15}" cy="{y+12}" r="2.6" fill="none" stroke="{p.cyan}" stroke-width="{HAIR}"/>
    <circle cx="{x+15}" cy="{y+12}" r="0.9" fill="{p.cyan}"/>
    <text x="{x+24}" y="{y+15}" fill="{p.cyan}" font-size="7.4" letter-spacing="2.8">{title}</text>
    <text x="{x+iw-14}" y="{y+15}" fill="{p.dim}" font-size="6.8" letter-spacing="1.8"
          text-anchor="end">{right}</text>
  </g>'''


def glass_shape_clip(prefix: str, w: int, h: int, radius: float = 18) -> str:
    """The clip every glass effect is bounded by."""
    return (f'<clipPath id="{prefix}Shape">'
            f'<path d="{squircle(PAD, PAD, w - 2*PAD, h - 2*PAD, radius)}"/></clipPath>')


# --------------------------------------------------------------------------- liquid glass
def squircle(x: float, y: float, w: float, h: float, r: float) -> str:
    """A continuous-curvature rounded rectangle.

    A plain `rx` corner jumps from straight to circular in one step, which is
    what makes a rounded box read as a box. Extending the corner region and
    pulling the control points further along it removes that break, which is
    the shape Apple's glass sits in.
    """
    r = min(r, w / 2, h / 2)
    e = r * 1.42          # how far the corner reaches along each edge
    c = r * 0.62          # control-point pull back towards the corner
    x2, y2 = x + w, y + h
    return (f"M{x+e:.2f} {y:.2f}"
            f"L{x2-e:.2f} {y:.2f}"
            f"C{x2-c:.2f} {y:.2f} {x2:.2f} {y+c:.2f} {x2:.2f} {y+e:.2f}"
            f"L{x2:.2f} {y2-e:.2f}"
            f"C{x2:.2f} {y2-c:.2f} {x2-c:.2f} {y2:.2f} {x2-e:.2f} {y2:.2f}"
            f"L{x+e:.2f} {y2:.2f}"
            f"C{x+c:.2f} {y2:.2f} {x:.2f} {y2-c:.2f} {x:.2f} {y2-e:.2f}"
            f"L{x:.2f} {y+e:.2f}"
            f"C{x:.2f} {y+c:.2f} {x+c:.2f} {y:.2f} {x+e:.2f} {y:.2f}Z")


def glass_defs(prefix: str, w: int, h: int, p: Palette) -> str:
    """Gradients and filters for one sheet of liquid glass."""
    dark = p.key == "dark"
    return f'''
  <linearGradient id="{prefix}Glass" x1="0.1" y1="0" x2="0.6" y2="1">
    <stop offset="0%"   stop-color="{p.bg_inner}" stop-opacity="{p.glass_top}"/>
    <stop offset="38%"  stop-color="{p.bg_mid}"   stop-opacity="{(p.glass_top+p.glass_bottom)/2:.2f}"/>
    <stop offset="100%" stop-color="{p.bg_outer}" stop-opacity="{p.glass_bottom}"/>
  </linearGradient>

  <!-- the rim catches light twice: once top-left, once bottom-right -->
  <linearGradient id="{prefix}Rim" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%"   stop-color="#ffffff" stop-opacity="{0.85 if dark else 1}"/>
    <stop offset="16%"  stop-color="{p.cyan}" stop-opacity="{0.72 if dark else 0.55}"/>
    <stop offset="45%"  stop-color="{p.edge}" stop-opacity="{0.24 if dark else 0.2}"/>
    <stop offset="72%"  stop-color="{p.cyan}" stop-opacity="{0.5 if dark else 0.4}"/>
    <stop offset="100%" stop-color="#ffffff" stop-opacity="{0.55 if dark else 0.75}"/>
  </linearGradient>

  <!-- light bends through the thickness at the edge, so the rim band is not flat -->
  <linearGradient id="{prefix}Refract" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%"   stop-color="#ffffff" stop-opacity="{0.42 if dark else 0.85}"/>
    <stop offset="24%"  stop-color="#ffffff" stop-opacity="0"/>
    <stop offset="76%"  stop-color="{p.cyan}" stop-opacity="0"/>
    <stop offset="100%" stop-color="{p.cyan}" stop-opacity="{0.22 if dark else 0.3}"/>
  </linearGradient>

  <linearGradient id="{prefix}Sheen" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%"   stop-color="#ffffff" stop-opacity="0"/>
    <stop offset="45%"  stop-color="#ffffff" stop-opacity="{0.5 if dark else 0.8}"/>
    <stop offset="55%"  stop-color="#ffffff" stop-opacity="{0.5 if dark else 0.8}"/>
    <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
  </linearGradient>

  <radialGradient id="{prefix}Blob" cx="42%" cy="36%" r="62%">
    <stop offset="0%"   stop-color="{p.cyan}" stop-opacity="{0.5 if dark else 0.42}"/>
    <stop offset="65%"  stop-color="{p.cyan}" stop-opacity="{0.22 if dark else 0.18}"/>
    <stop offset="100%" stop-color="{p.cyan}" stop-opacity="0"/>
  </radialGradient>

  <!-- blobs blurred then hard-thresholded: near ones merge, parting ones neck -->
  <filter id="{prefix}Goo" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="9" result="soft"/>
    <feColorMatrix in="soft" type="matrix" result="goo"
      values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 11 -4.6"/>
    <feGaussianBlur in="goo" stdDeviation="7"/>
  </filter>

  <filter id="{prefix}Cast" x="-16%" y="-16%" width="132%" height="140%">
    <feDropShadow dx="0" dy="{3.2 if dark else 2.6}" stdDeviation="{5 if dark else 4}"
                  flood-color="{'#000814' if dark else '#2c5468'}"
                  flood-opacity="{0.62 if dark else 0.2}"/>
  </filter>'''


def liquid(prefix: str, x: float, y: float, w: float, h: float, p: Palette,
           seed: int = 0) -> str:
    """Blobs drifting behind the content, merging where they meet."""
    import math as _m
    blobs = []
    for i in range(3):
        a = seed * 1.7 + i * 2.1
        r = min(w, h) * (0.22 + 0.07 * ((i + seed) % 3))
        cx0 = x + w * (0.22 + 0.28 * ((i * 3 + seed) % 3))
        cy0 = y + h * (0.34 + 0.22 * ((i * 2 + seed) % 2))
        dx = w * 0.13 * _m.cos(a)
        dy = h * 0.16 * _m.sin(a * 1.3)
        dur = 17 + i * 6 + (seed % 3) * 3
        blobs.append(
            f'<circle r="{r:.1f}" fill="url(#{prefix}Blob)">'
            f'<animate attributeName="cx" values="{cx0:.1f};{cx0+dx:.1f};{cx0-dx*0.7:.1f};{cx0:.1f}" '
            f'dur="{dur}s" repeatCount="indefinite" calcMode="spline" '
            f'keyTimes="0;0.33;0.66;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1;0.4 0 0.6 1"/>'
            f'<animate attributeName="cy" values="{cy0:.1f};{cy0-dy:.1f};{cy0+dy*0.8:.1f};{cy0:.1f}" '
            f'dur="{dur*1.3:.0f}s" repeatCount="indefinite" calcMode="spline" '
            f'keyTimes="0;0.33;0.66;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1;0.4 0 0.6 1"/>'
            f'</circle>')
    return (f'<g clip-path="url(#{prefix}Shape)" filter="url(#{prefix}Goo)" '
            f'opacity="{0.24 if p.key == "dark" else 0.22}">{"".join(blobs)}</g>')


def glass_body(prefix: str, x: float, y: float, w: float, h: float,
               p: Palette, radius: float = 20, seed: int = 0) -> str:
    """The sheet: shadow, back face, liquid *inside* the material, then the
    front face over it.

    Order matters. Blobs painted on top of the glass read as bubbles sitting on
    a window; painted underneath the front face they read as something moving
    within it, which is the whole point of the material.
    """
    path = squircle(x, y, w, h, radius)
    inner = squircle(x + 1.6, y + 1.6, w - 3.2, h - 3.2, radius - 1.6)
    return f'''
  <path d="{path}" fill="{p.bg_outer}" opacity="{0.5 if p.key == 'dark' else 0.24}" filter="url(#{prefix}Cast)"/>
  <path d="{path}" fill="url(#{prefix}Glass)"/>
{liquid(prefix, x, y, w, h, p, seed)}
  <path d="{path}" fill="url(#{prefix}Glass)" opacity="0.55"/>
  <path d="{path}" fill="url(#{prefix}Refract)" opacity="0.9"/>
  <g clip-path="url(#{prefix}Shape)">
    <rect x="{x-w*0.55:.1f}" y="{y}" width="{w*0.55:.1f}" height="{h}"
          fill="url(#{prefix}Sheen)" opacity="{0.2 if p.key == 'dark' else 0.5}"
          transform="skewX(-14)">
      <animate attributeName="x" values="{x-w*0.6:.1f};{x+w*1.15:.1f}"
               dur="14s" repeatCount="indefinite"/>
    </rect>
  </g>
  <path d="{inner}" fill="none" stroke="#ffffff" stroke-width="0.5"
        opacity="{0.32 if p.key == 'dark' else 0.55}"/>
  <path d="{path}" fill="none" stroke="url(#{prefix}Rim)" stroke-width="1.2"/>'''


