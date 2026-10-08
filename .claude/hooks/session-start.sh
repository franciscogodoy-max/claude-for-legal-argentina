#!/bin/bash
set -euo pipefail

# Only run in Claude Code cloud sessions
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# markitdown: converts PDF/DOCX/XLSX/PPTX to Markdown
if ! command -v markitdown >/dev/null 2>&1; then
  pip install --quiet "markitdown[all]"
fi
