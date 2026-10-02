---
name: derecho-argentino-base
description: >
  Perfil base para cualquier trabajo jurídico bajo derecho argentino: reglas de citación
  e inmodificables, jurisdicción y fueros (CABA nacional, PBA, federal), normativa de
  referencia por área, alertas de normas inestables (tasas, cambiaria, DNU 70/2023),
  revisión de contratos y ruteo al perfil de área que corresponda. Usar ante cualquier
  consulta, escrito, dictamen o revisión que involucre derecho, tribunales u organismos
  argentinos (CCCN, CPCCN, LGS, LCQ, LCT, etc.), aunque el usuario no nombre un área.
---

# Perfil base · Derecho argentino

Skill del plugin `argentina-legal` (capa argentina de claude-for-legal). El
contenido operativo vive en archivos de referencia dentro del plugin; esta skill
indica cuáles leer.

## Dónde están los archivos

La raíz del plugin está dos niveles arriba de este archivo (`../../`, equivale a
`${CLAUDE_PLUGIN_ROOT}`). Todas las rutas `argentina/...` de esta skill y de los
perfiles son relativas a esa raíz.

**Leer completo antes de responder:**

- `argentina/CLAUDE.md`

**Leer cuando la tarea lo requiera:**

- `argentina/fuentes.md` - ruteo de cada pieza a su fuente y verificación de vigencia
- `argentina/marcadores-GLOSARIO.md` - marcadores de verificación y cierre

## Ruteo a perfiles de área

Además de este perfil, usar la skill del área que corresponda: `civil`,
`concursos-quiebras`, `societario`, `contratos`, `consumidor`, `laboral`,
`familia`, `penal`, `previsional`, `administrativo`, `tributario`,
`proteccion-datos`, `discapacidad`, `transito`, `notarial`, `medicina-legal`,
`violencia-digital`. Herramientas transversales: `diagnostico-escritos`,
`plazos-procesales`, `bucle-fundamentacion`.

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
