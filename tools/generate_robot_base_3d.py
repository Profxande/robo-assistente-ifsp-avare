from math import cos, pi, sin
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAD_DIR = ROOT / "cad"
OUT = CAD_DIR / "base_robo_assistente_conceito_02_com_acessorios.stl"
NOTES = CAD_DIR / "base_robo_assistente_conceito_02_com_acessorios.md"


def facet(a, b, c):
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
    out = [f"  // {name}\n"]
    for a, b, c, d in faces:
        out.append(facet(p[a], p[b], p[c]))
        out.append(facet(p[a], p[c], p[d]))
    return "".join(out)


def cylinder(name, cx, cy, cz, radius, length, axis="x", segments=48):
    def point(theta, offset):
        u = radius * cos(theta)
        v = radius * sin(theta)
        if axis == "x":
            return (cx + offset, cy + u, cz + v)
        if axis == "y":
            return (cx + u, cy + offset, cz + v)
        return (cx + u, cy + v, cz + offset)

    out = [f"  // {name}\n"]
    a0 = -length / 2
    a1 = length / 2
    c0 = (cx + a0, cy, cz) if axis == "x" else (cx, cy + a0, cz) if axis == "y" else (cx, cy, cz + a0)
    c1 = (cx + a1, cy, cz) if axis == "x" else (cx, cy + a1, cz) if axis == "y" else (cx, cy, cz + a1)

    for i in range(segments):
        t0 = 2 * pi * i / segments
        t1 = 2 * pi * (i + 1) / segments
        p00 = point(t0, a0)
        p01 = point(t1, a0)
        p10 = point(t0, a1)
        p11 = point(t1, a1)
        out.append(facet(p00, p10, p11))
        out.append(facet(p00, p11, p01))
        out.append(facet(c0, p01, p00))
        out.append(facet(c1, p10, p11))
    return "".join(out)


def rounded_post(name, x, y, z, height, radius=5):
    return cylinder(name, x, y, z + height / 2, radius, height, axis="z", segments=24)


parts = [
    box("deck_principal_420x320x8", 0, 0, 4, 420, 320, 8),
    box("reforco_lateral_esquerdo", -170, 0, 17, 34, 250, 18),
    box("reforco_lateral_direito", 170, 0, 17, 34, 250, 18),
    box("pad_rodizio_frontal", 0, 135, 14, 110, 44, 16),
    box("pad_rodizio_traseiro", 0, -135, 14, 110, 44, 16),
    box("motor_esquerdo", -152, 0, 35, 45, 80, 38),
    box("motor_direito", 152, 0, 35, 45, 80, 38),
    cylinder("roda_lateral_esquerda", -222, 0, 56, 54, 28, axis="x"),
    cylinder("roda_lateral_direita", 222, 0, 56, 54, 28, axis="x"),
    cylinder("eixo_esquerdo", -190, 0, 56, 6, 72, axis="x", segments=24),
    cylinder("eixo_direito", 190, 0, 56, 6, 72, axis="x", segments=24),
    cylinder("rodizio_frontal_roda", 0, 162, 31, 24, 20, axis="y", segments=32),
    cylinder("rodizio_traseiro_roda", 0, -162, 31, 24, 20, axis="y", segments=32),
    rounded_post("pino_giro_rodizio_frontal", 0, 135, 16, 30, 7),
    rounded_post("pino_giro_rodizio_traseiro", 0, -135, 16, 30, 7),
    box("bateria_12v_ou_powerbank", -25, -35, 35, 120, 70, 44),
    box("placa_controladora", 45, 45, 17, 95, 65, 5),
    box("raspberry_ou_mini_pc_referencia", 45, 45, 25, 65, 45, 10),
    box("hub_cabos", -70, 55, 20, 54, 35, 14),
    box("base_torre_tela", 0, 0, 21, 120, 100, 18),
    box("coluna_torre_referencia", 0, 0, 115, 78, 54, 170),
    box("placa_tela_referencia", 0, 32, 225, 170, 18, 105),
]

for x in (-45, 45):
    for y in (-35, 35):
        parts.append(rounded_post(f"espacador_torre_{x}_{y}", x, y, 30, 36, 4))

for x in (15, 75):
    for y in (20, 70):
        parts.append(rounded_post(f"espacador_eletronica_{x}_{y}", x, y, 10, 12, 3))

for x in (-185, 185):
    for y in (-115, 115):
        parts.append(cylinder(f"furo_referencia_m4_visual_{x}_{y}", x, y, 15, 5, 4, axis="z", segments=20))

CAD_DIR.mkdir(exist_ok=True)
OUT.write_text(
    "solid base_robo_assistente_conceito_02\n"
    + "".join(parts)
    + "endsolid base_robo_assistente_conceito_02\n",
    encoding="utf-8",
)
NOTES.write_text(
    """# Base Robo Assistente IFSP - conceito 02 com acessorios

Modelo 3D conceitual gerado a partir do desenho 2D da base.

## Elementos incluidos

- Plataforma principal de 420 x 320 x 8 mm.
- Trilhos/reforcos laterais.
- Dois motores laterais representados por blocos.
- Duas rodas laterais de 108 mm de diametro.
- Eixos de referencia.
- Rodizio frontal e rodizio traseiro.
- Area central com bateria/powerbank.
- Placa controladora e mini-PC de referencia.
- Hub/canaleta de cabos.
- Base da torre/tela.
- Coluna e tela representativas para estudo de estabilidade.

## Avisos

Este modelo ainda nao e uma peca final para fabricacao. Ele serve para validar proporcoes,
espaco livre, interferencias e posicao dos principais componentes. A proxima etapa e escolher
motor, roda, bateria e tela reais para substituir estes volumes de referencia.
""",
    encoding="utf-8",
)
print(OUT)
print(NOTES)
