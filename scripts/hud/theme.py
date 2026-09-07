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
    dispersion: tuple[str, str, str, str, str]  # hues the edge splits light into


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
    glass_top=0.5, glass_bottom=0.3, edge="#7fe4fa",
    dispersion=("#7fe4fa", "#69f0d0", "#eaf6ff", "#b79cff", "#ffcf7a"),
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
    glass_top=0.4, glass_bottom=0.2, edge="#0e7490",
    dispersion=("#2aa6c4", "#3fc9a8", "#ffffff", "#8f7ae0", "#e0a54a"),
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


# --------------------------------------------------------------------------- glass

def slab(x: float, y: float, w: float, h: float) -> str:
    """A plain rectangular sheet. Real plate glass is cut, not moulded."""
    return f"M{x:.2f} {y:.2f}H{x+w:.2f}V{y+h:.2f}H{x:.2f}Z"


def squircle(x: float, y: float, w: float, h: float, r: float = 0) -> str:
    """Kept for callers that still pass a radius; r=0 gives the plain slab."""
    if r <= 0.01:
        return slab(x, y, w, h)
    r = min(r, w / 2, h / 2)
    e, c = r * 1.42, r * 0.62
    x2, y2 = x + w, y + h
    return (f"M{x+e:.2f} {y:.2f}L{x2-e:.2f} {y:.2f}"
            f"C{x2-c:.2f} {y:.2f} {x2:.2f} {y+c:.2f} {x2:.2f} {y+e:.2f}"
            f"L{x2:.2f} {y2-e:.2f}C{x2:.2f} {y2-c:.2f} {x2-c:.2f} {y2:.2f} {x2-e:.2f} {y2:.2f}"
            f"L{x+e:.2f} {y2:.2f}C{x+c:.2f} {y2:.2f} {x:.2f} {y2-c:.2f} {x:.2f} {y2-e:.2f}"
            f"L{x:.2f} {y+e:.2f}C{x:.2f} {y+c:.2f} {x+c:.2f} {y:.2f} {x+e:.2f} {y:.2f}Z")


def glass_defs(prefix: str, w: int, h: int, p: Palette) -> str:
    """The optics of one sheet of glass.

    Three things make glass look like glass rather than a tinted rectangle:
    it is most transparent where you look straight through it and most
    reflective at a grazing angle (Fresnel), its edges split light into colour
    (dispersion), and its corners concentrate that light into a glint.
    """
    dark = p.key == "dark"
    a, b, c, d, e = p.dispersion
    return f'''
  <!-- Fresnel: transparent looking straight through, reflective at the edges -->
  <linearGradient id="{prefix}Face" x1="0.12" y1="0" x2="0.55" y2="1">
    <stop offset="0%"   stop-color="{p.bg_inner}" stop-opacity="{p.glass_top}"/>
    <stop offset="46%"  stop-color="{p.bg_mid}"   stop-opacity="{p.glass_bottom}"/>
    <stop offset="100%" stop-color="{p.bg_outer}" stop-opacity="{(p.glass_top+p.glass_bottom)/2:.2f}"/>
  </linearGradient>
  <linearGradient id="{prefix}EdgeV" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%"   stop-color="{p.bg_inner}" stop-opacity="{0.5 if dark else 0.55}"/>
    <stop offset="14%"  stop-color="{p.bg_mid}"   stop-opacity="0"/>
    <stop offset="86%"  stop-color="{p.bg_outer}" stop-opacity="0"/>
    <stop offset="100%" stop-color="{p.bg_outer}" stop-opacity="{0.62 if dark else 0.34}"/>
  </linearGradient>

  <!-- dispersion: the hues travel along the edge, so the colour itself flows -->
  <linearGradient id="{prefix}Iris" x1="0" y1="0" x2="1" y2="0.35"
                  gradientUnits="objectBoundingBox">
    <stop offset="0.00" stop-color="{a}"/>
    <stop offset="0.26" stop-color="{b}"/>
    <stop offset="0.48" stop-color="{c}"/>
    <stop offset="0.71" stop-color="{d}"/>
    <stop offset="1.00" stop-color="{e}"/>
    <animate attributeName="x1" values="-1;0;1" dur="19s" repeatCount="indefinite"/>
    <animate attributeName="x2" values="0;1;2" dur="19s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="{prefix}IrisSoft" x1="0" y1="0" x2="1" y2="0.6">
    <stop offset="0.00" stop-color="{b}" stop-opacity="{0.4 if dark else 0.36}"/>
    <stop offset="0.34" stop-color="{c}" stop-opacity="{0.3 if dark else 0.28}"/>
    <stop offset="0.62" stop-color="{d}" stop-opacity="{0.36 if dark else 0.32}"/>
    <stop offset="1.00" stop-color="{a}" stop-opacity="{0.32 if dark else 0.3}"/>
    <animate attributeName="x1" values="-0.8;0.2;1.2" dur="26s" repeatCount="indefinite"/>
    <animate attributeName="x2" values="0.2;1.2;2.2" dur="26s" repeatCount="indefinite"/>
  </linearGradient>

  <!-- the polished top arris, and the ground bottom one -->
  <linearGradient id="{prefix}Arris" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%"   stop-color="#ffffff" stop-opacity="0"/>
    <stop offset="8%"   stop-color="#ffffff" stop-opacity="{0.7 if dark else 0.95}"/>
    <stop offset="55%"  stop-color="#ffffff" stop-opacity="{0.3 if dark else 0.6}"/>
    <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
  </linearGradient>

  <linearGradient id="{prefix}Sheen" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%"   stop-color="#ffffff" stop-opacity="0"/>
    <stop offset="50%"  stop-color="#ffffff" stop-opacity="{0.42 if dark else 0.72}"/>
    <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
  </linearGradient>

  <!-- a corner glint: light funnelled into the 90-degree arris -->
  <radialGradient id="{prefix}Glint" cx="50%" cy="50%" r="50%">
    <stop offset="0%"   stop-color="#ffffff" stop-opacity="{0.85 if dark else 1}"/>
    <stop offset="38%"  stop-color="{c}" stop-opacity="{0.4 if dark else 0.45}"/>
    <stop offset="100%" stop-color="{c}" stop-opacity="0"/>
  </radialGradient>

  <filter id="{prefix}Cast" x="-14%" y="-14%" width="128%" height="140%">
    <feDropShadow dx="0" dy="{4 if dark else 3}" stdDeviation="{6 if dark else 4.5}"
                  flood-color="{'#00070f' if dark else '#26495c'}"
                  flood-opacity="{0.7 if dark else 0.32}"/>
  </filter>
  <filter id="{prefix}Caustic" x="-40%" y="-60%" width="180%" height="260%">
    <feGaussianBlur stdDeviation="5"/>
  </filter>'''


def glass_body(prefix: str, x: float, y: float, w: float, h: float,
               p: Palette, radius: float = 0, seed: int = 0) -> str:
    """Shadow with its caustic, the sheet, the dispersed edges, the corners."""
    dark = p.key == "dark"
    path = slab(x, y, w, h)
    band = 9                       # how far the Fresnel edge reaches inward
    gl = 10                        # corner glint radius
    corners = "".join(
        f'<ellipse cx="{cx}" cy="{cy}" rx="{gl}" ry="{gl}" fill="url(#{prefix}Glint)" '
        f'opacity="{o}"/>'
        for cx, cy, o in ((x, y, 0.7), (x + w, y, 0.4),
                          (x, y + h, 0.28), (x + w, y + h, 0.45)))
    return f'''
  <path d="{path}" fill="{p.bg_outer}" opacity="{0.55 if dark else 0.26}" filter="url(#{prefix}Cast)"/>
  <rect x="{x+w*0.16:.1f}" y="{y+h+2:.1f}" width="{w*0.68:.1f}" height="7"
        fill="url(#{prefix}IrisSoft)" opacity="{0.3 if dark else 0.42}" filter="url(#{prefix}Caustic)"/>

  <path d="{path}" fill="url(#{prefix}Face)"/>
  <path d="{path}" fill="url(#{prefix}EdgeV)"/>

  <!-- edge band: dispersion strongest where the sheet is seen at a grazing angle -->
  <g clip-path="url(#{prefix}Shape)">
    <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none"
          stroke="url(#{prefix}IrisSoft)" stroke-width="{band*2}"
          opacity="{0.17 if dark else 0.2}"/>
    <rect x="{x-w*0.5:.1f}" y="{y}" width="{w*0.5:.1f}" height="{h}"
          fill="url(#{prefix}Sheen)" opacity="{0.1 if dark else 0.34}" transform="skewX(-12)">
      <animate attributeName="x" values="{x-w*0.55:.1f};{x+w*1.1:.1f}" dur="17s" repeatCount="indefinite"/>
    </rect>
    {corners}
  </g>

  <!-- polished arris along the top, ground edge along the bottom -->
  <path d="M{x+0.5:.1f} {y+0.5:.1f}H{x+w-0.5:.1f}" stroke="url(#{prefix}Arris)" stroke-width="1"/>
  <path d="M{x+0.5:.1f} {y+h-0.5:.1f}H{x+w-0.5:.1f}" stroke="{p.bg_outer}" stroke-width="1"
        opacity="{0.75 if dark else 0.3}"/>
  <path d="{path}" fill="none" stroke="url(#{prefix}Iris)" stroke-width="0.9"
        opacity="{0.5 if dark else 0.6}"/>'''


def glass_shape_clip(prefix: str, w: int, h: int, radius: float = 0) -> str:
    return (f'<clipPath id="{prefix}Shape">'
            f'<path d="{slab(PAD, PAD, w - 2*PAD, h - 2*PAD)}"/></clipPath>')
def chrome(prefix: str, w: int, h: int, p: Palette, title: str,
           right: str = "", radius: float = 0) -> str:
    """A tile: one sheet of glass with a title bar floated on top of it."""
    x, y = PAD, PAD
    iw, ih = w - 2 * PAD, h - 2 * PAD
    return f'''
{glass_body(prefix, x, y, iw, ih, p, radius)}
  <path d="M{x+10} {y + BAR} H{x + iw - 10}"
        stroke="url(#{prefix}IrisSoft)" stroke-width="0.6" opacity="0.75"/>
  <g class="t">
    <circle cx="{x+15}" cy="{y+12}" r="2.6" fill="none" stroke="{p.cyan}" stroke-width="{HAIR}"/>
    <circle cx="{x+15}" cy="{y+12}" r="0.9" fill="{p.cyan}"/>
    <text x="{x+24}" y="{y+15}" fill="{p.cyan}" font-size="7.4" letter-spacing="2.8">{title}</text>
    <text x="{x+iw-14}" y="{y+15}" fill="{p.dim}" font-size="6.8" letter-spacing="1.8"
          text-anchor="end">{right}</text>
  </g>'''
