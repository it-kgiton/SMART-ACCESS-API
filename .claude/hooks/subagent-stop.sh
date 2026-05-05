#!/bin/bash
# Subagent-stop hook — Smart Access API
# Berjalan saat subagent berhenti
# Input: JSON via stdin dengan field "agent_name", "exit_code", "summary"

INPUT=$(cat)
AGENT=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('agent_name','unknown'))" 2>/dev/null)
EXIT_CODE=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('exit_code','0'))" 2>/dev/null)

if [ "$EXIT_CODE" = "0" ]; then
    echo "✅ Subagent '$AGENT' selesai dengan sukses." >&2
else
    echo "❌ Subagent '$AGENT' berhenti dengan error (exit code: $EXIT_CODE)." >&2
    echo "   Periksa output subagent untuk detail." >&2
fi
