#!/bin/bash
# Stop hook — Smart Access API
# Berjalan saat Claude Code agent berhenti (normal stop)

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏁 Smart Access API — Session Ended"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Cek apakah ada uncommitted changes
if git rev-parse --is-inside-work-tree &>/dev/null; then
    CHANGED=$(git status --porcelain 2>/dev/null | wc -l)
    if [ "$CHANGED" -gt 0 ]; then
        echo "⚠️  Ada $CHANGED file dengan perubahan yang belum di-commit:"
        git status --short 2>/dev/null
        echo ""
        echo "   Jangan lupa: git add . && git commit -m 'your message'"
    else
        echo "✅ Working tree bersih — tidak ada perubahan yang belum di-commit."
    fi
fi

echo ""
echo "📅 Ended: $(date '+%Y-%m-%d %H:%M')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
