---
name: civil
description: >
  Práctica civil bajo derecho argentino: daños y perjuicios, responsabilidad civil
  contractual y extracontractual, accidentes de tránsito, mala praxis, obligaciones,
  contratos civiles, prescripción civil, cuantificación de daños e intereses, fuero
  Nacional Civil. Usar ante consultas, estrategia o redacción de escritos civiles,
  incluidas demandas de daños aunque no se nombre el modelo.
---

# Perfil civil · Daños y responsabilidad civil

Skill del plugin `argentina-legal` (capa argentina de claude-for-legal). El
contenido operativo vive en archivos de referencia dentro del plugin; esta skill
indica cuáles leer.

## Dónde están los archivos

La raíz del plugin está dos niveles arriba de este archivo (`../../`, equivale a
`${CLAUDE_PLUGIN_ROOT}`). Todas las rutas `argentina/...` de esta skill y de los
perfiles son relativas a esa raíz.

**Leer completo antes de responder:**

- `argentina/civil-CLAUDE.md`

**Leer cuando la tarea lo requiera:**

- `argentina/civil-DOCTRINA.md` - doctrina de referencia
- `argentina/ejemplos-civil.md` - casos modelo y liquidaciones
- `argentina/civil/escritos/escritos-civil-SKILL.md` - para redactar escritos civiles
- `argentina/civil/escritos/modelos/` - modelos: tránsito, mala praxis, incumplimiento contractual

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
