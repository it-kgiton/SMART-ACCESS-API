#!/bin/bash
# Post-tool-use hook — Smart Access API
# Berjalan SETELAH setiap tool call Bash selesai dieksekusi
# Input: JSON via stdin dengan field "tool_name", "tool_input", "tool_output", "exit_code"

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null)
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null)
EXIT_CODE=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('exit_code',''))" 2>/dev/null)

# ── Log test results ───────────────────────────────────────────────────────────

if echo "$COMMAND" | grep -q "pytest"; then
    if [ "$EXIT_CODE" = "0" ]; then
        echo "✅ Tests passed." >&2
    else
        echo "❌ Tests failed. Review output di atas sebelum melanjutkan." >&2
    fi
fi

# ── Log deployment ─────────────────────────────────────────────────────────────

if echo "$COMMAND" | grep -q "railway up"; then
    if [ "$EXIT_CODE" = "0" ]; then
        echo "🚀 Deployment ke Railway berhasil." >&2
    else
        echo "❌ Deployment gagal. Cek logs: railway logs" >&2
    fi
fi

# ── Log docker ─────────────────────────────────────────────────────────────────

if echo "$COMMAND" | grep -q "docker-compose up\|docker compose up"; then
    if [ "$EXIT_CODE" = "0" ]; then
        echo "🐳 Docker services started. API: http://localhost:8000 | Docs: http://localhost:8000/docs" >&2
    fi
fi

exit 0
