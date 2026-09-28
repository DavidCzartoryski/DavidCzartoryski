"""Palette, fonts and drawing helpers shared by every generated SVG.

The palette and the three families are the portfolio's own
(davidczartoryski.com, src/app/globals.css): ink-navy night, cream passport
paper, gold foil, stamp inks. Bodoni Moda for display, Instrument Sans for
body copy, IBM Plex Mono for anything that would be printed on a ticket.

GitHub serves README images through its camo proxy as a plain <img>, and an
SVG loaded that way cannot fetch web fonts. So every SVG carries its own:
the glyphs it actually uses, subset out of fonts/*.woff2 and inlined as
base64. That is what keeps the wordmark in Bodoni on a machine that has
never installed it. Glyphs are collected as text is written, so a file only
ever pays for the letters on it.
"""
import base64
import html
import io
import pathlib
import random
from collections import defaultdict

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"

INK, INK2, INK3 = "#0b1020", "#111a33", "#182347"
PAPER, PAPER2, PAPER3 = "#f3ead8", "#e6dcc4", "#d6c8a8"
GOLD, GOLD2, EMBER = "#d4a853", "#f0cf85", "#c8502c"
RED, BLUE, GREEN, VIOLET = "#d63a2f", "#3b5bb5", "#2f7a4f", "#6b4fb0"
# gold dark enough to read on GitHub's white theme
GOLD_INK = "#9a7328"

FACES = {
    "serif": ("Bodoni Moda", 400, "normal", "BodoniModa-Display.woff2"),
    "serif-i": ("Bodoni Moda", 400, "italic", "BodoniModa-DisplayItalic.woff2"),
    "sans": ("Instrument Sans", 400, "normal", "InstrumentSans-Regular.woff2"),
    "mono": ("IBM Plex Mono", 400, "normal", "IBMPlexMono-Regular.woff2"),
    "mono-md": ("IBM Plex Mono", 500, "normal", "IBMPlexMono-Medium.woff2"),
    "mono-sb": ("IBM Plex Mono", 600, "normal", "IBMPlexMono-SemiBold.woff2"),
}
FALLBACK = {
    "Bodoni Moda": "'Bodoni Moda',Didot,'Bodoni MT',Georgia,serif",
    "Instrument Sans": "'Instrument Sans','Helvetica Neue',Arial,sans-serif",
    "IBM Plex Mono": "'IBM Plex Mono','SF Mono',Menlo,Consolas,monospace",
}

# Top-down airliner, nose pointing right, in a 100x100 box (src/components/Plane.tsx)
PLANE = (
    "M96 50c0-3.2-4.4-5.4-11-6l-27.6-2L33.2 11.4c-1.1-1.4-2.8-2.2-4.6-2.2H25c-1.4 0-2.4 1.4-1.9 2.7"
    "l10.4 30H16.9l-6.4-8.6c-.8-1.1-2.1-1.7-3.5-1.7H4.6c-1.3 0-2.2 1.3-1.8 2.5L7.6 50l-4.8 15.9"
    "c-.4 1.2.5 2.5 1.8 2.5H7c1.4 0 2.7-.6 3.5-1.7l6.4-8.6h16.6l-10.4 30c-.5 1.3.5 2.7 1.9 2.7h3.6"
    "c1.8 0 3.5-.8 4.6-2.2L57.4 58l27.6-2c6.6-.6 11-2.8 11-6z"
)

GLYPHS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

_fonts = {}


def _font(face):
    if face not in _fonts:
        _fonts[face] = TTFont(FONTS / FACES[face][3])
    return _fonts[face]


def measure(face, s, size, ls=0.0):
    """Advance width of s in px. Ignores kerning, which is close enough to lay out by."""
    f = _font(face)
    cmap, hmtx = f.getBestCmap(), f["hmtx"]
    units = sum(hmtx[cmap.get(ord(c), ".notdef")][0] for c in s)
    return units * size / f["head"].unitsPerEm + ls * len(s)


def fit(face, s, size, max_w, ls=0.0):
    """Largest size <= size at which s fits in max_w."""
    w = measure(face, s, size, ls)
    return size if w <= max_w else round(size * max_w / w, 1)


def _subset_b64(face, chars):
    font = TTFont(FONTS / FACES[face][3])
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.hinting = False
    opts.desubroutinize = True
    opts.drop_tables += ["meta"]
    sub = subset.Subsetter(opts)
    sub.populate(text=chars + " ")
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def n(v):
    """Trim floats for attribute output."""
    return f"{v:.2f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v)


def esc(s):
    return html.escape(s, quote=True)


class Svg:
    def __init__(self, w, h, label, view=None):
        self.w, self.h, self.label = w, h, label
        self.view = view or f"0 0 {w} {h}"
        self.css, self.defs, self.body = [], [], []
        self.glyphs = defaultdict(set)

    def add(self, *parts):
        self.body.extend(parts)

    def text(self, x, y, spans, size, ls=0, anchor=None, attrs="", cls=None):
        """spans: (face, text, fill[, opacity]) or a list of them, rendered as tspans."""
        if isinstance(spans, tuple):
            spans = [spans]
        inner = []
        for sp in spans:
            face, s, fill = sp[:3]
            self.glyphs[face].update(s)
            a = f' fill="{fill}"'
            if len(sp) > 3 and sp[3] is not None:
                a += f' fill-opacity="{sp[3]}"'
            inner.append((face, esc(s), a))
        common = f'x="{n(x)}" y="{n(y)}" font-size="{n(size)}"'
        if ls:
            common += f' letter-spacing="{n(ls)}"'
        if anchor:
            common += f' text-anchor="{anchor}"'
        common += attrs
        extra = f" {cls}" if cls else ""
        if len(inner) == 1:
            face, s, a = inner[0]
            return f'<text class="t-{face}{extra}" {common}{a}>{s}</text>'
        tspans = "".join(f'<tspan class="t-{face}"{a}>{s}</tspan>' for face, s, a in inner)
        open_cls = f' class="{cls}"' if cls else ""
        return f"<text{open_cls} {common}>{tspans}</text>"

    def _font_css(self):
        out = []
        for face in sorted(self.glyphs):
            family, weight, style, _ = FACES[face]
            data = _subset_b64(face, "".join(sorted(self.glyphs[face])))
            out.append(
                f"@font-face{{font-family:'{family}';font-weight:{weight};font-style:{style};"
                f"src:url(data:font/woff2;base64,{data}) format('woff2')}}"
            )
            out.append(f".t-{face}{{font-family:{FALLBACK[family]};font-weight:{weight};font-style:{style}}}")
        return out

    def render(self):
        style = "\n".join(self._font_css() + self.css)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="{self.view}" role="img" aria-label="{esc(self.label)}">\n'
            f"<defs>\n<style><![CDATA[\n{style}\n]]></style>\n" + "\n".join(self.defs) + "\n</defs>\n"
            + "\n".join(self.body) + "\n</svg>\n"
        )

    def save(self, rel):
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        svg = self.render()
        path.write_text(svg)
        print(f"{rel}: {len(svg) / 1024:.1f} KB")


# ------------------------------------------------------------------ helpers
def plane(x, y, size, fill, rotate=0, opacity=None):
    op = f' fill-opacity="{opacity}"' if opacity is not None else ""
    return (
        f'<path transform="translate({n(x)} {n(y)}) rotate({rotate}) translate({n(-size / 2)} {n(-size / 2)}) '
        f'scale({n(size / 100)})" fill="{fill}"{op} d="{PLANE}"/>'
    )


def barcode(seed, x, y, w, h, fill, opacity=0.78):
    rng = random.Random(seed)
    bars, cx = [], 0.0
    while cx < w:
        bw = rng.choice([1, 1, 1.5, 2, 2.5, 3])
        if cx + bw > w:
            break
        bars.append(f'<rect x="{n(x + cx)}" y="{y}" width="{bw}" height="{h}"/>')
        cx += bw + rng.choice([1, 1.5, 2, 2.5])
    return f'<g fill="{fill}" opacity="{opacity}">' + "".join(bars) + "</g>"


def paper_filter(fid, seed=3):
    """Grain and faint foxing for passport paper. Apply to a rect filled with PAPER."""
    return (
        f'<filter id="{fid}" x="0" y="0" width="100%" height="100%">'
        f'<feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="{seed}" result="fine"/>'
        '<feColorMatrix in="fine" type="matrix" values="0 0 0 0 0.36  0 0 0 0 0.28  0 0 0 0 0.16  0 0 0 0.2 0" result="fineC"/>'
        f'<feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="3" seed="{seed + 5}" result="blot"/>'
        '<feColorMatrix in="blot" type="matrix" values="0 0 0 0 0.55  0 0 0 0 0.42  0 0 0 0 0.22  0 0 0 0.32 -0.1" result="blotC"/>'
        '<feMerge result="tex"><feMergeNode in="blotC"/><feMergeNode in="fineC"/></feMerge>'
        '<feComposite in="tex" in2="SourceGraphic" operator="in" result="texIn"/>'
        '<feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="texIn"/></feMerge>'
        "</filter>"
    )


def foil(mid, x0, x1, height, dur=9, begin=0):
    """Mask for the gold-foil glint: a soft band that sweeps x0 -> x1 once per cycle, then rests.

    Draw the text once in solid gold, then again in the shine colour with
    mask="url(#mid)". Filling the text itself with a gradient would be simpler,
    but Firefox rasterises gradient-filled text without stem darkening and
    Bodoni's hairlines vanish; a mask over solid text keeps them.
    """
    band = max(60.0, (x1 - x0) * 0.3)
    return (
        f'<linearGradient id="{mid}-g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000"/>'
        f'<stop offset="0.5" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>'
        f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="100000" height="{n(height)}">'
        f'<rect x="{n(-band)}" y="0" width="{n(band)}" height="{n(height)}" fill="url(#{mid}-g)">'
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="{n(x0)} 0;{n(x1 + band)} 0;{n(x1 + band)} 0" keyTimes="0;0.3;1" dur="{dur}s" begin="{begin}s" '
        f'repeatCount="indefinite"/></rect></mask>'
    )


# ------------------------------------------------------------ split flap
def flap_css(reel_len, h, cycle, segments, flip=0.36, name="flap"):
    """Keyframes that step a glyph reel along, one flip per segment.

    A tile's reel is [last, r, r, r, d0, r, r, r, d1, ...], so each segment
    steps four cells (three blurs and the landing glyph) and then holds. The
    reel ends on the same glyph it starts on, which makes the loop seamless.
    """
    steps = (reel_len - 1) // segments
    frames = []
    for k in range(segments):
        t0 = k * cycle / segments
        p0 = 100 * t0 / cycle
        p1 = 100 * (t0 + flip) / cycle
        frames.append(f"{p0:.3f}%{{transform:translateY({-k * steps * h}px);animation-timing-function:steps({steps},end)}}")
        frames.append(f"{p1:.3f}%{{transform:translateY({-(k + 1) * steps * h}px)}}")
    frames.append(f"100%{{transform:translateY({-segments * steps * h}px)}}")
    return f"@keyframes {name}{{{''.join(frames)}}}"


def flap_tiles(svg, x, y, word_seq, w, h, size, rng, tile_fill, glyph_fill, gap=3,
               cls="reel", delay_step=0.12, delay=0.0, hinge="#000", clip="tile-clip", pool=GLYPHS):
    """A row of split-flap tiles. word_seq is the sequence of words to land on."""
    parts = []
    for i in range(len(word_seq[0])):
        reel = [word_seq[-1][i]]
        for word in word_seq:
            reel += [rng.choice(pool) for _ in range(3)] + [word[i]]
        tx = x + i * (w + gap)
        glyphs = "".join(
            svg.text(w / 2, h * 0.5 + size * 0.36 + j * h, ("mono-sb", ch, glyph_fill), size, anchor="middle")
            for j, ch in enumerate(reel) if ch != " "
        )
        parts.append(
            f'<g transform="translate({n(tx)} {n(y)})">'
            f'<rect width="{w}" height="{h}" rx="{n(h * 0.1)}" fill="{tile_fill}"/>'
            f'<g clip-path="url(#{clip})"><g class="{cls}" style="animation-delay:{n(delay + i * delay_step)}s">{glyphs}</g></g>'
            f'<rect y="{n(h / 2 - 0.6)}" width="{w}" height="1.2" fill="{hinge}" opacity="0.55"/>'
            f'<rect y="{n(h / 2 + 0.6)}" width="{w}" height="0.6" fill="#fff" opacity="0.06"/>'
            "</g>"
        )
    return "".join(parts)
