from pathlib import Path


OUT = Path(__file__).resolve().parents[1] / "cad" / "base_robo_assistente_conceito_01.stl"


def tri(a, b, c):
    return f"""  facet normal 0 0 0
    outer loop
      vertex {a[0]:.3f} {a[1]:.3f} {a[2]:.3f}
      vertex {b[0]:.3f} {b[1]:.3f} {b[2]:.3f}
      vertex {c[0]:.3f} {c[1]:.3f} {c[2]:.3f}
    endloop
  endfacet
"""


def box(name, cx, cy, cz, sx, sy, sz):
    x0, x1 = cx - sx / 2, cx + sx / 2
    y0, y1 = cy - sy / 2, cy + sy / 2
    z0, z1 = cz - sz / 2, cz + sz / 2
    p = {
        "000": (x0, y0, z0),
        "100": (x1, y0, z0),
        "110": (x1, y1, z0),
        "010": (x0, y1, z0),
        "001": (x0, y0, z1),
        "101": (x1, y0, z1),
        "111": (x1, y1, z1),
        "011": (x0, y1, z1),
    }
    faces = [
        ("001", "101", "111", "011"),
        ("000", "010", "110", "100"),
        ("000", "100", "101", "001"),
        ("100", "110", "111", "101"),
        ("110", "010", "011", "111"),
        ("010", "000", "001", "011"),
    ]
    facets = [f"  // {name}\n"]
    for a, b, c, d in faces:
        facets.append(tri(p[a], p[b], p[c]))
        facets.append(tri(p[a], p[c], p[d]))
    return "".join(facets)


parts = [
    # Main low deck: enough space for battery, controller, sensors, and cable routing.
    box("main_deck_420x320x8", 0, 0, 4, 420, 320, 8),
    # Side wheel rails for differential-drive motor brackets.
    box("left_wheel_rail", -170, 0, 16, 34, 250, 24),
    box("right_wheel_rail", 170, 0, 16, 34, 250, 24),
    # Front/rear caster or free-wheel mounting pads.
    box("front_caster_pad", 0, 135, 14, 110, 44, 20),
    box("rear_caster_pad", 0, -135, 14, 110, 44, 20),
    # Central protected electronics/battery area.
    box("electronics_floor", 0, 0, 16, 180, 150, 16),
    # Totem/upper-body mounting plinth.
    box("totem_mount_plinth", 0, 0, 32, 120, 100, 16),
]

OUT.write_text("solid base_robo_assistente_ifsp\n" + "".join(parts) + "endsolid base_robo_assistente_ifsp\n")
print(OUT)
