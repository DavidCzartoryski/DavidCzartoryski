#!/usr/bin/env python3
"""Writes board.svg, the arrivals board at the foot of the README.

The same numbers github-readme-stats would show, pulled straight from the
GitHub API through `gh` and drawn as a departures board in the portfolio's
palette: split-flap counters, a year of weekly contributions, and a cargo
manifest of languages by bytes across public repos.

There is no stars row. A zero rendered in split-flap tiles is still a zero,
and the rows here are the ones that say something about the work.

Private contributions count in the calendar total because the profile
publishes them; the workflow's token sees exactly what a visitor sees.

Run: python3 scripts/generate-board.py   (needs gh, fonttools + brotli)
Called by scripts/refresh-board.sh, which the refresh-board workflow runs daily.
"""
import datetime as dt
import json
import random
import subprocess

from typeset import (
    BLUE, GOLD, GREEN, INK3, PAPER, RED, VIOLET,
    Svg, flap_css, flap_tiles, measure, n, plane,
)

USER = "DavidCzartoryski"
PANEL = "#080c19"
# Language order is fixed: the stamp inks, with gold stepped down one notch so
# all five sit in the same lightness band on the panel (validated for CVD).
INKS = ["#b88c3c", RED, BLUE, GREEN, VIOLET]
OTHER = "#5b6272"
TOP_LANGS = 5

GRAPHQL = """
query($login: String!) {
  user(login: $login) {
    pullRequests { totalCount }
    repositoriesContributedTo(contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]) { totalCount }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      nodes {
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
  }
}
"""


def fetch():
    out = subprocess.run(["gh", "api", "graphql", "-f", f"query={GRAPHQL}", "-F", f"login={USER}"],
                         capture_output=True, text=True, check=True).stdout
    user = json.loads(out)["data"]["user"]
    cal = user["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    weeks = [(w["contributionDays"][0]["date"], sum(d["contributionCount"] for d in w["contributionDays"]))
             for w in cal["weeks"]]

    streak = best = 0
    for d in days:
        streak = streak + 1 if d["contributionCount"] else 0
        best = max(best, streak)

    langs = {}
    for repo in user["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]

    return {
        "total": cal["totalContributions"],
        "weeks": weeks,
        "active": sum(1 for d in days if d["contributionCount"]),
        "streak": best,
        "prs": user["pullRequests"]["totalCount"],
        "contributed": user["repositoriesContributedTo"]["totalCount"],
        "langs": sorted(langs.items(), key=lambda kv: -kv[1]),
    }


def board(d, today):
    W, H = 820, 336
    svg = Svg(W, H, f"Arrivals board: {d['total']} contributions in the last year, "
                    f"{d['contributed']} repos contributed to, {d['prs']} pull requests, "
                    f"{d['active']} active days, longest streak {d['streak']} days. Languages: "
                    + ", ".join(k for k, _ in d["langs"][:TOP_LANGS]) + ".")
    rng = random.Random(today.toordinal())
    big = (34, 46, 30)    # tile w, h, glyph size for the headline counter
    small = (22, 26, 16)
    svg.css += [
        ".big{animation:bigflap 14s linear infinite}", flap_css(5, big[1], 14, 1, name="bigflap"),
        ".small{animation:smallflap 14s linear infinite}", flap_css(5, small[1], 14, 1, name="smallflap"),
    ]
    svg.defs += [
        f'<clipPath id="clip-big"><rect width="{big[0]}" height="{big[1]}" rx="4"/></clipPath>',
        f'<clipPath id="clip-small"><rect width="{small[0]}" height="{small[1]}" rx="3"/></clipPath>',
        '<clipPath id="bar"><rect x="440" y="222" width="340" height="8" rx="4"/></clipPath>',
    ]
    dim = (PAPER, 0.5)
    o = [f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" fill="{PANEL}" stroke="{PAPER}" stroke-opacity="0.08"/>',
         plane(46, 30.5, 13, GOLD),
         svg.text(60, 34, ("mono-md", "ARRIVALS · GITHUB.COM/DAVIDCZARTORYSKI", GOLD), 10.5, ls=2.6),
         svg.text(W - 40, 34, ("mono", f"UPDATED {today:%Y-%m-%d}", *dim), 9, ls=1.6, anchor="end"),
         f'<rect x="40" y="50" width="{W - 80}" height="1" fill="{PAPER}" opacity="0.08"/>']

    def tiles(value, count, size, cls, clip, delay):
        w, h, gs = size
        word = str(value).rjust(count)
        return word, lambda x, y: flap_tiles(svg, x, y, [word], w, h, gs, rng, INK3, PAPER, gap=3, cls=cls,
                                             delay=delay, clip=clip, pool="0123456789")

    # headline: contributions, and the year they came from
    o.append(svg.text(40, 80, ("mono", "CONTRIBUTIONS", *dim), 9, ls=2.2))
    _, draw = tiles(d["total"], 4, big, "big", "clip-big", 0)
    o.append(draw(40, 90))
    o.append(svg.text(40, 158, ("mono", "LAST 12 MONTHS", *dim), 9, ls=2.2))

    x0, x1, base, top = 262, W - 40, 140, 84
    slot = (x1 - x0) / len(d["weeks"])
    bw = min(slot - 2, 7)
    peak = max((c for _, c in d["weeks"]), default=0) or 1
    bars, months, last_month = [], [], None
    for i, (start, c) in enumerate(d["weeks"]):
        bx = x0 + i * slot + (slot - bw) / 2
        if c:
            bh = max(2.0, (base - top) * c / peak)
            r = min(2.0, bw / 2)
            # rounded data end, square at the baseline
            bars.append(f'<path d="M{n(bx)},{base} V{n(base - bh + r)} Q{n(bx)},{n(base - bh)} {n(bx + r)},{n(base - bh)} '
                        f'H{n(bx + bw - r)} Q{n(bx + bw)},{n(base - bh)} {n(bx + bw)},{n(base - bh + r)} V{base} Z"/>')
        month = dt.date.fromisoformat(start).replace(day=1)
        if month != last_month and i < len(d["weeks"]) - 2:
            if last_month is not None:
                months.append(svg.text(bx, base + 16, ("mono", f"{month:%b}".upper(), PAPER, 0.4), 8, ls=1.2))
            last_month = month
    o.append(f'<rect x="{x0}" y="{base}" width="{x1 - x0}" height="1" fill="{PAPER}" opacity="0.14"/>')
    o.append(f'<g fill="{GOLD}">' + "".join(bars) + "</g>")
    o += months
    i_peak = max(range(len(d["weeks"])), key=lambda i: d["weeks"][i][1])
    px = x0 + i_peak * slot + slot / 2
    o.append(svg.text(min(px, x1 - 30), top - 7, ("mono-md", f"PEAK WEEK {peak}", PAPER, 0.7), 8.5, ls=1.2,
                      anchor="middle" if px < x1 - 30 else "end"))

    o.append(f'<rect x="40" y="184" width="{W - 80}" height="1" fill="{PAPER}" opacity="0.08"/>')

    # counters
    rows = [("REPOS CONTRIBUTED TO", d["contributed"]), ("PULL REQUESTS", d["prs"]),
            ("DAYS ACTIVE · 12 MO", d["active"]), ("LONGEST STREAK · DAYS", d["streak"])]
    for i, (label, value) in enumerate(rows):
        y = 200 + i * 32
        o.append(svg.text(40, y + 18, ("mono", label, PAPER, 0.8), 10.5, ls=1.4))
        _, draw = tiles(value, 3, small, "small", "clip-small", 0.6 + i * 0.25)
        o.append(draw(400 - 3 * small[0] - 6, y))
        if i:
            o.append(f'<rect x="40" y="{y - 3}" width="360" height="1" fill="{PAPER}" opacity="0.06"/>')

    # cargo manifest
    o.append(svg.text(440, 210, ("mono", "CARGO MANIFEST · LANGUAGES BY BYTES", *dim), 9, ls=2.2))
    total = sum(s for _, s in d["langs"]) or 1
    top_l = d["langs"][:TOP_LANGS]
    rest = total - sum(s for _, s in top_l)
    entries = [(k, s, INKS[i]) for i, (k, s) in enumerate(top_l)] + ([("OTHER", rest, OTHER)] if rest else [])
    segs, cx = [], 440.0
    for _, s, colour in entries:
        w = 340 * s / total
        segs.append(f'<rect x="{n(cx)}" y="222" width="{n(max(w - 2, 1))}" height="8" fill="{colour}"/>')  # 2px surface gap
        cx += w
    o.append('<g clip-path="url(#bar)">' + "".join(segs) + "</g>")
    for i, (k, s, colour) in enumerate(entries):
        col, row = divmod(i, 3)
        lx, ly = 440 + col * 180, 256 + row * 26
        o.append(f'<circle cx="{lx + 4.5}" cy="{ly - 3.5}" r="4.5" fill="{colour}"/>')
        o.append(svg.text(lx + 16, ly, ("mono", k.upper(), PAPER, 0.85), 10, ls=1))
        o.append(svg.text(lx + 160, ly, ("mono-md", f"{100 * s / total:.1f}%", PAPER, 0.55), 10, anchor="end"))

    svg.add(*o)
    return svg


def main():
    d = fetch()
    today = dt.datetime.now(dt.timezone.utc).date()
    board(d, today).save("board.svg")
    print(f"total={d['total']} contributed={d['contributed']} prs={d['prs']} active={d['active']} "
          f"streak={d['streak']} langs={[k for k, _ in d['langs']]}")


if __name__ == "__main__":
    main()
