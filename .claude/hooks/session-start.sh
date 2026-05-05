#!/bin/bash
# Session-start hook — Smart Access API
# Berjalan saat sesi Claude Code dimulai

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔷 Smart Access API — Claude Code Session"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 Project: smart-access-api"
echo "🐍 Stack  : Python 3.11 + FastAPI + PostgreSQL"
echo "📅 Date   : $(date '+%Y-%m-%d %H:%M')"
echo ""

# Cek apakah .env ada
if [ ! -f ".env" ]; then
    echo "⚠️  WARNING: File .env tidak ditemukan!"
    echo "   Jalankan: cp .env.example .env dan isi nilai yang diperlukan."
    echo ""
fi

# Cek apakah venv aktif
if [ -z "$VIRTUAL_ENV" ]; then
    echo "ℹ️  Venv belum aktif. Tip: source .venv/bin/activate"
else
    echo "✅ Venv aktif: $VIRTUAL_ENV"
fi

# Cek apakah Docker running
if command -v docker &> /dev/null; then
    if docker ps &> /dev/null; then
        RUNNING=$(docker ps --format "{{.Names}}" | grep -i "smart-access\|postgres" | tr '\n' ', ')
        if [ -n "$RUNNING" ]; then
            echo "🐳 Docker containers aktif: $RUNNING"
        fi
    fi
fi

echo ""
echo "📖 CLAUDE.md dibaca otomatis."
echo "💡 Skills: api-design | database | testing | deployment"
echo "🤖 Agents: /code-reviewer | /test-runner | /explorer"
echo "⚡ Commands: /deploy | /review | /test"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
