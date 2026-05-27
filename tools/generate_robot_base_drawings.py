from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAD_DIR = ROOT / "cad"
CAD_DIR.mkdir(exist_ok=True)

SVG_PATH = CAD_DIR / "base_robo_assistente_conceito_01_topo.svg"
DXF_PATH = CAD_DIR / "base_robo_assistente_conceito_01_topo.dxf"
MD_PATH = CAD_DIR / "base_robo_assistente_conceito_01.md"


W = 420
H = 320
MOTOR_RAIL_X = 170
MOTOR_RAIL_W = 34
MOTOR_RAIL_H = 250
CASTER_W = 110
CASTER_H = 44
CASTER_Y = 135
ELECTRONICS_W = 180
ELECTRONICS_H = 150
TOTEM_W = 120
TOTEM_H = 100


def sx(x):
    return 500 + x


def sy(y):
    return 390 - y


def rect_svg(x, y, w, h, klass, label=None, label_dy=0):
    out = [
        f'<rect class="{klass}" x="{sx(x - w / 2):.1f}" y="{sy(y + h / 2):.1f}" '
        f'width="{w:.1f}" height="{h:.1f}" />'
    ]
    if label:
        out.append(f'<text class="label" x="{sx(x):.1f}" y="{sy(y) + label_dy:.1f}">{label}</text>')
    return "\n".join(out)


def circle_svg(x, y, r, klass, label=None):
    out = [f'<circle class="{klass}" cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="{r:.1f}" />']
    if label:
        out.append(f'<text class="hole-label" x="{sx(x + 8):.1f}" y="{sy(y - 5):.1f}">{label}</text>')
    return "\n".join(out)


holes = []
for x in (-185, 185):
    for y in (-115, 115):
        holes.append((x, y, 4, "M4"))
for x in (-35, 35):
    for y in (-135, 135):
        holes.append((x, y, 4, "M4"))
for x in (-45, 45):
    for y in (-35, 35):
        holes.append((x, y, 3, "M3"))


svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="780" viewBox="0 0 1000 780">
  <style>
    .title {{ font: 700 24px Arial; fill: #17202a; }}
    .note {{ font: 14px Arial; fill: #45515f; }}
    .dim {{ font: 13px Arial; fill: #17202a; }}
    .label {{ font: 700 12px Arial; fill: #17202a; text-anchor: middle; dominant-baseline: middle; }}
    .hole-label {{ font: 11px Arial; fill: #17202a; }}
    .deck {{ fill: #eef6ff; stroke: #1d4f7a; stroke-width: 2; }}
    .rail {{ fill: #dff3e6; stroke: #1d7a45; stroke-width: 1.5; }}
    .zone {{ fill: rgba(255, 224, 166, 0.55); stroke: #a56a00; stroke-width: 1.5; stroke-dasharray: 7 5; }}
    .totem {{ fill: rgba(198, 216, 255, 0.65); stroke: #4a65ad; stroke-width: 1.5; }}
    .hole {{ fill: white; stroke: #111; stroke-width: 1.3; }}
    .axis {{ stroke: #6b7785; stroke-width: 1; stroke-dasharray: 5 5; }}
    .dimline {{ stroke: #17202a; stroke-width: 1; marker-start: url(#arrow); marker-end: url(#arrow); }}
  </style>
  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 Z" fill="#17202a" />
    </marker>
  </defs>

  <text class="title" x="60" y="50">Base Robo Assistente IFSP - conceito 01</text>
  <text class="note" x="60" y="78">Vista superior em milimetros. Conceito inicial para locomocao em areas livres internas.</text>

  {rect_svg(0, 0, W, H, "deck")}
  {rect_svg(-MOTOR_RAIL_X, 0, MOTOR_RAIL_W, MOTOR_RAIL_H, "rail", "motor")}
  {rect_svg(MOTOR_RAIL_X, 0, MOTOR_RAIL_W, MOTOR_RAIL_H, "rail", "motor")}
  {rect_svg(0, CASTER_Y, CASTER_W, CASTER_H, "rail", "rodizio frontal")}
  {rect_svg(0, -CASTER_Y, CASTER_W, CASTER_H, "rail", "rodizio traseiro")}
  {rect_svg(0, 0, ELECTRONICS_W, ELECTRONICS_H, "zone", "bateria / eletronica", -58)}
  {rect_svg(0, 0, TOTEM_W, TOTEM_H, "totem", "fixacao torre", 0)}
  {"".join(circle_svg(x, y, r, "hole") for x, y, r, _ in holes)}

  <line class="axis" x1="{sx(-230)}" y1="{sy(0)}" x2="{sx(230)}" y2="{sy(0)}" />
  <line class="axis" x1="{sx(0)}" y1="{sy(-180)}" x2="{sx(0)}" y2="{sy(180)}" />

  <line class="dimline" x1="{sx(-W/2)}" y1="{sy(-205)}" x2="{sx(W/2)}" y2="{sy(-205)}" />
  <text class="dim" x="{sx(0)}" y="{sy(-225)}" text-anchor="middle">420 mm</text>
  <line class="dimline" x1="{sx(245)}" y1="{sy(-H/2)}" x2="{sx(245)}" y2="{sy(H/2)}" />
  <text class="dim" x="{sx(268)}" y="{sy(0)}" transform="rotate(-90 {sx(268)} {sy(0)})" text-anchor="middle">320 mm</text>

  <text class="note" x="60" y="145">Legenda</text>
  <rect class="rail" x="60" y="165" width="26" height="16" /><text class="note" x="96" y="178">suporte de motor ou rodizio</text>
  <rect class="zone" x="60" y="195" width="26" height="16" /><text class="note" x="96" y="208">area reservada para bateria e eletronica</text>
  <rect class="totem" x="60" y="225" width="26" height="16" /><text class="note" x="96" y="238">base de fixacao da torre/tela</text>
  <circle class="hole" cx="73" cy="263" r="4" /><text class="note" x="96" y="268">furos M4/M3 de referencia</text>

  <text class="note" x="60" y="720">Notas: furos M4 para trilhos/rodizios; furos M3 para placa/eletronica. Ajustar conforme motor, roda, bateria e altura final do totem.</text>
</svg>
"""


def dxf_line(x1, y1, x2, y2, layer="0"):
    return f"0\nLINE\n8\n{layer}\n10\n{x1:.3f}\n20\n{y1:.3f}\n30\n0\n11\n{x2:.3f}\n21\n{y2:.3f}\n31\n0\n"


def dxf_circle(x, y, r, layer="FUROS"):
    return f"0\nCIRCLE\n8\n{layer}\n10\n{x:.3f}\n20\n{y:.3f}\n30\n0\n40\n{r:.3f}\n"


def dxf_rect(x, y, w, h, layer):
    x0, x1 = x - w / 2, x + w / 2
    y0, y1 = y - h / 2, y + h / 2
    return (
        dxf_line(x0, y0, x1, y0, layer)
        + dxf_line(x1, y0, x1, y1, layer)
        + dxf_line(x1, y1, x0, y1, layer)
        + dxf_line(x0, y1, x0, y0, layer)
    )


dxf_entities = [
    dxf_rect(0, 0, W, H, "PLATAFORMA"),
    dxf_rect(-MOTOR_RAIL_X, 0, MOTOR_RAIL_W, MOTOR_RAIL_H, "TRILHOS_MOTOR"),
    dxf_rect(MOTOR_RAIL_X, 0, MOTOR_RAIL_W, MOTOR_RAIL_H, "TRILHOS_MOTOR"),
    dxf_rect(0, CASTER_Y, CASTER_W, CASTER_H, "RODIZIOS"),
    dxf_rect(0, -CASTER_Y, CASTER_W, CASTER_H, "RODIZIOS"),
    dxf_rect(0, 0, ELECTRONICS_W, ELECTRONICS_H, "ELETRONICA"),
    dxf_rect(0, 0, TOTEM_W, TOTEM_H, "TORRE"),
]
dxf_entities.extend(dxf_circle(x, y, r, "FUROS") for x, y, r, _ in holes)

dxf = "0\nSECTION\n2\nENTITIES\n" + "".join(dxf_entities) + "0\nENDSEC\n0\nEOF\n"


MD_PATH.write_text(
    """# Base Robo Assistente IFSP - conceito 01

Primeiro desenho mecanico conceitual da base movel do robo/totem.

## Medidas iniciais

- Plataforma: 420 x 320 mm.
- Espessura sugerida da chapa: 6 a 8 mm.
- Trilhos laterais para motores/rodas: 34 x 250 mm.
- Pads dianteiro e traseiro para rodizio: 110 x 44 mm.
- Area central para bateria/eletronica: 180 x 150 mm.
- Base da torre/tela: 120 x 100 mm.

## Arquivos

- `base_robo_assistente_conceito_01_topo.svg`: desenho visual com cotas.
- `base_robo_assistente_conceito_01_topo.dxf`: desenho 2D para importar como sketch no Onshape.
- `base_robo_assistente_conceito_01.stl`: volume conceitual 3D inicial.

## Proximas decisoes

- Escolher motor, roda e diametro dos rodizios.
- Medir bateria e computador/tela.
- Definir altura e peso da torre para avaliar estabilidade.
- Revisar largura para passar em corredores e portas com folga.
""",
    encoding="utf-8",
)

SVG_PATH.write_text(svg, encoding="utf-8")
DXF_PATH.write_text(dxf, encoding="utf-8")
print(SVG_PATH)
print(DXF_PATH)
print(MD_PATH)
