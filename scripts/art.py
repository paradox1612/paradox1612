"""Day / Night header art for the GitHub profile. Writes day.svg and night.svg."""
import random

W, H = 1000, 560
SERIF = "'Iowan Old Style','Palatino Linotype',Palatino,Georgia,'Times New Roman',serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
GROUND = 548


def skyline(seed=7):
    """Deterministic skyline. Returns list of (x, w, h, kind)."""
    rnd = random.Random(seed)
    out, x = [], -10
    while x < W + 10:
        w = rnd.choice([34, 42, 50, 58, 66])
        h = rnd.randint(46, 128)
        out.append((x, w, h))
        x += w + rnd.choice([0, 0, 4, 8])
    # the four homelab towers, under the searchlight
    towers = [(612, 30, 168), (646, 30, 186), (680, 30, 176), (714, 30, 158)]
    out = [b for b in out if b[0] + b[2] < 604 or b[0] > 748] + towers
    return sorted(out), towers


def bat_envelope(t):
    """t in [-1, 1] -> (top, bottom) of the bat emblem, y up, unit scale."""
    a = abs(t)
    top_pts = [(0, .30), (.07, .30), (.12, .70), (.17, .34), (.26, .30), (.45, .36), (.68, .50), (.88, .66), (1, .60)]
    bot_pts = [(0, -.80), (.10, -.52), (.20, -.40), (.30, -.58), (.42, -.22), (.54, -.36), (.66, -.06), (.78, -.18), (.92, .16), (1, .60)]

    def lerp(pts):
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if x0 <= a <= x1:
                u = (a - x0) / (x1 - x0)
                u = u * u * (3 - 2 * u)  # smoothstep between control points
                return y0 + (y1 - y0) * u
        return pts[-1][1]
    return lerp(top_pts), lerp(bot_pts)


def windows(buildings, lit_ratio, rnd, night):
    parts = []
    for bx, bw, bh in buildings:
        cols = max(1, (bw - 8) // 10)
        rows = max(1, (bh - 14) // 14)
        for r in range(rows):
            for c in range(cols):
                wx = bx + 6 + c * 10
                wy = GROUND - bh + 10 + r * 14
                if rnd.random() > lit_ratio:
                    continue
                if night:
                    anim = ""
                    if rnd.random() < .08:
                        d, delay = rnd.uniform(3, 9), rnd.uniform(0, 8)
                        anim = f' style="animation:flick {d:.1f}s {delay:.1f}s infinite"'
                    op = rnd.choice([.35, .5, .7, .9])
                    parts.append(f'<rect x="{wx}" y="{wy}" width="4" height="6" fill="#f3d98b" opacity="{op}"{anim}/>')
                else:
                    parts.append(f'<rect x="{wx}" y="{wy}" width="4" height="6" fill="none" stroke="#1d1d1f" stroke-width=".6" opacity=".35"/>')
    return "".join(parts)


def text_block(fg, sub, kicker, line1, line2, line3, hint, hint_col):
    return f"""
  <text x="64" y="104" font-family="{MONO}" font-size="15" letter-spacing="3" fill="{sub}">{kicker}</text>
  <text x="62" y="186" font-family="{SERIF}" font-style="italic" font-size="78" fill="{fg}">{line1}</text>
  <text font-family="{SERIF}" font-size="27" fill="{fg}">
    <tspan x="64" y="244">{line2}</tspan>
    <tspan x="64" y="280">{line3}</tspan>
  </text>
  <text font-family="{MONO}" font-size="14" fill="{hint_col}">{hint_lines(hint)}</text>"""


def hint_lines(hint):
    return "".join(f'<tspan x="64" y="{336 + i * 22}">{line}</tspan>' for i, line in enumerate(hint.split(" | ")))


def day():
    rnd = random.Random(3)
    blds, towers = skyline()
    b = "".join(f'<rect x="{x}" y="{GROUND-h}" width="{w}" height="{h}" fill="#faf8f4" stroke="#1d1d1f" stroke-width="1.1"/>' for x, w, h in blds)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="By day, I build full-stack enterprise LLM applications.">
  <rect width="{W}" height="{H}" fill="#faf8f4"/>
  <circle cx="790" cy="200" r="64" fill="none" stroke="#1d1d1f" stroke-width="1.1"/>
  <circle cx="790" cy="200" r="64" fill="#e9e4d8" opacity=".55"/>
  {text_block("#1d1d1f", "#8a857b", "KUSHKUMAR PATEL", "By day,", "I build full-stack enterprise", "LLM applications.",
              "There is more after dark. Switch GitHub to dark mode.", "#8a857b")}
  <g>{b}{windows(blds, .22, rnd, False)}</g>
  <line x1="0" y1="{GROUND}" x2="{W}" y2="{GROUND}" stroke="#1d1d1f" stroke-width="1.1"/>
</svg>"""


def night(signal_on=True):
    rnd = random.Random(3)
    blds, towers = skyline()
    cx, cy, rx, ry = 790, 196, 132, 74
    # bat emblem drawn as audio bars
    bars, n = [], 79
    for i in range(n):
        t = -1 + 2 * i / (n - 1)
        top, bot = bat_envelope(t)
        if top - bot < .02:
            continue
        x = cx + t * rx * .84
        y0, y1 = cy - top * ry * .78, cy - bot * ry * .78
        d = 1.1
        delay = (i % 8) * .14
        bars.append(f'<rect x="{x-1.2:.1f}" y="{y0:.1f}" width="2.4" height="{y1-y0:.1f}" rx="1.2" fill="#0b0f17" '
                    f'style="transform-origin:{x:.1f}px {cy}px;animation:talk {d:.2f}s {delay:.2f}s ease-in-out infinite alternate"/>')
    pts = []
    while len(pts) < 70:
        sx, sy = rnd.uniform(0, W), rnd.uniform(20, 330)
        if 40 < sx < 680 and 70 < sy < 350:
            continue  # keep the text block clear
        pts.append((sx, sy))
    stars = "".join(
        f'<circle cx="{sx:.0f}" cy="{sy:.0f}" r="{rnd.choice([.6, .8, 1.1])}" fill="#cfd6e6" '
        f'style="animation:tw {rnd.uniform(2, 6):.1f}s {rnd.uniform(0, 5):.1f}s infinite"/>' for sx, sy in pts)
    b = "".join(f'<rect x="{x}" y="{GROUND-h}" width="{w}" height="{h}" fill="#0e1320"/>' for x, w, h in blds)
    src_x, src_y = 663 + 12, GROUND - 186
    lamp = f'<rect x="{src_x-9}" y="{src_y-10}" width="18" height="10" rx="2" fill="#2a3142"/>'
    signal = ""
    if signal_on:
        signal = f"""
  <polygon points="{src_x-6},{src_y-8} {src_x+6},{src_y-8} {cx+rx*.62:.0f},{cy+ry*.55:.0f} {cx-rx*.62:.0f},{cy+ry*.55:.0f}" fill="url(#beam)"/>
  <ellipse cx="{cx}" cy="{cy}" rx="{rx+40}" ry="{ry+30}" fill="url(#halo)"/>
  <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#spot)"/>
  <g>{''.join(bars)}</g>"""
        hint = "Click the signal to see what I am building. | Switch GitHub to light mode for the day shift."
    else:
        hint = "The signal is off. | Switch GitHub to light mode for the day shift."
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="By night, I become Batman and build voice AI agents, a media player, and a homelab to run them all.">
  <style>
    @keyframes talk {{ from {{ transform: scaleY(.86) }} to {{ transform: scaleY(1) }} }}
    @keyframes tw {{ 0%,100% {{ opacity:.9 }} 50% {{ opacity:.2 }} }}
    @keyframes flick {{ 0%,92%,100% {{ opacity:.85 }} 94% {{ opacity:.1 }} 96% {{ opacity:.7 }} }}
  </style>
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#070a12"/><stop offset="1" stop-color="#121a2c"/></linearGradient>
    <linearGradient id="beam" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#f7e7b4" stop-opacity=".55"/><stop offset="1" stop-color="#f7e7b4" stop-opacity=".06"/></linearGradient>
    <radialGradient id="spot"><stop offset="0" stop-color="#fbf0c9"/><stop offset=".8" stop-color="#f3dc95"/><stop offset="1" stop-color="#e9c86d" stop-opacity=".9"/></radialGradient>
    <radialGradient id="halo"><stop offset=".6" stop-color="#f7e7b4" stop-opacity=".14"/><stop offset="1" stop-color="#f7e7b4" stop-opacity="0"/></radialGradient>
  </defs>
  <rect width="{W}" height="{H}" fill="url(#sky)"/>
  {stars}
  {signal}
  {text_block("#eef1f7", "#7f8aa3", "KUSHKUMAR PATEL", "By night,", "I become Batman and build voice AI agents,", "a media player, and a homelab to run them all.",
              hint, "#c9b67a")}
  <g>{b}{windows(blds, .3, rnd, True)}{lamp}</g>
  <rect x="0" y="{GROUND}" width="{W}" height="{H-GROUND}" fill="#0e1320"/>
</svg>"""


open("assets/day.svg", "w").write(day())
open("assets/night.svg", "w").write(night(True))
open("assets/night-off.svg", "w").write(night(False))
print("ok")
