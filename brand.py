"""Reads the vendored brand layer (brand/, guarded by scripts/check-brand.mjs). Shared by every generator here.

This is a Silicon Wat surface, so it vendors the neutrals (tokens.css) and NOT the B-Emblem: the emblem stands for the
B in HeartBank and does not belong on a Silicon Wat page. The icon here is a placeholder until Silicon Wat's own mark
is settled (ICON below), marked [ PLACEHOLDER ICON ] wherever it is shown large.
"""
import io, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
_TOK = io.open(os.path.join(HERE, "brand", "tokens.css"), encoding="utf-8").read()

# ── this surface's own, in ONE place: every generator imports these, none types its own ─────────────────────────────
# Silicon Wat's orange robe (the body palette has no pinned hex yet, A383). #c2410c is the orange siliconwat.dev's own
# links already use (Tailwind orange-700); #fdba74 is its dark-mode twin (orange-300). Provisional.
ACCENT, ACCENT_DARK = "#c2410c", "#fdba74"
# The drawn scan: paper and print ink. An illustration of a printed page, not a neutral, so it does not invert in dark.
PAPER, PRINT = "#f3ecdc", "#2a2420"

# The placeholder icon: a page with three printed lines, drawn in a 24-unit box. NOT a mark; Silicon Wat's own is unsettled.
ICON_GLYPH = ('<rect x="5" y="3" width="14" height="18" rx="2.2" fill="none" stroke="{c}" stroke-width="1.8"/>'
              '<path d="M8.5 8h7M8.5 12h7M8.5 16h4.5" stroke="{c}" stroke-width="1.8" stroke-linecap="round"/>')


def icon_svg(color, size=22, cls="ico"):
    return ('<svg class="%s" width="%d" height="%d" viewBox="0 0 24 24" aria-label="[ PLACEHOLDER ICON ]">%s</svg>'
            % (cls, size, size, ICON_GLYPH.format(c=color)))


def tok(name):
    m = re.search(r"^\s*--%s:\s*([^;]+);" % re.escape(name), _TOK, re.M)
    if not m:
        raise SystemExit("brand: brand/tokens.css has no --%s; sync the brand layer" % name)
    return re.sub(r"\s+", "", m.group(1))


def fill(text, keys=("bg", "surface", "surface-2", "line", "line-strong", "ink", "ink-dim", "ink-faint", "scrim")):
    """Replace @L_BG@-style placeholders with the vendored neutrals, then refuse any left unfilled."""
    for k in keys:
        for p in ("l", "d"):
            text = text.replace("@%s_%s@" % (p.upper(), k.upper().replace("-", "_")), tok("%s-%s" % (p, k)))
    text = text.replace("@ACCENT@", ACCENT).replace("@ACCENT_DARK@", ACCENT_DARK).replace("@PAPER@", PAPER).replace("@PRINT@", PRINT)
    left = re.findall(r"@[A-Z_0-9]+@", text)
    assert not left, "unfilled brand placeholder(s): %s" % sorted(set(left))
    return text
