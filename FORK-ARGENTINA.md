# Usar este fork como plugin en Claude

La carpeta `argentina/` no es un plugin: Claude no la carga sola. Este fork la
empaqueta como el plugin `argentina-legal` (22 skills: perfil base, una por
área, diagnóstico de escritos, plazos, bucle de fundamentación y configuración).

## Qué agrega este fork

| Archivo | Para qué |
|---|---|
| `scripts/build_argentina_plugin.py` | Genera `argentina-legal/` a partir de `argentina/` y lo registra en el marketplace |
| `.github/workflows/argentina-plugin.yml` | Todos los días trae los cambios de Probanza-ar, regenera el plugin y sube la versión |
| `argentina-legal/` | El plugin generado. No se edita a mano |
| `.claude-plugin/marketplace.json` | Suma `argentina-legal` y renombra el marketplace a `claude-for-legal-argentina` (el nombre `claude-for-legal` está reservado para Anthropic) |

## Puesta en marcha

1. En GitHub, pestaña **Actions** del fork: habilitar los workflows (en los forks
   vienen apagados).
2. Correr una vez **Plugin argentina-legal → Run workflow** (si `argentina-legal/`
   ya está en el repo, este paso solo verifica).
3. En Claude: **Personalizar → Plugins → Agregar → Agregar marketplace → Agregar
   desde un repositorio** → `<tu-usuario>/claude-for-legal-argentina`.
4. Instalar **Argentina Legal** y activar **Sincronizar automáticamente**.

## Para tener en cuenta

- Los cambios de contenido se hacen en `argentina/`. El workflow regenera el plugin.
- No subir `legal.local.md` ni escritos de clientes si el fork es público. Los datos
  del estudio van en las preferencias de Claude o se generan con la skill
  `configurar-perfil-argentino`.
- Si el merge con Probanza-ar tiene conflictos, el workflow lo aborta, deja `main`
  intacto y abre un issue.
