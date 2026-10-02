---
name: configurar-perfil-argentino
description: >
  Entrevista de configuración del sistema claude-for-legal Argentina: recoge datos del
  abogado o estudio (matrícula, jurisdicción, fueros, firma, tasas, criterios de
  trabajo) y genera el perfil personalizado. Usar solo cuando el usuario pida
  configurar, actualizar o revisar su perfil de práctica argentino.
---

# Configurar el perfil del estudio

Skill del plugin `argentina-legal` (capa argentina de claude-for-legal). El
contenido operativo vive en archivos de referencia dentro del plugin; esta skill
indica cuáles leer.

## Dónde están los archivos

La raíz del plugin está dos niveles arriba de este archivo (`../../`, equivale a
`${CLAUDE_PLUGIN_ROOT}`). Todas las rutas `argentina/...` de esta skill y de los
perfiles son relativas a esa raíz.

**Leer completo antes de responder:**

- `argentina/setup-interview.md`
- `argentina/setup-output-TEMPLATE.md`

**Leer cuando la tarea lo requiera:**

- `argentina/legal.local.md.template` - plantilla de datos del estudio

## Dónde queda el perfil

El plugin es público y de solo lectura: el perfil generado no se guarda dentro
de el. Entregarlo al usuario y sugerirle guardarlo en sus preferencias o
instrucciones personales de Claude, en las instrucciones de un Project, o como
una skill personal. Nunca proponer subirlo al repositorio.

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
