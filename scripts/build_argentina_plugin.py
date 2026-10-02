#!/usr/bin/env python3
"""Genera el plugin `argentina-legal/` a partir de la carpeta `argentina/`.

La carpeta `argentina/` es la fuente (la mantiene Probanza-ar). Este script la
empaqueta como plugin instalable desde Claude (Personalizar > Plugins > Agregar
marketplace), con una skill por area y por herramienta transversal.

Uso:  python3 scripts/build_argentina_plugin.py

Es idempotente: si el contenido no cambio, no toca nada. Si cambio, regenera
`argentina-legal/` y sube la version del plugin para que Claude detecte la
actualizacion. Lo corre el workflow `.github/workflows/argentina-plugin.yml`.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "argentina"
PLUGIN = ROOT / "argentina-legal"
REF = PLUGIN / "argentina"  # espejo de argentina/: las rutas internas "argentina/..." resuelven desde la raiz del plugin
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
# "claude-for-legal" esta reservado para el marketplace oficial de Anthropic: un
# fork que lo conserve no se puede agregar. Se renombra en cada build.
MARKETPLACE_NAME = "claude-for-legal-argentina"

PLUGIN_NAME = "argentina-legal"
PLUGIN_DESC = (
    "Capa argentina de claude-for-legal: perfiles de práctica por fuero (civil, "
    "comercial, concursos, societario, contratos, laboral, familia, penal, "
    "previsional, administrativo, tributario, consumidor, protección de datos y "
    "más), diagnóstico previo de escritos, cómputo de plazos procesales, bucle de "
    "fundamentación y modelos de escritos bajo derecho argentino."
)
AUTHOR = {"name": "Probanza-ar / comunidad claude-for-legal-argentina"}

# Archivos de argentina/ que no viajan en el plugin.
EXCLUDE_NAMES = {
    "CHANGELOG.md",                     # historial, no operativo
    "legal.local.md",                   # datos privados del estudio: nunca al repo publico
    "legal.local.template.md",          # duplicado de legal.local.md.template
    "diagnostico-casos-prueba.md",      # casos de prueba del skill
    "administrativo-_PROVINCIA_-CLAUDE",  # archivo vacio sin extension
}
EXCLUDE_DIRS = {"evals"}

# argentina/ trae CLAUDE.md y claude.md (colisionan en Windows/macOS). claude.md
# es la version vigente (ruteo completo, repo Probanza-ar); si desaparece se usa CLAUDE.md.
CORE_CANDIDATES = ["claude.md", "CLAUDE.md"]

COMMON_RULES = """\
## Reglas comunes

- **Perfil base.** Las reglas de citación, de hechos, de avance bajo reserva y de
  diagnóstico previo del perfil base (`argentina/CLAUDE.md`) rigen siempre. Si no
  están ya en contexto, leer esas secciones antes de producir el entregable.
- **Datos del estudio.** Las variables marcadas `[COMPLETAR]` o de "Configuración
  inicial" (matrícula, FUERO_HABITUAL, firma, tasa de interés, domicilio de
  notificación, etc.) no viven en el plugin porque el repositorio es público.
  Tomarlas de las preferencias y la memoria del usuario, o de un `legal.local.md`
  que aporte. Si falta un dato necesario, preguntarlo; no suponerlo. Ignorar las
  instrucciones de "primera vez / corré la entrevista" de los perfiles salvo que
  el usuario pida configurar (skill `configurar-perfil-argentino`).
- **Fuentes.** Verificar normas, vigencia y jurisprudencia con los conectores de
  fuentes argentinas disponibles (hub mcp-legal-ar: InfoLEG, SAIJ, BORA, JUBA,
  JusCABA, SCBA, PTN, TFN, etc.) según el ruteo de `argentina/fuentes.md`. Lo que
  no se pueda verificar lleva el marcador que corresponda según
  `argentina/marcadores-GLOSARIO.md`.
- **Borrador.** Todo entregable es un borrador para revisión del abogado.
"""

# name, titulo, description (disparo), leer siempre, leer segun la tarea [(ruta, para que)]
SKILLS: list[dict] = [
    {
        "name": "derecho-argentino-base",
        "title": "Perfil base · Derecho argentino",
        "description": (
            "Perfil base para cualquier trabajo jurídico bajo derecho argentino: reglas de "
            "citación e inmodificables, jurisdicción y fueros (CABA nacional, PBA, federal), "
            "normativa de referencia por área, alertas de normas inestables (tasas, cambiaria, "
            "DNU 70/2023), revisión de contratos y ruteo al perfil de área que corresponda. "
            "Usar ante cualquier consulta, escrito, dictamen o revisión que involucre derecho, "
            "tribunales u organismos argentinos (CCCN, CPCCN, LGS, LCQ, LCT, etc.), aunque el "
            "usuario no nombre un área."
        ),
        "always": ["argentina/CLAUDE.md"],
        "optional": [
            ("argentina/fuentes.md", "ruteo de cada pieza a su fuente y verificación de vigencia"),
            ("argentina/marcadores-GLOSARIO.md", "marcadores de verificación y cierre"),
        ],
        "extra": """\
## Ruteo a perfiles de área

Además de este perfil, usar la skill del área que corresponda: `civil`,
`concursos-quiebras`, `societario`, `contratos`, `consumidor`, `laboral`,
`familia`, `penal`, `previsional`, `administrativo`, `tributario`,
`proteccion-datos`, `discapacidad`, `transito`, `notarial`, `medicina-legal`,
`violencia-digital`. Herramientas transversales: `diagnostico-escritos`,
`plazos-procesales`, `bucle-fundamentacion`.
""",
    },
    {
        "name": "diagnostico-escritos",
        "title": "Diagnóstico previo de escritos",
        "description": (
            "Diagnóstico previo de un escrito jurídico argentino aportado (demanda, contestación, "
            "recurso, alegato, dictamen, memo, contrato) antes de modificarlo, corregirlo, "
            "ampliarlo o usarlo como base: detecta argumentos sin norma de respaldo, hechos no "
            "acreditados, citas no verificadas, peticiones sin fundamento, contradicciones "
            "internas y normas pendientes de verificación, y espera instruccion antes de tocar "
            "el texto. Usar siempre que el usuario aporte un escrito y pida revisarlo, "
            "corregirlo, mejorarlo, adaptarlo o responderlo."
        ),
        "always": ["argentina/diagnostico-SKILL.md"],
        "optional": [
            ("argentina/marcadores-GLOSARIO.md", "marcadores del bloque de diagnostico"),
            ("argentina/fuentes.md", "para verificar las citas detectadas"),
        ],
    },
    {
        "name": "plazos-procesales",
        "title": "Cómputo de plazos procesales · Derecho argentino",
        "description": (
            "Computa plazos procesales y administrativos bajo derecho argentino: días hábiles "
            "judiciales y administrativos, corridos, en horas, meses y años, ferias, "
            "suspensiones por mediacion y SECLO, plazo de gracia, y emite alerta de plazo fatal. "
            "Usar ante cualquier consulta por vencimiento de plazo, traslado, recurso, "
            "notificación, prescripción o caducidad en causa judicial o administrativa "
            "argentina. No usar para plazos ante ARCA/AFIP, ANSES o recaudadores provinciales."
        ),
        "always": ["argentina/plazos-SKILL.md"],
        "optional": [("argentina/marcadores-GLOSARIO.md", "marcador A10 y demás alertas")],
    },
    {
        "name": "bucle-fundamentacion",
        "title": "Bucle de fundamentación de escritos de fondo",
        "description": (
            "Arma o fundamenta desde cero un escrito de fondo bajo derecho argentino (demanda, "
            "contestación, recurso, expresión de agravios, alegato, verificación de crédito) "
            "como un bucle con criterio de salida verificable: hechos, prueba, derecho, "
            "jurisprudencia y petitorio anclados en fuente verificada, con control previo de "
            "plazo, competencia y agotamiento de vía. Usar cuando el usuario pide redactar o "
            "fundamentar un escrito nuevo (no cuando aporta uno ya hecho: ahi va diagnostico)."
        ),
        "always": [
            "argentina/bucles-SKILL.md",
            "argentina/fuentes.md",
            "argentina/marcadores-GLOSARIO.md",
        ],
        "optional": [],
    },
    {
        "name": "civil",
        "title": "Perfil civil · Daños y responsabilidad civil",
        "description": (
            "Práctica civil bajo derecho argentino: daños y perjuicios, responsabilidad civil "
            "contractual y extracontractual, accidentes de tránsito, mala praxis, obligaciones, "
            "contratos civiles, prescripción civil, cuantificación de daños e intereses, fuero "
            "Nacional Civil. Usar ante consultas, estrategia o redacción de escritos civiles, "
            "incluidas demandas de daños aunque no se nombre el modelo."
        ),
        "always": ["argentina/civil-CLAUDE.md"],
        "optional": [
            ("argentina/civil-DOCTRINA.md", "doctrina de referencia"),
            ("argentina/ejemplos-civil.md", "casos modelo y liquidaciones"),
            ("argentina/civil/escritos/escritos-civil-SKILL.md", "para redactar escritos civiles"),
            ("argentina/civil/escritos/modelos/", "modelos: tránsito, mala praxis, incumplimiento contractual"),
        ],
    },
    {
        "name": "concursos-quiebras",
        "title": "Perfil concursal · Concursos y quiebras",
        "description": (
            "Práctica concursal argentina (Ley 24.522, fuero Nacional Comercial y provinciales): "
            "concurso preventivo, quiebra, verificación tempestiva y tardía de creditos, "
            "revisión e incidentes, pronto pago, privilegios, APE, cramdown, informe individual "
            "y general de la sindicatura, extensión de quiebra y acciones de responsabilidad. "
            "Usar ante cualquier consulta o escrito en un concurso o quiebra."
        ),
        "always": ["argentina/concursos-CLAUDE.md"],
        "optional": [],
    },
    {
        "name": "societario",
        "title": "Perfil societario y M&A",
        "description": (
            "Derecho societario argentino y M&A: Ley General de Sociedades, IGJ y DPPJ, "
            "constitución y reformas, asambleas y directorio, actas, impugnación de decisiones "
            "asamblearias, designación e inscripción de autoridades, transferencia de acciones, "
            "pactos de accionistas, due diligence y operaciones de compraventa de empresas. "
            "Usar ante consultas, conflictos societarios o redacción de documentos societarios."
        ),
        "always": ["argentina/societario-CLAUDE.md"],
        "optional": [("argentina/ejemplos-societario.md", "casos modelo")],
    },
    {
        "name": "contratos",
        "title": "Perfil contratos · Revisión y redacción",
        "description": (
            "Revisión y redacción de contratos bajo derecho argentino (CCCN): NDA, servicios, "
            "suministro, compraventa, locacion, SaaS, mutuo, agencia, distribucion, "
            "fideicomiso, convenios marco. Aplica red-flags de nulidad y riesgo, cláusulas "
            "abusivas, indices y tasas de actualización. Usar cuando la tarea principal es un "
            "contrato, en cualquier área de práctica."
        ),
        "always": ["argentina/contratos/CLAUDE.md", "argentina/contratos/red-flags.md"],
        "optional": [("argentina/contratos/indices-y-tasas.md", "cláusulas de ajuste, indices y tasas")],
    },
    {
        "name": "consumidor",
        "title": "Perfil derecho del consumidor",
        "description": (
            "Derecho del consumidor argentino (Ley 24.240, CCCN): relación de consumo, daño "
            "punitivo, garantía y producto defectuoso, prepagas y amparo de salud, bancos y "
            "servicios, reclamos ante Ventanilla Federal / OMIC, cartas documento e "
            "intimaciones al proveedor. Usar ante consultas o escritos de consumo, aunque no se "
            "nombre el modelo."
        ),
        "always": ["argentina/consumidor-CLAUDE.md"],
        "optional": [
            ("argentina/consumidor/escritos/escritos-consumidor-SKILL.md", "para redactar escritos de consumo"),
            ("argentina/consumidor/escritos/modelos/", "modelos: amparo prepaga, daño punitivo, garantía, OMIC, cartas documento"),
        ],
    },
    {
        "name": "laboral",
        "title": "Perfil laboral",
        "description": (
            "Derecho laboral argentino (LCT y reformas Ley 27.742 / 27.802, CCT, LRT): contrato "
            "de trabajo, despido, liquidación final, indemnizaciones, registración, accidentes y "
            "enfermedades, SECLO, telegramas y cartas documento laborales. Usar ante consultas, "
            "liquidaciones o escritos laborales, y ante cualquier pedido de telegrama o CD "
            "laboral aunque no se diga 'telegrama'."
        ),
        "always": ["argentina/laboral-CLAUDE.md"],
        "optional": [
            ("argentina/ejemplos-laboral.md", "liquidaciones modelo y checklist"),
            ("argentina/laboral/telegrama/telegramas-SKILL.md", "para redactar telegramas y CD"),
            ("argentina/laboral/telegrama/tipos-de-telegrama.md", "tipología de piezas postales"),
            ("argentina/laboral/telegrama/reglas-normativas.md", "verificación normativa post-reforma"),
            ("argentina/laboral/telegrama/modelos/", "modelos por bloque (registro, despido, salarios, etc.)"),
        ],
    },
    {
        "name": "familia",
        "title": "Perfil derecho de familia",
        "description": (
            "Derecho de familia argentino (CCCN libro II): divorcio y convenio regulador, "
            "alimentos, cuidado personal, régimen comunicacional, filiación, adopción, "
            "compensación económica, unión convivencial y violencia familiar. Usar ante "
            "consultas o escritos de familia, aunque no se nombre el modelo."
        ),
        "always": ["argentina/familia-CLAUDE.md"],
        "optional": [
            ("argentina/familia-DOCTRINA.md", "doctrina de referencia"),
            ("argentina/ejemplos-familia.md", "casos modelo"),
            ("argentina/familia/escritos/escritos-familia-SKILL.md", "para redactar escritos de familia"),
            ("argentina/familia/escritos/modelos/", "modelos: convenio regulador, alimentos, medidas de protección"),
        ],
    },
    {
        "name": "penal",
        "title": "Perfil penal",
        "description": (
            "Derecho penal y procesal penal argentino: defensa del imputado, querella, "
            "excarcelación y prisión preventiva, probation, hábeas corpus, nulidades, "
            "allanamientos, recurso de casación, medidas cautelares penales, delitos económicos "
            "y societarios. Usar ante consultas o escritos penales."
        ),
        "always": ["argentina/penal-CLAUDE.md"],
        "optional": [
            ("argentina/penal-DOCTRINA.md", "doctrina de referencia"),
            ("argentina/penal-APUNTES-DOCTRINA.md", "apuntes complementarios"),
            ("argentina/ejemplos-penal.md", "casos modelo"),
            ("argentina/penal/escritos/escritos-penal-SKILL.md", "para redactar escritos penales"),
            ("argentina/penal/escritos/modelos/", "modelos: excarcelación, probation, hábeas corpus, nulidad, casación"),
        ],
    },
    {
        "name": "previsional",
        "title": "Perfil previsional",
        "description": (
            "Derecho previsional argentino (SIPA, ANSES, Fuero Federal de la Seguridad Social): "
            "reajuste de haberes, haber inicial y movilidad, denegatorias de beneficio, "
            "jubilación, pensión y pensión derivada, retiro por invalidez, PUAM, moratorias. "
            "Usar ante consultas, liquidaciones o escritos previsionales."
        ),
        "always": ["argentina/previsional-CLAUDE.md"],
        "optional": [
            ("argentina/ejemplos-previsional.md", "liquidaciones de reajuste"),
            ("argentina/previsional/escritos/escritos-previsional-SKILL.md", "para redactar escritos previsionales"),
            ("argentina/previsional/escritos/modelos/", "modelos: reajuste, denegatoria, pensión derivada"),
        ],
    },
    {
        "name": "administrativo",
        "title": "Perfil derecho administrativo",
        "description": (
            "Derecho administrativo argentino nacional, CABA, PBA y provincias: procedimiento "
            "administrativo (LNPA, Dec. 1510/97, Dec-Ley 7647/70), recursos y agotamiento de "
            "vía, contencioso administrativo, amparo contra el Estado, responsabilidad del "
            "Estado, contratación pública, empleo público, sanciones y organismos de control. "
            "Usar ante consultas o escritos frente a la Administración."
        ),
        "always": ["argentina/administrativo-CLAUDE.md"],
        "optional": [
            ("argentina/administrativo/", "perfiles provinciales: leer solo el de la jurisdicción del caso (CABA, PBA, CORDOBA, SANTAFE, MENDOZA, etc.)"),
        ],
    },
    {
        "name": "tributario",
        "title": "Perfil tributario",
        "description": (
            "Derecho tributario argentino: ARCA (ex AFIP), procedimiento de la Ley 11.683, "
            "determinaciones de oficio, Tribunal Fiscal de la Nación, IVA, Ganancias, ingresos "
            "brutos y tributos provinciales, ejecuciones fiscales, régimen penal tributario. "
            "Usar ante consultas o escritos tributarios."
        ),
        "always": ["argentina/tributario-CLAUDE.md"],
        "optional": [],
    },
    {
        "name": "proteccion-datos",
        "title": "Perfil protección de datos personales",
        "description": (
            "Protección de datos personales en Argentina: Ley 25.326, hábeas data, derechos de "
            "acceso, rectificación y supresión, informes crediticios (Veraz, Nosis, BCRA), "
            "AAIP como autoridad de control, bases de datos, transferencias internacionales, "
            "usurpación de identidad y daños por tratamiento ilícito. Usar ante cualquier "
            "consulta o escrito sobre datos personales o hábeas data."
        ),
        "always": ["argentina/proteccion-datos-CLAUDE.md"],
        "optional": [],
    },
    {
        "name": "discapacidad",
        "title": "Perfil derecho de la discapacidad",
        "description": (
            "Derecho de la discapacidad argentino (Leyes 22.431 y 24.901, CUD): cobertura de "
            "prestaciones por obras sociales y prepagas, amparo de salud, acompañante "
            "terapéutico, reintegros, transporte y educación. Usar ante consultas o escritos "
            "sobre discapacidad."
        ),
        "always": ["argentina/discapacidad-CLAUDE.md"],
        "optional": [
            ("argentina/discapacidad-DOCTRINA.md", "doctrina de referencia"),
            ("argentina/ejemplos-discapacidad.md", "casos modelo: amparos, AT, reintegros"),
        ],
    },
    {
        "name": "transito",
        "title": "Perfil infracciones de tránsito",
        "description": (
            "Infracciones y multas de tránsito en Argentina (Ley 24.449, CABA, PBA y "
            "provincias): actas, fotomultas, cinemómetros, descargos, prescripción, denuncia "
            "de venta, apelación ante controlador o juez de faltas. Usar ante cualquier "
            "mención de multa o infraccion de tránsito, aunque no se diga 'descargo'."
        ),
        "always": ["argentina/transito-CLAUDE.md"],
        "optional": [
            ("argentina/transito/descargos/descargos-SKILL.md", "para redactar descargos y recursos"),
            ("argentina/transito/descargos/modelo-acapite-prescripcion-CABA.md", "acápite de prescripción CABA"),
            ("argentina/transito/descargos/modelos/", "modelos por causal"),
        ],
    },
    {
        "name": "notarial",
        "title": "Perfil derecho notarial",
        "description": (
            "Derecho notarial argentino: escrituras públicas, actas notariales, estudio de "
            "títulos, poderes, compraventas y donaciones inmobiliarias, registros de la "
            "propiedad (Ley 17.801), prevención de lavado (UIF) y cláusulas notariales. Usar "
            "ante consultas o redacción de documentos notariales."
        ),
        "always": ["argentina/especialidades/notarial/notarial-CLAUDE.md"],
        "optional": [
            ("argentina/especialidades/notarial/notarial-clausulas.md", "cláusulas modelo"),
            ("argentina/especialidades/notarial/notarial-_PROVINCIA_-CLAUDE.md", "plantilla para normativa de un colegio provincial"),
        ],
    },
    {
        "name": "medicina-legal",
        "title": "Perfil medicina legal",
        "description": (
            "Medicina legal aplicada a litigios argentinos: informes médico-legales y "
            "periciales, lesiones, incapacidad (baremos), imputabilidad, invalidez previsional, "
            "praxis médica, impugnación de pericias en fuero civil, penal, laboral y de la "
            "seguridad social. Usar ante consultas sobre pericias o cuestiones médico-legales."
        ),
        "always": ["argentina/especialidades/medicina-legal-CLAUDE.md"],
        "optional": [],
    },
    {
        "name": "violencia-digital",
        "title": "Perfil violencia digital",
        "description": (
            "Violencia digital en Argentina (Ley Olimpia y normativa concordante): difusión no "
            "consentida de imágenes íntimas, sextorsión, hostigamiento o acoso digital, "
            "usurpación de identidad digital, medidas de protección y remoción de contenidos. "
            "Usar ante consultas o escritos sobre violencia digital o telemática."
        ),
        "always": ["argentina/especialidades/violencia-digital-CLAUDE.md"],
        "optional": [],
    },
    {
        "name": "configurar-perfil-argentino",
        "title": "Configurar el perfil del estudio",
        "description": (
            "Entrevista de configuración del sistema claude-for-legal Argentina: recoge datos "
            "del abogado o estudio (matrícula, jurisdicción, fueros, firma, tasas, criterios de "
            "trabajo) y genera el perfil personalizado. Usar solo cuando el usuario pida "
            "configurar, actualizar o revisar su perfil de práctica argentino."
        ),
        "always": ["argentina/setup-interview.md", "argentina/setup-output-TEMPLATE.md"],
        "optional": [("argentina/legal.local.md.template", "plantilla de datos del estudio")],
        "extra": """\
## Dónde queda el perfil

El plugin es público y de solo lectura: el perfil generado no se guarda dentro
de el. Entregarlo al usuario y sugerirle guardarlo en sus preferencias o
instrucciones personales de Claude, en las instrucciones de un Project, o como
una skill personal. Nunca proponer subirlo al repositorio.
""",
    },
]


def find_core() -> Path:
    for name in CORE_CANDIDATES:
        p = SRC / name
        # En Windows/macOS ambos nombres apuntan al mismo archivo: verificar el nombre real.
        if p.exists() and name in {c.name for c in SRC.iterdir()}:
            return p
    sys.exit("No se encontro argentina/CLAUDE.md ni argentina/claude.md")


def copy_sources() -> None:
    REF.mkdir(parents=True)
    core = find_core()
    for path in sorted(SRC.rglob("*")):
        rel = path.relative_to(SRC)
        if any(part in EXCLUDE_DIRS or part.strip() != part for part in rel.parts):
            continue
        if path.is_dir() or path.name in EXCLUDE_NAMES:
            continue
        if rel.parent == Path(".") and path.name.lower() == "claude.md":
            continue  # el perfil base se copia una sola vez, abajo
        dest = REF / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
    shutil.copy2(core, REF / "CLAUDE.md")


def yaml_block(text: str, indent: str = "  ", width: int = 86) -> str:
    words, lines, line = text.split(), [], ""
    for w in words:
        if line and len(line) + 1 + len(w) > width:
            lines.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    if line:
        lines.append(line)
    return "\n".join(indent + l for l in lines)


def render_skill(s: dict) -> str:
    out = [
        "---",
        f"name: {s['name']}",
        "description: >",
        yaml_block(s["description"]),
        "---",
        "",
        f"# {s['title']}",
        "",
        "Skill del plugin `argentina-legal` (capa argentina de claude-for-legal). El",
        "contenido operativo vive en archivos de referencia dentro del plugin; esta skill",
        "indica cuáles leer.",
        "",
        "## Dónde están los archivos",
        "",
        "La raíz del plugin está dos niveles arriba de este archivo (`../../`, equivale a",
        "`${CLAUDE_PLUGIN_ROOT}`). Todas las rutas `argentina/...` de esta skill y de los",
        "perfiles son relativas a esa raíz.",
        "",
        "**Leer completo antes de responder:**",
        "",
    ]
    out += [f"- `{p}`" for p in s["always"]]
    if s["optional"]:
        out += ["", "**Leer cuando la tarea lo requiera:**", ""]
        out += [f"- `{p}` - {why}" for p, why in s["optional"]]
    out.append("")
    if s.get("extra"):
        out += [s["extra"].rstrip(), ""]
    out += [COMMON_RULES.rstrip(), ""]
    return "\n".join(out)


def check_paths() -> None:
    missing = []
    for s in SKILLS:
        for p in s["always"] + [p for p, _ in s["optional"]]:
            if not (PLUGIN / p).exists():
                missing.append(f"{s['name']}: {p}")
    if missing:
        sys.exit("Rutas inexistentes en el plugin generado:\n  " + "\n  ".join(missing))


def render_readme() -> str:
    rows = "\n".join(
        f"| `{s['name']}` | {s['title']} |" for s in SKILLS
    )
    return f"""# argentina-legal

Plugin generado automaticamente a partir de la carpeta `argentina/` del repo
(`scripts/build_argentina_plugin.py`). **No editar a mano:** los cambios se
hacen en `argentina/` y el workflow `argentina-plugin.yml` regenera esta carpeta.

## Instalacion

1. En Claude: Personalizar > Plugins > Agregar > Agregar marketplace > Agregar
   desde un repositorio, y escribir `<tu-usuario>/claude-for-legal-argentina`.
2. Instalar `argentina-legal` y activar "Sincronizar automáticamente".

Los datos del estudio (matricula, fueros, firma, tasas) no van en el repo:
se cargan en las preferencias de Claude o con la skill `configurar-perfil-argentino`.

## Skills

| Skill | Contenido |
|---|---|
{rows}
"""


def content_hash() -> str:
    h = hashlib.sha256()
    for p in sorted(PLUGIN.rglob("*")):
        if p.is_file() and p.name not in {"plugin.json", ".build-hash"}:
            h.update(str(p.relative_to(PLUGIN)).encode())
            h.update(p.read_bytes())
    return h.hexdigest()


def ensure_marketplace_entry(entry: dict) -> None:
    data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    data["name"] = MARKETPLACE_NAME
    plugins = data["plugins"]
    for i, p in enumerate(plugins):
        if p["name"] == entry["name"]:
            plugins[i] = entry
            break
    else:
        plugins.append(entry)
    MARKETPLACE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    old_hash, old_version = "", "1.0.0"
    if (PLUGIN / ".build-hash").exists():
        old_hash = (PLUGIN / ".build-hash").read_text().strip()
    pj = PLUGIN / ".claude-plugin" / "plugin.json"
    if pj.exists():
        old_version = json.loads(pj.read_text(encoding="utf-8")).get("version", old_version)

    if PLUGIN.exists():
        shutil.rmtree(PLUGIN)
    copy_sources()
    for s in SKILLS:
        d = PLUGIN / "skills" / s["name"]
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(render_skill(s), encoding="utf-8")
    (PLUGIN / "README.md").write_text(render_readme(), encoding="utf-8")
    check_paths()

    new_hash = content_hash()
    if new_hash == old_hash:
        version = old_version
    else:
        version = "1.0." + datetime.now(timezone.utc).strftime("%Y%m%d%H%M")
    (PLUGIN / ".build-hash").write_text(new_hash + "\n")
    pj.parent.mkdir(parents=True, exist_ok=True)
    manifest = {"name": PLUGIN_NAME, "version": version, "description": PLUGIN_DESC, "author": AUTHOR}
    pj.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    ensure_marketplace_entry({
        "name": PLUGIN_NAME,
        "displayName": "Argentina Legal",
        "source": f"./{PLUGIN_NAME}",
        "description": PLUGIN_DESC,
        "author": AUTHOR,
    })
    print(f"{PLUGIN_NAME} {version} ({'sin cambios' if new_hash == old_hash else 'actualizado'}), "
          f"{len(SKILLS)} skills")


if __name__ == "__main__":
    main()
