"""ASCII STL of the homelab mini-rack: four Lenovo M720q nodes and a switch in a 10-inch frame.
Units are mm. GitHub renders ```stl fenced blocks as an interactive 3D viewer."""

tris = []


def box(x0, y0, z0, x1, y1, z1):
    """Axis-aligned box as 12 triangles (x = width, y = depth, z = height)."""
    v = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    faces = [  # quads as vertex indices, outward winding
        ((0, 2, 3, 1), (0, 0, -1)), ((4, 5, 7, 6), (0, 0, 1)),
        ((0, 1, 5, 4), (0, -1, 0)), ((2, 6, 7, 3), (0, 1, 0)),
        ((0, 4, 6, 2), (-1, 0, 0)), ((1, 3, 7, 5), (1, 0, 0)),
    ]
    for (a, b, c, d), n in faces:
        tris.append((n, v[a], v[b], v[c]))
        tris.append((n, v[a], v[c], v[d]))


RACK_W, RACK_D = 254, 200          # 10" frame
POST = 14
NODE_W, NODE_D, NODE_H = 179, 183, 34.5
GAP = 9
x_in = (RACK_W - NODE_W) / 2

# frame: four posts, base and top plates
height = 22 + 4 * (NODE_H + GAP) + 26 + 14
for px in (0, RACK_W - POST):
    for py in (0, RACK_D - POST):
        box(px, py, 0, px + POST, py + POST, height)
box(0, 0, 0, RACK_W, RACK_D, 8)
box(0, 0, height - 8, RACK_W, RACK_D, height)
# rack ears with screw tabs on the front posts
for i in range(9):
    z = 16 + i * (height - 32) / 8
    box(-4, -3, z, 0, 0, z + 4)
    box(RACK_W, -3, z, RACK_W + 4, 0, z + 4)

z = 14
for n in range(4):
    # shelf and node body
    box(POST, 6, z - 4, RACK_W - POST, RACK_D - 6, z)
    box(x_in, 8, z, x_in + NODE_W, 8 + NODE_D, z + NODE_H)
    fy = 8 - 1.6  # front face details, slightly proud of the chassis
    box(x_in + 10, fy, z + 12, x_in + 21, 8, z + 23)            # power button
    for k in range(2):                                           # USB-A ports
        box(x_in + 32 + k * 16, fy, z + 13, x_in + 44 + k * 16, 8, z + 18)
    box(x_in + 70, fy, z + 13, x_in + 76, 8, z + 19)             # USB-C
    for k in range(12):                                          # front vent fins
        vx = x_in + 96 + k * 6.5
        box(vx, fy, z + 6, vx + 3, 8, z + NODE_H - 6)
    z += NODE_H + GAP

# 8-port switch on the top shelf
box(POST, 6, z - 4, RACK_W - POST, RACK_D - 6, z)
box(x_in, 8, z, x_in + NODE_W, 8 + 120, z + 26)
for k in range(8):
    px = x_in + 18 + k * 18
    box(px, 6.4, z + 8, px + 13, 8, z + 19)

with open("homelab.stl", "w") as f:
    f.write("solid homelab\n")
    for (nx, ny, nz), a, b, c in tris:
        f.write(f"facet normal {nx} {ny} {nz}\nouter loop\n")
        for p in (a, b, c):
            f.write("vertex {:.1f} {:.1f} {:.1f}\n".format(*p))
        f.write("endloop\nendfacet\n")
    f.write("endsolid homelab\n")
print(len(tris), "triangles")
