#!/usr/bin/env python3
"""Writes the static art for the profile README: the hero, the section
headers, the route dividers, the portfolio button and the map.

Everything is drawn in the portfolio's own language (davidczartoryski.com):
a night sky over the cloud deck, a boarding pass whose destination flips
like a departures board, Bodoni with the surname in gold foil. The dividers
are one round trip through the home bases, BOS to SFO to WAW and back.

Headers and dividers come in two inks, because they sit on the page itself:
cream on night for GitHub's dark theme, ink on paper for the light one. The
README picks between them with <picture>. The hero, map and board carry
their own night sky and read the same on both.

Run: python3 scripts/generate-art.py   (needs fonttools + brotli)
"""
import json
import random

from typeset import (
    BLUE, EMBER, GOLD, GOLD2, GOLD_INK, GREEN, INK, INK2, INK3, PAPER, RED, ROOT, VIOLET,
    Svg, barcode, fit, flap_css, flap_tiles, foil, measure, n, paper_filter, plane,
)

# the destinations the boarding pass cycles through (src/components/sections/Hero.tsx)
DESTINATIONS = [
    ("WAW", "WARSAW"), ("MXP", "MILAN"), ("SFO", "SAN FRANCISCO"), ("IST", "ISTANBUL"),
    ("DXB", "DUBAI"), ("TIA", "TIRANA"), ("ATH", "ATHENS"),
]
SEGMENT = 3.2  # seconds each destination stays up, same as the site


# ------------------------------------------------------------------ hero
def hero():
    W, H = 1000, 492
    rng = random.Random(2027)
    svg = Svg(W, H, "David Czartoryski. Software engineer and founder. Northeastern, Class of 2027. "
                    "Boston, San Francisco, Warsaw.")
    cycle = SEGMENT * len(DESTINATIONS)
    TW, TH, TS = 29, 40, 26  # flap tile width, height, glyph size
    svg.css += [
        f".reel{{animation:flap {cycle}s linear infinite}}",
        flap_css(1 + 4 * len(DESTINATIONS), TH, cycle, len(DESTINATIONS)),
        f".city{{opacity:0;animation:city {cycle}s steps(1,end) infinite}}",
        f"@keyframes city{{0%{{opacity:1}}{100 / len(DESTINATIONS):.3f}%,100%{{opacity:0}}}}",
        ".tw{animation:tw 5s ease-in-out infinite}",
        "@keyframes tw{0%,100%{opacity:1}50%{opacity:.25}}",
        ".strobe{animation:strobe 1.3s steps(1,end) infinite}",
        "@keyframes strobe{0%,8%{opacity:1}9%,100%{opacity:0}}",
    ]

    # sky
    svg.defs += [
        f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>',
        f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#060a16"/>'
        f'<stop offset="0.5" stop-color="{INK}"/><stop offset="0.82" stop-color="{INK2}"/>'
        f'<stop offset="1" stop-color="#1b2342"/></linearGradient>',
        f'<radialGradient id="dawn" cx="0.8" cy="1.08" r="0.7"><stop offset="0" stop-color="{EMBER}" stop-opacity="0.55"/>'
        f'<stop offset="0.3" stop-color="#7a3526" stop-opacity="0.22"/><stop offset="1" stop-color="{EMBER}" stop-opacity="0"/></radialGradient>',
        f'<radialGradient id="dawn2" cx="0.8" cy="1.02" r="0.34"><stop offset="0" stop-color="{GOLD2}" stop-opacity="0.32"/>'
        f'<stop offset="1" stop-color="{GOLD2}" stop-opacity="0"/></radialGradient>',
        '<filter id="cloud" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="16"/></filter>',
        '<filter id="halo" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="2.2"/></filter>',
        '<filter id="shadow" x="-20%" y="-20%" width="140%" height="160%"><feGaussianBlur stdDeviation="18"/></filter>',
        '<linearGradient id="trail" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0.5"/></linearGradient>',
        paper_filter("paper", seed=7),
        f'<clipPath id="tile-clip"><rect width="{TW}" height="{TH}" rx="4"/></clipPath>',
    ]
    body = ['<g clip-path="url(#frame)">',
            f'<rect width="{W}" height="{H}" fill="url(#sky)"/>',
            f'<rect width="{W}" height="{H}" fill="url(#dawn)"/>',
            f'<rect width="{W}" height="{H}" fill="url(#dawn2)"/>']

    # stars, thinning toward the horizon
    stars = []
    for i in range(130):
        x, y = rng.uniform(0, W), rng.uniform(0, H) ** 1.35 / H ** 0.35
        r = rng.choice([0.4, 0.5, 0.6, 0.7, 0.9, 1.1])
        op = round(max(0.12, 0.85 - y / H) * rng.uniform(0.5, 1), 2)
        tw = f' class="tw" style="animation-delay:-{rng.uniform(0, 5):.1f}s;animation-duration:{rng.uniform(3, 7):.1f}s"' if i % 5 == 0 else ""
        stars.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" opacity="{op}"{tw}/>')
    body.append(f'<g fill="{PAPER}">' + "".join(stars) + "</g>")
    for x, y in [(528, 30), (978, 64), (470, 262)]:
        body.append(f'<g fill="#fff"><circle cx="{x}" cy="{y}" r="3" opacity="0.35" filter="url(#halo)"/>'
                    f'<circle cx="{x}" cy="{y}" r="1.2" class="tw" style="animation-duration:4.4s"/></g>')

    # cloud deck catching the dawn
    clouds = []
    for i in range(16):
        cx = -60 + i * 72 + rng.uniform(-20, 20)
        clouds.append(f'<ellipse cx="{cx:.0f}" cy="{H + 10 + rng.uniform(-14, 18):.0f}" rx="{rng.uniform(70, 130):.0f}" '
                      f'ry="{rng.uniform(26, 44):.0f}"/>')
    body.append(f'<g fill="#0a0f1f" opacity="0.75" filter="url(#cloud)">' + "".join(clouds) + "</g>")

    # a flight crossing the top of the sky
    route = "M-80 44 Q500 -30 1080 30"
    body.append(f'<path d="{route}" fill="none" stroke="{PAPER}" stroke-opacity="0.13" stroke-width="1" stroke-dasharray="2 7"/>')
    body.append(
        '<g><animateMotion dur="19s" repeatCount="indefinite" rotate="auto" path="' + route + '"/>'
        '<rect x="-170" y="-0.9" width="160" height="1.8" rx="0.9" fill="url(#trail)"/>'
        + plane(0, 0, 21, PAPER)
        + f'<circle cx="-8" cy="0" r="1.3" fill="{RED}" class="strobe"/></g>'
    )

    # left column: passport line, name, copy
    x0 = 56
    ks = 11
    kls = ks * 0.3
    cur = x0
    kicker = []
    for i, (s, fill, op) in enumerate([("PASSPORT NO. DC-2027", GOLD, None), ("ISSUED BOSTON, MA", PAPER, 0.5),
                                       ("VALID WORLDWIDE", PAPER, 0.5)]):
        if i:
            kicker.append(f'<rect x="{n(cur + 14)}" y="70" width="30" height="1" fill="{PAPER}" opacity="0.2"/>')
            cur += 58
        kicker.append(svg.text(cur, 74, ("mono", s, fill, op), ks, ls=kls))
        cur += measure("mono", s, ks, kls) - kls
    body += kicker

    size = min(fit("serif", "David", 124, 520, -3.6), fit("serif-i", "Czartoryski", 124, 520, -3.6))
    ls = round(-0.03 * size, 2)
    w_last = measure("serif-i", "Czartoryski", size, ls)
    svg.defs.append(foil("foil", x0, x0 + w_last, H, dur=10, begin=1.5))
    body.append(svg.text(x0 - 4, 196, ("serif", "David", PAPER), size, ls=ls))
    for fill, attrs in [(GOLD2, ""), ("#fff4d6", ' mask="url(#foil)"')]:
        body.append(svg.text(x0 - 2, 196 + size * 0.9, ("serif-i", "Czartoryski", fill), size, ls=ls, attrs=attrs))
    for i, line in enumerate(["Software engineer and founder out of Northeastern.",
                              "Wrestler by trade, Polish at home, Bostonian by zip code."]):
        body.append(svg.text(x0, 366 + i * 25, ("sans", line, PAPER, 0.7), 17))

    # stats rail
    body.append(f'<rect x="{x0}" y="418" width="{W - 2 * x0}" height="1" fill="{PAPER}" opacity="0.1"/>')
    for i, (v, k) in enumerate([("23", "COUNTRIES STAMPED"), ("03", "HOME BASES"),
                                ("1ST", "MA STATE CHAMPION"), ("04", "VENTURES IN THE HOLD")]):
        cx = x0 + i * 222
        body.append(svg.text(cx, 441, ("mono", k, PAPER, 0.5), 9.5, ls=2.6))
        body.append(svg.text(cx - 1, 476, ("serif", v, PAPER), 34, ls=-0.6))

    # the boarding pass
    CW, CH = 352, 282
    card = [f'<rect x="6" y="26" width="{CW - 12}" height="{CH - 10}" rx="16" fill="#000" opacity="0.6" filter="url(#shadow)"/>',
            f'<rect width="{CW}" height="{CH}" rx="16" fill="{PAPER}" filter="url(#paper)"/>',
            svg.text(20, 24, ("mono", "BOARDING PASS", INK, 0.7), 9, ls=2.7),
            svg.text(CW - 20, 24, ("mono", "HERCULES AIR", INK, 0.7), 9, ls=2.7, anchor="end"),
            plane(CW - 20 - measure("mono", "HERCULES AIR", 9, 2.7) - 10, 20.5, 12, INK, opacity=0.7),
            f'<rect y="38" width="{CW}" height="1" fill="{INK}" opacity="0.14"/>',
            svg.text(20, 62, ("mono", "FROM", INK, 0.55), 8.5, ls=2.2),
            svg.text(17, 110, ("serif", "BOS", INK), 52, ls=-1.5),
            svg.text(20, 128, ("mono", "BOSTON", INK, 0.6), 8.5, ls=1.3),
            svg.text(CW - 20, 62, ("mono", "TO", INK, 0.55), 8.5, ls=2.2, anchor="end"),
            f'<g stroke="{INK}" stroke-opacity="0.4" stroke-dasharray="3 3"><line x1="128" y1="93" x2="156" y2="93"/>'
            f'<line x1="178" y1="93" x2="206" y2="93"/></g>',
            plane(167, 93, 15, INK, opacity=0.5)]
    fx = CW - 20 - 3 * TW - 2 * 3
    card.append(flap_tiles(svg, fx, 71, [d[0] for d in DESTINATIONS], TW, TH, TS, rng, INK, PAPER))
    for k, (_, city) in enumerate(DESTINATIONS):
        # each name shows for its own segment; negative delays line them up with the tiles
        d = -((cycle - (k * SEGMENT + 0.36)) % cycle)
        card.append(svg.text(CW - 20, 128, ("mono", city, INK, 0.6), 8.5, ls=1.3, anchor="end",
                             cls="city", attrs=f' style="animation-delay:{d:.2f}s"'))
    card.append(f'<line x1="20" y1="146" x2="{CW - 20}" y2="146" stroke="{INK}" stroke-opacity="0.25" stroke-dasharray="3 3"/>')
    facts = [("PASSENGER", "CZARTORYSKI / D"), ("FLIGHT", "HH 2027"), ("GATE", "23"),
             ("SEAT", "1A"), ("CLASS", "FOUNDER"), ("DEPARTS", "MAY 2027")]
    cols = [20, 150, 250]  # the passenger name needs the widest column
    for i, (k, v) in enumerate(facts):
        cx, cy = cols[i % 3], 170 + (i // 3) * 40
        card.append(svg.text(cx, cy, ("mono", k, INK, 0.55), 8, ls=2))
        card.append(svg.text(cx, cy + 16, ("mono-sb", v, INK), 11, ls=0.6))
    card.append(barcode(11, 20, 236, CW - 40, 30, INK, 0.72))
    body.append(f'<g transform="translate(612 116) rotate(-2.4 {CW / 2} {CH / 2})">' + "".join(card) + "</g>")

    body.append("</g>")
    svg.add(*body)
    svg.save("hero.svg")


# --------------------------------------------------------------- headers
HEADERS = [
    ("01", "Passport", "Twenty-three countries, ", "one passport."),
    ("02", "Flight log", "Every leg ", "logged."),
    ("03", "Cargo", "What’s in ", "the hold."),
    ("04", "Carry-on", "Only what ", "fits overhead."),
    ("05", "Arrivals", "Now ", "landing."),
]
THEMES = {
    # name: (title, italic base, italic shine, kicker text, rules)
    "dark": (PAPER, GOLD2, "#fff4d6", PAPER, PAPER),
    "light": (INK, GOLD_INK, "#d9b565", INK, INK),
}


def header(num, kicker, plain, italic, theme):
    title_c, gold_c, shine, kick_c, rule_c = THEMES[theme]
    W, H = 900, 112
    svg = Svg(W, H, f"{num} {kicker}. {plain}{italic}")
    num_c = GOLD if theme == "dark" else GOLD_INK
    ks, kls = 11, 3.3
    parts = [svg.text(2, 20, ("mono", num, num_c), ks, ls=kls)]
    x = 2 + measure("mono", num, ks, kls) + 12
    parts.append(f'<rect x="{n(x)}" y="16" width="40" height="1" fill="{rule_c}" opacity="0.22"/>')
    parts.append(svg.text(x + 56, 20, ("mono", kicker.upper(), kick_c, 0.55), ks, ls=kls))
    size = fit("serif", plain + italic, 52, W - 8, -1.0)
    ls = round(-0.02 * size, 2)
    x_it = measure("serif", plain, size, ls)
    svg.defs.append(foil("foil", x_it, x_it + measure("serif-i", italic, size, ls), H, dur=11, begin=0.6 * int(num)))
    parts.append(svg.text(0, 90, [("serif", plain, title_c), ("serif-i", italic, gold_c)], size, ls=ls))
    # the glint layer repeats the whole line so the italic lands exactly where it did above
    parts.append(svg.text(0, 90, [("serif", plain, title_c, 0), ("serif-i", italic, shine)], size, ls=ls,
                          attrs=' mask="url(#foil)"'))
    svg.add(*parts)
    slug = kicker.lower().replace(" ", "-")
    svg.save(f"headers/{num}-{slug}{'' if theme == 'dark' else '-light'}.svg")


# -------------------------------------------------------------- dividers
# one leg per section, a round trip that lands back in Boston for Arrivals
LEGS = [("BOS", "SFO", GOLD), ("SFO", "WAW", RED), ("WAW", "IST", BLUE), ("IST", "ATH", GREEN), ("ATH", "BOS", VIOLET)]


def divider(i, a, b, colour, theme):
    W, H = 760, 30
    y = 15
    line_c = PAPER if theme == "dark" else INK
    if theme == "light" and colour == GOLD:
        colour = GOLD_INK
    svg = Svg(W, H, f"Route divider, {a} to {b}")
    x0, x1 = 44, W - 44
    dur = 7.5
    svg.defs.append(f'<linearGradient id="trail" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{colour}" stop-opacity="0"/>'
                    f'<stop offset="1" stop-color="{colour}" stop-opacity="0.9"/></linearGradient>')
    svg.defs.append(f'<clipPath id="lane"><rect x="{x0 + 6}" y="0" width="{x1 - x0 - 12}" height="{H}"/></clipPath>')
    svg.add(
        svg.text(0, y + 3.6, ("mono-md", a, line_c, 0.6), 10, ls=2),
        svg.text(W, y + 3.6, ("mono-md", b, line_c, 0.6), 10, ls=2, anchor="end"),
        f'<line x1="{x0 + 8}" y1="{y}" x2="{x1 - 8}" y2="{y}" stroke="{line_c}" stroke-opacity="0.22" stroke-dasharray="4 6"/>',
        f'<circle cx="{x0}" cy="{y}" r="3.2" fill="none" stroke="{colour}" stroke-width="1.4"/>',
        f'<circle cx="{x1}" cy="{y}" r="3.2" fill="{colour}"/>',
        '<g clip-path="url(#lane)"><g>'
        f'<animateTransform attributeName="transform" type="translate" values="{x0 - 20} {y};{x1 + 20} {y}" '
        f'dur="{dur}s" repeatCount="indefinite"/>'
        f'<rect x="-150" y="-1" width="140" height="2" rx="1" fill="url(#trail)"/>'
        + plane(0, 0, 18, colour) + "</g></g>",
    )
    svg.save(f"dividers/{i}-{a.lower()}-{b.lower()}{'' if theme == 'dark' else '-light'}.svg")


# ---------------------------------------------------------------- button
def button():
    W, H = 480, 86
    svg = Svg(W, H, "Open the passport at davidczartoryski.com")
    svg.css += [".blink{animation:blink 1.4s steps(1,end) infinite}",
                "@keyframes blink{0%,55%{opacity:1}56%,100%{opacity:.2}}",
                ".nudge{animation:nudge 2.4s ease-in-out infinite}",
                "@keyframes nudge{0%,60%,100%{transform:translateX(0)}75%{transform:translateX(5px)}}"]
    px = 356  # perforation
    shape = (f"M12,0.75 H{px - 9} A9,9 0 0 0 {px + 9},0.75 H{W - 12.75} A12,12 0 0 1 {W - 0.75},12.75 "
             f"V{H - 12.75} A12,12 0 0 1 {W - 12.75},{H - 0.75} H{px + 9} A9,9 0 0 0 {px - 9},{H - 0.75} "
             f"H12.75 A12,12 0 0 1 0.75,{H - 12.75} V12.75 A12,12 0 0 1 12.75,0.75 Z")
    svg.defs.append(paper_filter("paper", seed=4))
    size = 29
    host = "davidczartoryski"
    w_host = measure("serif", host, size, -0.4)
    w_com = measure("serif-i", ".com", size, -0.4)
    svg.add(
        f'<path d="{shape}" fill="{PAPER}" filter="url(#paper)"/>',
        f'<path d="{shape}" fill="none" stroke="{INK}" stroke-opacity="0.22" stroke-width="1.5"/>',
        f'<circle class="blink" cx="28" cy="26.5" r="3.2" fill="{RED}"/>',
        svg.text(40, 30, ("mono-md", "NOW BOARDING · OPEN THE PASSPORT", INK, 0.62), 9, ls=2.2),
        svg.text(24, 66, [("serif", host, INK), ("serif-i", ".com", GOLD_INK)], size, ls=-0.4),
        f'<g class="nudge">{svg.text(24 + w_host + w_com + 14, 64, ("mono-md", "→", GOLD_INK), 20)}</g>',
        f'<line x1="{px}" y1="14" x2="{px}" y2="{H - 14}" stroke="{INK}" stroke-opacity="0.3" stroke-dasharray="2 3"/>',
        svg.text(px + 18, 30, ("mono", "GATE", INK, 0.55), 8, ls=2),
        svg.text(px + 16, 66, ("serif", "23", INK), 32),
        barcode(5, px + 62, 22, 44, 44, INK, 0.72),
    )
    svg.save("button.svg")


# ------------------------------------------------------------------- map
def world_map():
    geo = json.loads((ROOT / "data/geo.json").read_text())
    VX, VY, VW, VH = 20, -6, 1160, 356  # everything visited sits north of the equator
    svg = Svg(1000, round(1000 * VH / VW), "World map: 23 countries stamped, home bases in Boston, "
                                           "San Francisco and Warsaw", view=f"{VX} {VY} {VW} {VH}")
    svg.css += [
        ".route{stroke-dasharray:4 5;animation:dash 1.1s linear infinite}",
        "@keyframes dash{to{stroke-dashoffset:-9}}",
        ".ping{transform-box:fill-box;transform-origin:center;animation:ping 3.2s ease-out infinite}",
        "@keyframes ping{0%{transform:scale(.4);opacity:.8}80%,100%{transform:scale(2.6);opacity:0}}",
    ]
    svg.defs += [
        f'<clipPath id="frame"><rect x="{VX}" y="{VY}" width="{VW}" height="{VH}" rx="20"/></clipPath>',
        f'<radialGradient id="mglow"><stop offset="0" stop-color="{GOLD}" stop-opacity="0.5"/>'
        f'<stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient>',
        f'<radialGradient id="vig" cx="0.5" cy="0.45" r="0.75"><stop offset="0.6" stop-color="{INK}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{INK}" stop-opacity="0.85"/></radialGradient>',
    ]
    body = ['<g clip-path="url(#frame)">', f'<rect x="{VX}" y="{VY}" width="{VW}" height="{VH}" fill="{INK}"/>',
            f'<path d="{geo["sphere"]}" fill="{PAPER}" fill-opacity="0.02" stroke="{PAPER}" stroke-opacity="0.12"/>']
    land = [c["d"] for c in geo["countries"] if not c["slug"]]
    seen = [c["d"] for c in geo["countries"] if c["slug"]]
    body.append(f'<path d="{"".join(land)}" fill="{PAPER}" fill-opacity="0.06" stroke="{PAPER}" '
                f'stroke-opacity="0.14" stroke-width="0.5"/>')
    body.append(f'<path d="{"".join(seen)}" fill="{GOLD}" fill-opacity="0.78" stroke="{INK}" '
                f'stroke-opacity="0.6" stroke-width="0.8"/>')

    cp = geo["cityPoints"]
    bases = [("BOS", cp["boston"]), ("SFO", cp["menloPark"]), ("WAW", cp["warsaw"])]

    def arc(a, b):
        mx, my = (a["x"] + b["x"]) / 2, (a["y"] + b["y"]) / 2
        d = ((b["x"] - a["x"]) ** 2 + (b["y"] - a["y"]) ** 2) ** 0.5
        return f"M{a['x']},{a['y']} Q{mx:.1f},{my - d * 0.28:.1f} {b['x']},{b['y']}"

    rng = random.Random(23)
    for m in geo["markers"]:
        body.append(f'<g transform="translate({m["x"]} {m["y"]})"><circle r="7" fill="url(#mglow)"/>'
                    f'<circle r="4" fill="none" stroke="{PAPER}" stroke-width="0.8" class="ping" '
                    f'style="animation-delay:-{rng.uniform(0, 3.2):.2f}s"/><circle r="1.8" fill="{PAPER}"/></g>')
    for i, (code, pt) in enumerate(bases[1:]):
        path = arc(cp["boston"], pt)
        body.append(f'<path d="{path}" fill="none" stroke="{PAPER}" stroke-opacity="0.6" stroke-width="1.3" class="route"/>')
        body.append(f'<g><animateMotion dur="{8 + i * 2.5}s" repeatCount="indefinite" rotate="auto" '
                    f'keyPoints="0;1;1" keyTimes="0;0.8;1" calcMode="linear" path="{path}"/>'
                    + plane(0, 0, 16, GOLD2) + "</g>")
    for code, pt in bases:
        body.append(f'<g transform="translate({pt["x"]} {pt["y"]})"><circle r="3.4" fill="{RED}" stroke="{INK}" stroke-width="0.9"/>'
                    + svg.text(7, -6, ("mono-md", code, PAPER), 12, ls=1.6) + "</g>")

    body.append(f'<rect x="{VX}" y="{VY}" width="{VW}" height="{VH}" fill="url(#vig)"/>')
    # captions, down in the empty Pacific
    bottom = VY + VH
    body.append(svg.text(VX + 30, bottom - 50, ("mono", "ENTRY STAMPS \u00b7 23", GOLD), 13, ls=3.6))
    body.append(plane(VX + 37, bottom - 29.5, 14, PAPER, opacity=0.55))
    body.append(svg.text(VX + 53, bottom - 25, ("mono", "ROUTES OUT OF BOS", PAPER, 0.55), 12, ls=3))
    body.append("</g>")
    svg.add(*body)
    svg.save("map.svg")


def main():
    hero()
    for h in HEADERS:
        for theme in THEMES:
            header(*h, theme)
    for i, leg in enumerate(LEGS, 1):
        for theme in THEMES:
            divider(i, *leg, theme)
    button()
    world_map()


if __name__ == "__main__":
    main()
