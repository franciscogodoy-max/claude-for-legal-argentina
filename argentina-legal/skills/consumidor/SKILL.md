---
name: consumidor
description: >
  Derecho del consumidor argentino (Ley 24.240, CCCN): relación de consumo, daño
  punitivo, garantía y producto defectuoso, prepagas y amparo de salud, bancos y
  servicios, reclamos ante Ventanilla Federal / OMIC, cartas documento e intimaciones al
  proveedor. Usar ante consultas o escritos de consumo, aunque no se nombre el modelo.
---

# Perfil derecho del consumidor

Skill del plugin `argentina-legal` (capa argentina de claude-for-legal). El
contenido operativo vive en archivos de referencia dentro del plugin; esta skill
indica cuáles leer.

## Dónde están los archivos

La raíz del plugin está dos niveles arriba de este archivo (`../../`, equivale a
`${CLAUDE_PLUGIN_ROOT}`). Todas las rutas `argentina/...` de esta skill y de los
perfiles son relativas a esa raíz.

**Leer completo antes de responder:**

- `argentina/consumidor-CLAUDE.md`

**Leer cuando la tarea lo requiera:**

- `argentina/consumidor/escritos/escritos-consumidor-SKILL.md` - para redactar escritos de consumo
- `argentina/consumidor/escritos/modelos/` - modelos: amparo prepaga, daño punitivo, garantía, OMIC, cartas documento

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
