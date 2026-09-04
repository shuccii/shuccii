"""Two palettes, one geometry.

The dark panel is a lit instrument; the light panel is the same instrument
drawn as a blueprint on paper. Line weights, positions and data are identical —
only colour, glow and film grain change, so both variants stay in register.

Hairline is the rule: nothing structural is heavier than 1.2.
"""
from __future__ import annotations

from dataclasses import dataclass, field

HAIR = 0.6
LINE = 0.9
ACCENT = 1.2

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


DARK = Palette(
    key="dark",
    bg_inner="#07202b", bg_mid="#040f18", bg_outer="#01050a",
    cyan="#5fd8f2", cyan_deep="#1e9bbd", gold="#e8b455",
    dim="#3f7f96", faint="#12384a", pale="#cfeefb", ink="#f2fdff",
    metal="#17536b",
    core_stops=(("0%", "#ffffff", "1"), ("26%", "#dff8ff", "1"),
                ("60%", "#54c8e8", "0.62"), ("100%", "#0a4b61", "0")),
    ramp=["#1b4055", "#12617a", "#1e9bbd", "#4fd0ee", "#a8f0ff"],
    scan_colour="#0a3242", scan_opacity=0.28,
    grain_alpha=0.18, grain_opacity=0.32,
    vignette="#000000", vignette_opacity=0.6,
    glow_scale=1.0, aberration=0.26, sweep_opacity=0.09,
    pulse="#eafcff",
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
    <stop offset="0%" stop-color="{p.bg_inner}"/><stop offset="46%" stop-color="{p.bg_mid}"/>
    <stop offset="100%" stop-color="{p.bg_outer}"/>
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
        stroke="{p.dim}" stroke-width="0.8" opacity="0.6"/>'''
