#!/bin/bash
# Pre-tool-use hook — Smart Access API
# Berjalan SEBELUM setiap tool call Bash dieksekusi
# Input: JSON via stdin dengan field "tool_name" dan "tool_input"
# Output: exit 0 = izinkan, exit 1 = blokir (dengan pesan ke stderr)

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null)
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null)

# ── Blokir perintah berbahaya ──────────────────────────────────────────────────

# Blokir reset database di production
if echo "$COMMAND" | grep -q "reset.sql"; then
    if echo "$COMMAND" | grep -qiE "(production|prod|railway)"; then
        echo "🚨 BLOCKED: reset.sql dilarang dijalankan di lingkungan production!" >&2
        exit 1
    fi
fi

# Blokir force push
if echo "$COMMAND" | grep -q "git push --force\|git push -f"; then
    echo "🚨 BLOCKED: Force push dilarang. Gunakan --force-with-lease jika benar-benar diperlukan." >&2
    exit 1
fi

# Blokir hard reset yang menghapus commit
if echo "$COMMAND" | grep -qE "git reset --hard HEAD~[0-9]+"; then
    echo "🚨 BLOCKED: git reset --hard yang menghapus commit dilarang tanpa konfirmasi manual." >&2
    exit 1
fi

# Blokir penghapusan file .env
if echo "$COMMAND" | grep -qE "rm.*\.env$|rm.*\.env "; then
    echo "🚨 BLOCKED: Penghapusan file .env dilarang." >&2
    exit 1
fi

# Blokir DROP DATABASE / DROP SCHEMA
if echo "$COMMAND" | grep -qiE "DROP (DATABASE|SCHEMA)"; then
    echo "🚨 BLOCKED: DROP DATABASE/SCHEMA dilarang via tool. Jalankan manual jika perlu." >&2
    exit 1
fi

# ── Warning ────────────────────────────────────────────────────────────────────

# Warning untuk perintah yang mengubah database
if echo "$COMMAND" | grep -q "schema.sql\|seed.sql"; then
    echo "⚠️  INFO: Menjalankan SQL file yang memodifikasi skema database." >&2
fi

# Warning untuk docker-compose down -v (hapus volume)
if echo "$COMMAND" | grep -q "docker-compose down -v\|docker compose down -v"; then
    echo "⚠️  INFO: docker-compose down -v akan menghapus database lokal." >&2
fi

exit 0
