#!/usr/bin/env python3
"""Restyle the lowlighter/metrics reactions row as iOS frosted glass.

github-metrics.svg embeds the reactions as HTML (foreignObject): 8
`.category.column` divs, each with a 50x50 gauge SVG (circle.gauge-base
+ emoji text). This injects CSS into the template's own <style> block,
a colorful aura behind every orb, and a glossy highlight inside it.

v2 (12 Nov 2026): v1 looked foggy + laggy — the heavy white fill over a
uniform dark card reads as milk, and animating box-shadow every frame
is the classic jank source. v2 fixes both: much lighter white, a
colorful radial aura behind each orb so the frost has color to refract
(real iOS glass needs something colorful behind it), blur 14px -> 8px,
and transform/opacity-only animation (no box-shadow animation).

Idempotent: v2 marker present -> no-op. Re-running over a v1 file
strips all v1 artifacts first, then injects v2 fresh.

Run from repo root after metrics generation:
    python3 scripts/glass_reactions.py github-metrics.svg
"""
import re
import sys

MARKER = "/* glass-reactions v2 */"

CSS = """
/* glass-reactions v2 */
/* iOS frosted-glass reaction orbs — transform/opacity animation only */
.categories .category{position:relative}
.categories .category .glass-aura{position:absolute;left:50%;top:50%;width:74px;height:74px;margin:-37px 0 0 -37px;border-radius:50%;z-index:0;pointer-events:none;filter:blur(7px);opacity:.5;animation:glass-aura 4s ease-in-out infinite;
  background:radial-gradient(circle at 35% 30%,rgba(0,240,255,.7),rgba(255,0,229,.42) 55%,rgba(0,0,0,0) 72%)}
.categories .category:nth-child(2) .glass-aura{background:radial-gradient(circle at 35% 30%,rgba(255,0,229,.65),rgba(0,120,255,.5) 55%,rgba(0,0,0,0) 72%)}
.categories .category:nth-child(3) .glass-aura{background:radial-gradient(circle at 35% 30%,rgba(0,120,255,.65),rgba(0,230,118,.45) 55%,rgba(0,0,0,0) 72%)}
.categories .category:nth-child(4) .glass-aura{background:radial-gradient(circle at 35% 30%,rgba(0,230,118,.65),rgba(255,234,0,.5) 55%,rgba(0,0,0,0) 72%)}
.categories .category:nth-child(5) .glass-aura{background:radial-gradient(circle at 35% 30%,rgba(255,234,0,.65),rgba(255,145,0,.5) 55%,rgba(0,0,0,0) 72%)}
.categories .category:nth-child(6) .glass-aura{background:radial-gradient(circle at 35% 30%,rgba(255,145,0,.65),rgba(255,61,0,.5) 55%,rgba(0,0,0,0) 72%)}
.categories .category:nth-child(7) .glass-aura{background:radial-gradient(circle at 35% 30%,rgba(255,61,0,.65),rgba(168,85,247,.5) 55%,rgba(0,0,0,0) 72%)}
.categories .category:nth-child(8) .glass-aura{background:radial-gradient(circle at 35% 30%,rgba(168,85,247,.65),rgba(0,240,255,.5) 55%,rgba(0,0,0,0) 72%)}
.categories .category:nth-child(1) .glass-aura{animation-delay:0s}
.categories .category:nth-child(2) .glass-aura{animation-delay:.5s}
.categories .category:nth-child(3) .glass-aura{animation-delay:1s}
.categories .category:nth-child(4) .glass-aura{animation-delay:1.5s}
.categories .category:nth-child(5) .glass-aura{animation-delay:2s}
.categories .category:nth-child(6) .glass-aura{animation-delay:2.5s}
.categories .category:nth-child(7) .glass-aura{animation-delay:3s}
.categories .category:nth-child(8) .glass-aura{animation-delay:3.5s}
.categories .category svg.gauge{position:relative;z-index:1;width:54px;height:54px;border-radius:50%;
  background:linear-gradient(160deg,rgba(255,255,255,.15),rgba(255,255,255,.02) 55%,rgba(255,255,255,.08));
  border:1px solid rgba(255,255,255,.5);
  box-shadow:0 8px 24px rgba(0,0,0,.42),inset 0 1px 0 rgba(255,255,255,.7),inset 0 -8px 14px rgba(255,255,255,.05),inset 1px 0 4px rgba(255,255,255,.12);
  backdrop-filter:blur(8px) saturate(1.7);-webkit-backdrop-filter:blur(8px) saturate(1.7);
  will-change:transform;animation:glass-float 3.4s ease-in-out infinite}
.categories .category:nth-child(1) svg.gauge{animation-delay:0s}
.categories .category:nth-child(2) svg.gauge{animation-delay:.3s}
.categories .category:nth-child(3) svg.gauge{animation-delay:.6s}
.categories .category:nth-child(4) svg.gauge{animation-delay:.9s}
.categories .category:nth-child(5) svg.gauge{animation-delay:1.2s}
.categories .category:nth-child(6) svg.gauge{animation-delay:1.5s}
.categories .category:nth-child(7) svg.gauge{animation-delay:1.8s}
.categories .category:nth-child(8) svg.gauge{animation-delay:2.1s}
.categories .gauge-base{fill:rgba(255,255,255,.04);stroke:rgba(255,255,255,.55);stroke-width:5}
.categories .gauge text{filter:drop-shadow(0 1px 2px rgba(0,0,0,.45))}
@keyframes glass-float{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
@keyframes glass-aura{0%,100%{opacity:.45}50%{opacity:.75}}
/* /glass-reactions */
"""

# Glossy highlight spot inside each gauge orb, gently shimmering (SMIL).
HIGHLIGHT = (
    '<ellipse cx="42" cy="38" rx="26" ry="13" fill="#ffffff" opacity="0.18" '
    'transform="rotate(-25 42 38)">'
    '<animate attributeName="opacity" values="0.18;0.08;0.18" dur="3.4s" '
    'repeatCount="indefinite"/></ellipse>'
)

AURA = '<span class="glass-aura"></span>'


def strip_old(svg):
    """Remove every previously injected glass artifact (v1 and v2)."""
    # v2 CSS block (start marker .. end marker)
    svg = re.sub(
        r"/\* glass-reactions v2 \*/.*?/\* /glass-reactions \*/\n?",
        "",
        svg,
        flags=re.S,
    )
    # v1 CSS block: start marker .. end of its <style> content
    svg = re.sub(r"/\* glass-reactions \*/.*?(?=</style>)", "", svg, flags=re.S)
    # highlight ellipses + aura spans
    svg = re.sub(
        r'<ellipse cx="42" cy="38"[^>]*>.*?</ellipse>', "", svg, flags=re.S
    )
    svg = re.sub(r'<span class="glass-aura"></span>', "", svg)
    return svg


def main():
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        svg = f.read()
    if MARKER in svg:
        print("already glass v2 — nothing to do")
        return
    svg = strip_old(svg)
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
    # 2. Colorful aura behind every reaction orb.
    n_aura = len(re.findall(r'<div class="category column">', svg))
    svg = svg.replace('<div class="category column">', '<div class="category column">' + AURA)
    # 3. Gloss highlight inside every reaction gauge orb.
    n_hi = 0

    def add_highlight(match):
        nonlocal n_hi
        n_hi += 1
        return match.group(0) + HIGHLIGHT

    svg = re.sub(
        r'(<svg[^>]*class="gauge info"[^>]*>\s*<circle class="gauge-base"[^/]*/>)',
        add_highlight,
        svg,
    )
    print(f"glassified v2 {path}: {n_aura} auras, {n_hi} orbs, css injected")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)


if __name__ == "__main__":
    main()
