#!/bin/bash
# claude-sync-push.sh — Copia memórias Claude local → repositório git
# Executado automaticamente pelo hook pre-commit

set -e

PROJECT_PATH=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
CLAUDE_HASH=$(echo "$PROJECT_PATH" | tr '/_' '--')
CLAUDE_MEMORY_DIR="$HOME/.claude/projects/$CLAUDE_HASH/memory"

REPO_MEMORY_DIR="$PROJECT_PATH/.claude/memory"

mkdir -p "$REPO_MEMORY_DIR"

COPIED=0

if [ -d "$CLAUDE_MEMORY_DIR" ]; then
    for f in "$CLAUDE_MEMORY_DIR"/*.md; do
        [ -f "$f" ] || continue
        cp "$f" "$REPO_MEMORY_DIR/"
        COPIED=$((COPIED + 1))
    done
fi

echo "✅ claude-sync-push: $COPIED arquivo(s) copiado(s) para o repositório"
