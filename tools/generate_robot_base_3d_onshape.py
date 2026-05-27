from math import cos, pi, sin
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "base_robo_assistente_conceito_02_onshape.stl"
NOTES = ROOT / "cad" / "base_robo_assistente_conceito_02_onshape.md"


def facet(a, b, c):
    return (
        "  facet normal 0 0 0\n"
        "    outer loop\n"
        f"      vertex {a[0]:.3f} {a[1]:.3f} {a[2]:.3f}\n"
        f"      vertex {b[0]:.3f} {b[1]:.3f} {b[2]:.3f}\n"
        f"      vertex {c[0]:.3f} {c[1]:.3f} {c[2]:.3f}\n"
        "    endloop\n"
        "  endfacet\n"
    )


def box(cx, cy, cz, sx, sy, sz):
    x0, x1 = cx - sx / 2, cx + sx / 2
    y0, y1 = cy - sy / 2, cy + sy / 2
    z0, z1 = cz - sz / 2, cz + sz / 2
    p = [
        (x0, y0, z0),
        (x1, y0, z0),
        (x1, y1, z0),
        (x0, y1, z0),
        (x0, y0, z1),
        (x1, y0, z1),
        (x1, y1, z1),
        (x0, y1, z1),
    ]
    faces = [
        (4, 5, 6, 7),
        (0, 3, 2, 1),
        (0, 1, 5, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (3, 0, 4, 7),
    ]
    out = []
    for a, b, c, d in faces:
        out.append(facet(p[a], p[b], p[c]))
        out.append(facet(p[a], p[c], p[d]))
    return "".join(out)


def cylinder(cx, cy, cz, radius, length, axis="x", segments=24):
    def p(theta, offset):
        u = radius * cos(theta)
        v = radius * sin(theta)
        if axis == "x":
            return (cx + offset, cy + u, cz + v)
        if axis == "y":
            return (cx + u, cy + offset, cz + v)
        return (cx + u, cy + v, cz + offset)

    a0 = -length / 2
    a1 = length / 2
    c0 = (cx + a0, cy, cz) if axis == "x" else (cx, cy + a0, cz) if axis == "y" else (cx, cy, cz + a0)
    c1 = (cx + a1, cy, cz) if axis == "x" else (cx, cy + a1, cz) if axis == "y" else (cx, cy, cz + a1)
    out = []
    for i in range(segments):
        t0 = 2 * pi * i / segments
        t1 = 2 * pi * (i + 1) / segments
        p00 = p(t0, a0)
        p01 = p(t1, a0)
        p10 = p(t0, a1)
        p11 = p(t1, a1)
        out.append(facet(p00, p10, p11))
        out.append(facet(p00, p11, p01))
        out.append(facet(c0, p01, p00))
        out.append(facet(c1, p10, p11))
    return "".join(out)


parts = [
    box(0, 0, 4, 420, 320, 8),
    box(-170, 0, 18, 34, 250, 20),
    box(170, 0, 18, 34, 250, 20),
    box(-150, 0, 38, 42, 80, 34),
    box(150, 0, 38, 42, 80, 34),
    cylinder(-224, 0, 56, 52, 24, "x"),
    cylinder(224, 0, 56, 52, 24, "x"),
    box(0, 135, 16, 110, 44, 16),
    box(0, -135, 16, 110, 44, 16),
    cylinder(0, 165, 32, 22, 18, "y"),
    cylinder(0, -165, 32, 22, 18, "y"),
    box(-35, -35, 34, 120, 70, 42),
    box(55, 45, 18, 95, 65, 6),
    box(0, 0, 28, 120, 100, 24),
    box(0, 0, 112, 70, 50, 160),
    box(0, 34, 220, 165, 16, 100),
]

OUT.write_text("solid robo_base_onshape\n" + "".join(parts) + "endsolid robo_base_onshape\n", encoding="utf-8")
NOTES.write_text(
    """# Base Robo Assistente IFSP - conceito 02 Onshape

Versao simplificada do modelo 3D para facilitar a traducao no Onshape.

Inclui plataforma, trilhos, motores, rodas laterais, rodizios, bateria, placa,
base de torre, coluna e tela de referencia. Esta versao nao substitui o desenho
parametrico final; ela serve para validar volume e proporcao dentro do Onshape.
""",
    encoding="utf-8",
)
print(OUT)
print(NOTES)
