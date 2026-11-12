#!/usr/bin/env python3
"""Generate assets/rgb-pc.svg — a 3D RGB gaming PC (animated SVG).

Hand-built vector art: tower with glass side panel (GPU, CPU cooler,
RGB RAM), 3 front RGB fans, RGB edge strips, underglow. Fans spin and
the RGB hues cycle via CSS animations (rendered by GitHub in the README).
Run: python3 scripts/gen_rgb_pc.py
"""
import math

RAINBOW = "#ff004c,#ff8a00,#ffee00,#00e676,#00cfff,#7b2fff,#ff004c"


def fan_blades(cx, cy, r, cls, dur, reverse=False):
    """One RGB fan: ring + 7 blades + hub. Blades spin via CSS."""
    blades = []
    for i in range(7):
        a = i * (360 / 7)
        # Petal blade pointing outward, swept clockwise.
        blades.append(
            f'<path d="M0 0 C {r*0.28:.1f} {-r*0.55:.1f} {r*0.78:.1f} {-r*0.62:.1f} '
            f'{r*0.92:.1f} {-r*0.18:.1f} C {r*0.72:.1f} {r*0.12:.1f} {r*0.3:.1f} {r*0.16:.1f} 0 0 Z" '
            f'transform="rotate({a})" fill="url(#rgbGrad)" opacity="0.92"/>'
        )
    direction = "reverse" if reverse else "normal"
    return f"""
<g transform="translate({cx} {cy})">
  <circle r="{r}" fill="none" stroke="url(#rgbGrad)" stroke-width="4" class="rgb"/>
  <circle r="{r - 9}" fill="none" stroke="#ffffff" stroke-opacity="0.14" stroke-width="1.5"/>
  <g class="{cls}" style="animation-duration:{dur}s;animation-direction:{direction}">
    {''.join(blades)}
  </g>
  <circle r="{r * 0.26:.1f}" fill="#0d1117" stroke="#2b323d" stroke-width="2"/>
  <circle r="3" fill="#00F0FF"/>
</g>"""


def main():
    fans = (
        fan_blades(241, 132, 40, "fan", 6)
        + fan_blades(241, 222, 40, "fan", 8, reverse=True)
        + fan_blades(241, 312, 40, "fan", 7)
    )
    gpu_fans = fan_blades(368, 272, 15, "fan", 5) + fan_blades(428, 272, 15, "fan", 5, reverse=True)
    cooler_fan = fan_blades(432, 158, 26, "fan", 6, reverse=True)
    ram = "".join(
        f'<rect x="{x}" y="104" width="11" height="86" rx="3" fill="#1a212b" stroke="#2b323d"/>'
        f'<rect x="{x}" y="104" width="11" height="12" rx="3" fill="url(#rgbGrad)" class="rgb"/>'
        for x in (498, 514, 530, 546)
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="760" height="440" viewBox="0 0 760 440">
<defs>
  <linearGradient id="rgbGrad" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#ff004c"/><stop offset="16%" stop-color="#ff8a00"/>
    <stop offset="33%" stop-color="#ffee00"/><stop offset="50%" stop-color="#00e676"/>
    <stop offset="66%" stop-color="#00cfff"/><stop offset="83%" stop-color="#7b2fff"/>
    <stop offset="100%" stop-color="#ff004c"/>
  </linearGradient>
  <linearGradient id="caseGrad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#232a33"/><stop offset="100%" stop-color="#12161c"/>
  </linearGradient>
  <linearGradient id="gpuGrad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#232c38"/><stop offset="100%" stop-color="#12161d"/>
  </linearGradient>
  <radialGradient id="glowGrad" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#00F0FF" stop-opacity="0.55"/>
    <stop offset="55%" stop-color="#7b2fff" stop-opacity="0.22"/>
    <stop offset="100%" stop-color="#7b2fff" stop-opacity="0"/>
  </radialGradient>
  <clipPath id="glassClip"><rect x="300" y="70" width="264" height="300" rx="8"/></clipPath>
  <style>
    .fan{{animation:spin 7s linear infinite;transform-box:fill-box;transform-origin:center}}
    @keyframes spin{{to{{transform:rotate(360deg)}}}}
    .rgb{{animation:hue 6s linear infinite}}
    @keyframes hue{{to{{filter:hue-rotate(360deg)}}}}
    .underglow{{animation:pulse 3s ease-in-out infinite}}
    @keyframes pulse{{0%,100%{{opacity:.35}}50%{{opacity:.65}}}}
    .pwr{{animation:pulse 2s ease-in-out infinite}}
  </style>
</defs>
<ellipse class="underglow" cx="395" cy="404" rx="285" ry="20" fill="url(#glowGrad)"/>
<!-- 3D box: top + right faces -->
<polygon points="180,50 210,26 610,26 580,50" fill="#2b323d"/>
<polygon points="580,50 610,26 610,366 580,390" fill="#12161c"/>
<!-- front face -->
<rect x="180" y="50" width="400" height="340" fill="url(#caseGrad)" stroke="#000" stroke-opacity="0.4"/>
<!-- RGB edge strips -->
<rect x="180" y="50" width="6" height="340" fill="url(#rgbGrad)" class="rgb"/>
<rect x="180" y="384" width="400" height="6" fill="url(#rgbGrad)" class="rgb"/>
<!-- front RGB fans -->
{fans}
<!-- power button -->
<circle class="pwr" cx="556" cy="64" r="5" fill="#00F0FF"/>
<rect x="536" y="60" width="12" height="8" rx="2" fill="#2b323d"/>
<!-- glass side panel -->
<g clip-path="url(#glassClip)">
  <rect x="300" y="70" width="264" height="300" fill="#070a0e"/>
  <rect x="312" y="84" width="240" height="272" rx="6" fill="#10151c" stroke="#ffffff" stroke-opacity="0.06"/>
  <!-- motherboard traces -->
  <path d="M312 150 H552 M312 210 H552 M312 320 H552" stroke="#ffffff" stroke-opacity="0.05" stroke-width="6"/>
  <!-- CPU cooler -->
  <rect x="400" y="110" width="64" height="92" rx="6" fill="#1a212b" stroke="#2b323d"/>
  {cooler_fan}
  <!-- RGB RAM -->
  {ram}
  <!-- GPU -->
  <rect x="322" y="248" width="220" height="46" rx="6" fill="url(#gpuGrad)" stroke="#2b323d"/>
  <rect x="322" y="248" width="220" height="5" rx="2" fill="url(#rgbGrad)" class="rgb"/>
  {gpu_fans}
  <text x="480" y="282" fill="#8b949e" font-size="11" font-family="Segoe UI, Ubuntu, Sans-Serif">RTX</text>
  <!-- cables -->
  <path d="M320 330 C 380 350 460 340 540 356" stroke="#ffffff" stroke-opacity="0.1" stroke-width="4" fill="none"/>
  <!-- glass reflection -->
  <polygon points="340,70 400,70 330,370 300,370" fill="#ffffff" opacity="0.045"/>
</g>
<rect x="300" y="70" width="264" height="300" rx="8" fill="none" stroke="url(#rgbGrad)" stroke-width="2.5" class="rgb"/>
</svg>
"""
    import os
    os.makedirs("assets", exist_ok=True)
    with open("assets/rgb-pc.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote assets/rgb-pc.svg ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
