"""Isometric homelab art for the profile: the 10-inch rack, nothing else.
Writes lab-day.svg (paper and ink, powered down) and lab-night.svg (lit, LEDs blinking).
Geometry is in mm. Pod count from `kubectl get pods -A` on the k3s cluster."""
import math, random

W, H = 1000, 520
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
NODES = ["k3s-1", "k3s-2", "k3s-3", "k3s-4"]  # top to bottom
NOTES = ["8 × 1 GbE · 5 links up",  # one quiet line per unit, top to bottom
         "control plane · 25 pods", "control plane · 21 pods", "control plane · 52 pods", "worker · 31 pods"]
PODS = 129

A, E, K = math.radians(30), math.radians(15), 1.3  # camera azimuth, elevation, scale
V = (math.sin(A) * math.cos(E), -math.cos(A) * math.cos(E), math.sin(E))
R = (math.cos(A), math.sin(A), 0)
U = (-math.sin(A) * math.sin(E), math.cos(A) * math.sin(E), math.cos(E))
OX, OY = 0, 0  # set below so the rack is centred


def P(x, y, z):
    return OX + K * (x * R[0] + y * R[1]), OY - K * (x * U[0] + y * U[1] + z * U[2])


RACK_W, RACK_D, WALL = 254, 200, 7
NODE_W, NODE_D, NODE_H, GAP = 179, 183, 34.5, 7
XI = (RACK_W - NODE_W) / 2
SW_H = 26
RU = 44.45  # one rack unit
HEIGHT = 2 * WALL + 5 * RU + 6

# centre the rack's screen bounding box in the canvas, leaving room for the caption
_xs, _ys = zip(*(P(x, y, z) for x in (0, RACK_W) for y in (0, RACK_D) for z in (0, HEIGHT)))
OX = 340 - (min(_xs) + max(_xs)) / 2
OY = (H - 60) / 2 - (min(_ys) + max(_ys)) / 2 + 10


def pts(quad):
    return " ".join("%.1f,%.1f" % P(*p) for p in quad)


def scene(night):
    faces = []

    def box(x0, y0, z0, x1, y1, z1, m):
        for key, quad in (
            ("top", [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]),
            ("front", [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)]),
            ("side", [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)]),
        ):
            c = [sum(v) / 4 for v in zip(*quad)]
            faces.append((c[0] * V[0] + c[1] * V[1] + c[2] * V[2],
                          f'<polygon points="{pts(quad)}" fill="{m[key]}" stroke="{m["s"]}" stroke-width="{m["w"]}" stroke-linejoin="round"/>'))

    if night:
        shell = dict(top="#2b3347", front="#1a2131", side="#121827", s="#38425c", w=.8)
        inner = dict(top="#0d111b", front="#0d111b", side="#0b0f18", s="#0d111b", w=0)
        unit = dict(top="#1d2434", front="#131926", side="#0e131e", s="#2a3247", w=.7)
        slot = dict(top="#05070b", front="#05070b", side="#05070b", s="#05070b", w=0)
    else:
        ink = "#1d1d1f"
        shell = dict(top="#ffffff", front="#f3efe7", side="#e4ded1", s=ink, w=1.1)
        inner = dict(top="#d9d2c3", front="#d9d2c3", side="#d9d2c3", s=ink, w=0)
        unit = dict(top="#ffffff", front="#f7f4ee", side="#e9e4d8", s=ink, w=1)
        slot = dict(top="#cfc8b9", front="#cfc8b9", side="#cfc8b9", s="#cfc8b9", w=0)

    def rail(x):
        """Square cage-nut holes, three per rack unit, on a wall's front edge."""
        for u in range(5):
            for h in (6.35, 22.2, 38.1):
                hz = WALL + 3 + u * RU + h
                box(x + 2.2, -.4, hz - 1.3, x + 4.8, 0, hz + 1.3, slot)

    # drawn back to front: back panel, floor, left wall, units bottom-up, right wall, lid
    box(WALL, RACK_D - 4, WALL, RACK_W - WALL, RACK_D, HEIGHT - WALL, inner)
    box(0, 0, 0, RACK_W, RACK_D, WALL, shell)
    box(0, 0, WALL, WALL, RACK_D, HEIGHT - WALL, shell)
    rail(0)

    leds, tags, screws = [], [], []
    rnd = random.Random(4)
    tape = dict(top="#e8e2d0", front="#e8e2d0", side="#bdb6a3", s="#e8e2d0", w=0) if night else \
        dict(top="#ffffff", front="#ffffff", side="#ffffff", s="#1d1d1f", w=.6)
    blue = dict(top="#3b7be0", front="#2c63c4", side="#1d4590", s="#1d4590", w=0) if night else slot
    rows = []

    def label(x, z, text, size=6.2, col=None):
        ox, oy = P(x, 6.6, z)
        ax, ay = P(x + 1, 6.6, z)
        bx, by = P(x, 6.6, z - 1)
        tags.append(f'<text transform="matrix({ax-ox:.4f},{ay-oy:.4f},{bx-ox:.4f},{by-oy:.4f},{ox:.1f},{oy:.1f})" '
                    f'font-family="{MONO}" font-size="{size}" font-weight="700" letter-spacing=".4" '
                    f'fill="{col or "#15181f"}">{text}</text>')

    def faceplate(z0, inner_x0, inner_x1, inner_z0, inner_z1, name):
        """1U panel between the rails with a cutout around the device, two thumbscrews a side
        and a label-maker tape on the left wing."""
        box(WALL, 7, z0 + .5, inner_x0, 9, z0 + RU - .5, unit)
        box(inner_x1, 7, z0 + .5, RACK_W - WALL, 9, z0 + RU - .5, unit)
        box(inner_x0, 7, inner_z1, inner_x1, 9, z0 + RU - .5, unit)
        box(inner_x0, 7, z0 + .5, inner_x1, 9, inner_z0, unit)
        for sx in (WALL + 5, RACK_W - WALL - 5):
            for sz in (z0 + 7, z0 + RU - 7):
                screws.append(P(sx, 6.8, sz))
        box(WALL + 3, 6.6, z0 + RU / 2 - 3.6, inner_x0 - 4, 7, z0 + RU / 2 + 3.6, tape)
        label(WALL + 4.4, z0 + RU / 2 - 2.2, name)

    for i, name in enumerate(reversed(NODES)):
        z0 = WALL + 3 + i * RU
        z = z0 + (RU - NODE_H) / 2
        box(XI, 9, z, XI + NODE_W, 9 + NODE_D, z + NODE_H, unit)
        f = 8.6
        box(XI + 8, f, z + 12, XI + 18, 9, z + 22, slot)                     # power button
        for k in range(2):                                                  # audio jacks
            box(XI + 24 + k * 6, f, z + 15, XI + 27.5 + k * 6, 9, z + 18.5, slot)
        box(XI + 40, f, z + 15, XI + 47, 9, z + 18, slot)                   # USB-C
        for k in range(2):                                                  # USB-A, USB 3 blue
            box(XI + 52 + k * 15, f, z + 14, XI + 63 + k * 15, 9, z + 19, blue)
        for k in range(12):                                                 # vent slots
            vx = XI + 98 + k * 6.2
            box(vx, f, z + 7, vx + 2.4, 9, z + NODE_H - 7, slot)
        leds.append((P(XI + 13, 8.4, z + 17), "#fff2c8", None))
        leds.append((P(XI + 88, 8.4, z + 9), "#f3b34c", (rnd.uniform(.7, 1.6), rnd.uniform(0, 1.5))))
        faceplate(z0, XI - 1, XI + NODE_W + 1, z - 1, z + NODE_H + 1, name)
        rows.append(P(RACK_W, 0, z0 + RU / 2))

    z0 = WALL + 3 + 4 * RU                                                   # switch
    sx0, SW_W = (RACK_W - 150) / 2, 150
    z = z0 + (RU - SW_H) / 2
    box(sx0, 9, z, sx0 + SW_W, 110, z + SW_H, unit)
    for k in range(8):
        px = sx0 + 30 + k * 14
        box(px, 8.6, z + 5, px + 10, 9, z + 15, slot)
        if k < 5:
            leds.append((P(px + 2.5, 8.4, z + 19.5), "#7be495", None))
            leds.append((P(px + 7.5, 8.4, z + 19.5), "#f3b34c", (rnd.uniform(.25, .7), rnd.uniform(0, 1))))
    faceplate(z0, sx0 - 1, sx0 + SW_W + 1, z - 1, z + SW_H + 1, "SW-8")
    rows.append(P(RACK_W, 0, z0 + RU / 2))

    box(RACK_W - WALL, 0, WALL, RACK_W, RACK_D, HEIGHT - WALL, shell)
    rail(RACK_W - WALL)
    box(0, 0, HEIGHT - WALL, RACK_W, RACK_D, HEIGHT, shell)
    body = "".join(s for _, s in faces)

    out = []
    for (x, y), col, blink in leds:
        if night:
            anim = f' style="animation:bl {blink[0]:.2f}s {blink[1]:.2f}s infinite"' if blink else ""
            out.append(f'<g{anim}><circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{col}" opacity=".35" filter="url(#glow)"/>'
                       f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.4" fill="{col}"/></g>')
        else:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.3" fill="#1d1d1f"/>')
    # lid edge catches the light from above
    if night:
        a, b = P(0, 0, HEIGHT), P(RACK_W, 0, HEIGHT)
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#e9c86d" stroke-width="1" opacity=".6"/>')
    for x, y in screws:
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.1" fill="{"#3a4460" if night else "#faf8f4"}" '
                   f'stroke="{"#56607c" if night else "#1d1d1f"}" stroke-width=".7"/>')
    return body, "".join(tags), "".join(out), rows


def svg(night):
    body, tags, top, rows = scene(night)
    fx, fy = P(RACK_W / 2, RACK_D / 2, 0)
    cap_y = H - 28
    fg = "#eef1f7" if night else "#1d1d1f"
    names = ["SW-8"] + NODES
    col = "".join(f'<text x="640" y="{y + 4:.0f}"><tspan fill="{fg}" font-weight="700">{n}</tspan>'
                  f'<tspan x="712">{t}</tspan></text>' for (x, y), n, t in zip(reversed(rows), names, NOTES))
    if night:
        head = """<style>
    @keyframes bl { 0%, 100% { opacity: 1 } 45% { opacity: 1 } 50% { opacity: .1 } 60% { opacity: 1 } }
  </style>
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#070a12"/><stop offset="1" stop-color="#121a2c"/></linearGradient>
    <radialGradient id="pool"><stop offset="0" stop-color="#f3dc95" stop-opacity=".18"/><stop offset="1" stop-color="#f3dc95" stop-opacity="0"/></radialGradient>
    <filter id="glow" x="-2" y="-2" width="5" height="5"><feGaussianBlur stdDeviation="2.4"/></filter>
  </defs>"""
        bg = (f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'
              f'<ellipse cx="{fx:.0f}" cy="{fy+14:.0f}" rx="300" ry="70" fill="url(#pool)"/>')
        cap = f"4 nodes · {PODS} pods · 0 cloud bills"
        cap_col = "#7f8aa3"
        label = f"The homelab after dark: four k3s nodes and a switch in a ten-inch rack, {PODS} pods running."
    else:
        head = ""
        bg = (f'<rect width="{W}" height="{H}" fill="#faf8f4"/>'
              f'<ellipse cx="{fx:.0f}" cy="{fy+12:.0f}" rx="210" ry="34" fill="#1d1d1f" opacity=".05"/>')
        cap = "Fig. 1 · it hums after dark"
        cap_col = "#8a857b"
        label = "Fig. 1, the homelab: four k3s nodes and a switch in a ten-inch rack, drawn in ink."
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{label}">
  {head}
  {bg}
  <g>{body}</g>
  <g>{tags}</g>
  <g>{top}</g>
  <g font-family="{MONO}" font-size="13" fill="{cap_col}">{col}</g>
  <text x="{340}" y="{cap_y}" text-anchor="middle" font-family="{MONO}" font-size="13" letter-spacing="1.5" fill="{cap_col}">{cap}</text>
</svg>"""


open("assets/lab-night.svg", "w").write(svg(True))
open("assets/lab-day.svg", "w").write(svg(False))
print("ok")
