"""One palette and one set of line weights for every panel.

Hairline is the rule: nothing structural is drawn heavier than 1.2, so the
interface reads as an instrument rather than an illustration.
"""

CYAN   = "#5fd8f2"
CYAN_D = "#1e9bbd"
GOLD   = "#e8b455"
DIM    = "#3f7f96"
FAINT  = "#123murk"          # replaced below
PALE   = "#cfeefb"
WHITE  = "#f2fdff"
INK    = "#01050a"

FAINT = "#12384a"

# contribution intensity ramp (level 0 .. 4)
RAMP = ["#1b4055", "#12617a", "#1e9bbd", "#4fd0ee", "#a8f0ff"]

HAIR   = 0.6
LINE   = 0.9
ACCENT = 1.2

MONO = '"SFMono-Regular","SF Mono",Menlo,Consolas,"DejaVu Sans Mono",monospace'


def defs(prefix: str, w: int, h: int, *, light=(-70, -70, 60)) -> str:
    """Shared gradients / filters, namespaced so several panels can coexist."""
    lx, ly, lz = light
    return f'''
  <radialGradient id="{prefix}Deep" cx="16%" cy="50%" r="88%">
    <stop offset="0%" stop-color="#07202b"/><stop offset="46%" stop-color="#040f18"/>
    <stop offset="100%" stop-color="{INK}"/>
  </radialGradient>
  <radialGradient id="{prefix}Vig" cx="50%" cy="50%" r="74%">
    <stop offset="58%" stop-color="#000" stop-opacity="0"/>
    <stop offset="100%" stop-color="#000" stop-opacity="0.6"/>
  </radialGradient>
  <radialGradient id="{prefix}Core" cx="50%" cy="42%" r="58%">
    <stop offset="0%" stop-color="#fff"/><stop offset="26%" stop-color="#dff8ff"/>
    <stop offset="60%" stop-color="#54c8e8" stop-opacity="0.62"/>
    <stop offset="100%" stop-color="#0a4b61" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="{prefix}Sweep" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{CYAN}" stop-opacity="0"/>
    <stop offset="52%" stop-color="#bdeeff" stop-opacity="0.45"/>
    <stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/>
  </linearGradient>
  <filter id="{prefix}Bevel" x="-60%" y="-60%" width="220%" height="220%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="1.4" result="h"/>
    <feSpecularLighting in="h" surfaceScale="3.6" specularConstant="0.85"
                        specularExponent="26" lighting-color="#dff6ff" result="s">
      <fePointLight x="{lx}" y="{ly}" z="{lz}">
        <animate attributeName="x" values="{lx};{-lx};{lx}" dur="9s" repeatCount="indefinite"/>
        <animate attributeName="y" values="{ly};{-ly};{ly}" dur="13s" repeatCount="indefinite"/>
      </fePointLight>
    </feSpecularLighting>
    <feComposite in="s" in2="SourceAlpha" operator="in" result="sc"/>
    <feComposite in="SourceGraphic" in2="sc" operator="arithmetic" k1="0" k2="1" k3="0.9" k4="0"/>
  </filter>
  <filter id="{prefix}Glow" x="-200%" y="-200%" width="500%" height="500%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="0.9" result="a"/>
    <feGaussianBlur in="SourceGraphic" stdDeviation="3.6" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="a"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="{prefix}Grain" x="0%" y="0%" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3" seed="5" result="n">
      <animate attributeName="seed" values="5;13;21;5" dur="1.3s" calcMode="discrete" repeatCount="indefinite"/>
    </feTurbulence>
    <feColorMatrix in="n" type="matrix"
      values="0 0 0 0 0.12  0 0 0 0 0.66  0 0 0 0 0.8  0 0 0 0.18 0"/>
  </filter>
  <pattern id="{prefix}Scan" width="3" height="3" patternUnits="userSpaceOnUse">
    <rect width="3" height="0.8" fill="#0a3242" opacity="0.28"/>
  </pattern>
  <clipPath id="{prefix}Clip"><rect width="{w}" height="{h}" rx="3"/></clipPath>
  <style>.t{{font-family:{MONO};}}</style>'''


def atmosphere(prefix: str, w: int, h: int, sweep_dur: str = "9s") -> str:
    return f'''
  <rect x="{-w//3}" y="0" width="{w//3}" height="{h}" fill="url(#{prefix}Sweep)" opacity="0.09">
    <animate attributeName="x" values="{-w//3};{w}" dur="{sweep_dur}" repeatCount="indefinite"/>
  </rect>
  <rect width="{w}" height="{h}" fill="url(#{prefix}Scan)" opacity="0.34"/>
  <rect width="{w}" height="{h}" filter="url(#{prefix}Grain)" opacity="0.32"/>
  <rect width="{w}" height="{h}" fill="url(#{prefix}Vig)"/>'''


def frame(w: int, h: int, inset: int = 10, arm: int = 42) -> str:
    return f'''
  <g stroke="{CYAN}" stroke-width="{LINE}" fill="none" opacity="0.8">
    <path d="M{inset} {inset+24} V{inset} H{inset+arm}"/>
    <path d="M{w-inset} {inset+24} V{inset} H{w-inset-arm}"/>
    <path d="M{inset} {h-inset-24} V{h-inset} H{inset+arm}"/>
    <path d="M{w-inset} {h-inset-24} V{h-inset} H{w-inset-arm}"/>
  </g>
  <rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="3" fill="none"
        stroke="{DIM}" stroke-width="0.8" opacity="0.6"/>'''
