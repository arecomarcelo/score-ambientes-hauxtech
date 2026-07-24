#!/bin/bash
# claude-sync-pull.sh — Copia memórias Claude do repositório → local
# Executado automaticamente pelo hook post-merge (após git pull)

set -e

PROJECT_PATH=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
CLAUDE_HASH=$(echo "$PROJECT_PATH" | tr '/_' '--')
CLAUDE_MEMORY_DIR="$HOME/.claude/projects/$CLAUDE_HASH/memory"

REPO_MEMORY_DIR="$PROJECT_PATH/.claude/memory"

mkdir -p "$CLAUDE_MEMORY_DIR"

COPIED=0

if [ -d "$REPO_MEMORY_DIR" ]; then
    for f in "$REPO_MEMORY_DIR"/*.md; do
        [ -f "$f" ] || continue
        cp "$f" "$CLAUDE_MEMORY_DIR/"
        COPIED=$((COPIED + 1))
    done
fi

echo "✅ claude-sync-pull: $COPIED arquivo(s) restaurado(s) para ~/.claude/"
