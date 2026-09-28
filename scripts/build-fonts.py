#!/usr/bin/env python3
"""Rebuilds fonts/*.woff2 from the Google Fonts sources. Only needed if the
faces change; the generators read the committed files.

Bodoni Moda and Instrument Sans are variable fonts. They are frozen to the
one instance the art uses (Bodoni at display optical size, as the site renders
its headings) and their overlapping contours are merged, which is what keeps
the hairlines intact under Firefox's text renderer. Plex Mono ships static.

Run: python3 scripts/build-fonts.py   (needs fonttools, brotli, skia-pathops)
"""
import io
import pathlib
import urllib.request

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import OverlapMode, instantiateVariableFont

OUT = pathlib.Path(__file__).resolve().parent.parent / "fonts"
BASE = "https://github.com/google/fonts/raw/main/ofl/"
FONTS = [
    ("bodonimoda/BodoniModa%5Bopsz,wght%5D.ttf", {"wght": 400, "opsz": 80}, "BodoniModa-Display.woff2"),
    ("bodonimoda/BodoniModa-Italic%5Bopsz,wght%5D.ttf", {"wght": 400, "opsz": 80}, "BodoniModa-DisplayItalic.woff2"),
    ("instrumentsans/InstrumentSans%5Bwdth,wght%5D.ttf", {"wght": 400, "wdth": 100}, "InstrumentSans-Regular.woff2"),
    ("ibmplexmono/IBMPlexMono-Regular.ttf", None, "IBMPlexMono-Regular.woff2"),
    ("ibmplexmono/IBMPlexMono-Medium.ttf", None, "IBMPlexMono-Medium.woff2"),
    ("ibmplexmono/IBMPlexMono-SemiBold.ttf", None, "IBMPlexMono-SemiBold.woff2"),
]


def main():
    for src, location, dst in FONTS:
        with urllib.request.urlopen(BASE + src) as r:
            font = TTFont(io.BytesIO(r.read()))
        if location:
            font = instantiateVariableFont(font, location, updateFontNames=False, overlap=OverlapMode.REMOVE)
        font.flavor = "woff2"
        font.save(OUT / dst)
        print(f"fonts/{dst}: {(OUT / dst).stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
