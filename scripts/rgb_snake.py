#!/usr/bin/env python3
"""RGB-ify a Platane/snk snake SVG (post-process step in snake.yml).

The snk output draws the snake head in one flat color (--cs) and the
eaten cells in a green scale (--c1..--c4). This turns it into an RGB
snake: eaten cells become a rainbow heat scale, the head gets a flowing
rainbow gradient + neon glow. Everything else (path, keyframes, timing)
is left untouched, so the animation keeps working exactly as snk made it.

Usage: python3 scripts/rgb_snake.py <path-to-snake.svg>
"""
import re
import sys

# Rainbow heat scale for eaten cells (low -> high contribution).
HEAT = {"--c1": "#2979ff", "--c2": "#00e676", "--c3": "#ffea00", "--c4": "#ff3d00"}

# Rainbow stops for the head gradient (animated, flows over time).
RAINBOW = ["#ff004c", "#ff8a00", "#ffee00", "#00e676", "#00cfff", "#7b2fff"]
DUR = "8s"


def build_defs():
    stops = []
    n = len(RAINBOW)
    for i, color in enumerate(RAINBOW):
        # Each stop cycles through the rainbow, staggered so the gradient flows.
        values = ";".join(RAINBOW[i:] + RAINBOW[:i] + [RAINBOW[i]])
        stops.append(
            f'<stop offset="{i * 100 // (n - 1)}%" stop-color="{color}">'
            f'<animate attributeName="stop-color" values="{values}" '
            f'dur="{DUR}" repeatCount="indefinite"/></stop>'
        )
    return (
        "<defs><linearGradient id=\"rgbGrad\" x1=\"0%\" y1=\"0%\" "
        "x2=\"100%\" y2=\"100%\">" + "".join(stops) + "</linearGradient></defs>"
    )


def rgbify(svg: str) -> str:
    # 1. Rainbow heat scale for the eaten cells / trail bars.
    for var, color in HEAT.items():
        svg = re.sub(rf"{re.escape(var)}:#[0-9a-fA-F]+", f"{var}:{color}", svg, count=1)
    # 2. Flowing rainbow gradient defs, right after the opening <svg> tag.
    m = re.search(r"<svg[^>]*>", svg)
    if not m:
        raise ValueError("no <svg> tag found")
    svg = svg[: m.end()] + build_defs() + svg[m.end():]
    # 3. Head: rainbow gradient fill + neon glow instead of the flat --cs.
    svg = re.sub(
        r"(\.s\{[^}]*?)fill:var\(--cs\)",
        r"\1fill:url(#rgbGrad);filter:drop-shadow(0 0 5px #00F0FF)",
        svg,
        count=1,
    )
    return svg


def main():
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        svg = f.read()
    out = rgbify(svg)
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"rgbified {path} ({len(out)} bytes)")


if __name__ == "__main__":
    main()
