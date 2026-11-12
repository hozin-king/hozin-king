#!/usr/bin/env python3
"""Restyle the lowlighter/metrics reactions row as iOS frosted glass.

github-metrics.svg embeds the reactions as HTML (foreignObject): 8
`.category.column` divs, each with a 50x50 gauge SVG (circle.gauge-base
+ emoji text). This injects CSS into the template's own <style> block
plus a glossy highlight ellipse into every gauge, so the row becomes
frosted-glass orbs that float, glow and shimmer — fully animated.

Idempotent: if the /* glass-reactions */ marker is already present, the
file is left untouched. Run from repo root after metrics generation:
    python3 scripts/glass_reactions.py github-metrics.svg
"""
import re
import sys

MARKER = "/* glass-reactions */"

CSS = """
/* glass-reactions */
/* iOS frosted-glass reaction orbs, fully animated */
.categories .category{position:relative}
.categories .category svg.gauge{width:54px;height:54px;border-radius:50%;
  background:linear-gradient(135deg,rgba(255,255,255,.24),rgba(255,255,255,.05) 45%,rgba(255,255,255,.16));
  border:1px solid rgba(255,255,255,.38);
  box-shadow:0 10px 28px rgba(0,0,0,.45),inset 0 2px 0 rgba(255,255,255,.55),inset 0 -10px 18px rgba(255,255,255,.08),inset 2px 0 6px rgba(255,255,255,.14);
  backdrop-filter:blur(14px) saturate(1.8);-webkit-backdrop-filter:blur(14px) saturate(1.8);
  animation:glass-float 3.2s ease-in-out infinite,glass-glow 3.2s ease-in-out infinite}
.categories .category:nth-child(1) svg.gauge{animation-delay:0s}
.categories .category:nth-child(2) svg.gauge{animation-delay:.25s}
.categories .category:nth-child(3) svg.gauge{animation-delay:.5s}
.categories .category:nth-child(4) svg.gauge{animation-delay:.75s}
.categories .category:nth-child(5) svg.gauge{animation-delay:1s}
.categories .category:nth-child(6) svg.gauge{animation-delay:1.25s}
.categories .category:nth-child(7) svg.gauge{animation-delay:1.5s}
.categories .category:nth-child(8) svg.gauge{animation-delay:1.75s}
.categories .gauge-base{fill:rgba(255,255,255,.07);stroke:rgba(255,255,255,.55);stroke-width:6}
.categories .gauge text{filter:drop-shadow(0 2px 4px rgba(0,0,0,.55))}
@keyframes glass-float{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}
@keyframes glass-glow{0%,100%{box-shadow:0 10px 28px rgba(0,0,0,.45),0 0 0 rgba(0,240,255,0),inset 0 2px 0 rgba(255,255,255,.55),inset 0 -10px 18px rgba(255,255,255,.08)}50%{box-shadow:0 14px 34px rgba(0,0,0,.5),0 0 24px rgba(0,240,255,.5),inset 0 2px 0 rgba(255,255,255,.55),inset 0 -10px 18px rgba(255,255,255,.08)}}
"""

# Glossy highlight spot inside each gauge orb, gently shimmering (SMIL).
HIGHLIGHT = (
    '<ellipse cx="42" cy="38" rx="26" ry="13" fill="#ffffff" opacity="0.28" '
    'transform="rotate(-25 42 38)">'
    '<animate attributeName="opacity" values="0.28;0.10;0.28" dur="3.2s" '
    'repeatCount="indefinite"/></ellipse>'
)


def main():
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        svg = f.read()
    if MARKER in svg:
        print("already glass — nothing to do")
        return
    # 1. Inject CSS into the style block that holds the .categories rules.
    m = None
    for cand in re.finditer(r"<style[^>]*>(.*?)</style>", svg, re.S):
        if ".categories{" in cand.group(1):
            m = cand
            break
    if not m:
        raise SystemExit("no style block with .categories found")
    css = m.group(1)
    svg = svg[: m.start(1)] + css.rstrip() + "\n" + CSS + svg[m.end(1):]
    # 2. Gloss highlight inside every reaction gauge orb.
    n = 0

    def add_highlight(match):
        nonlocal n
        n += 1
        return match.group(0) + HIGHLIGHT

    svg = re.sub(
        r'(<svg[^>]*class="gauge info"[^>]*>\s*<circle class="gauge-base"[^/]*/>)',
        add_highlight,
        svg,
    )
    print(f"glassified {path}: {n} reaction orbs, css injected")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)


if __name__ == "__main__":
    main()
