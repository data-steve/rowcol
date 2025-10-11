#!/usr/bin/env bash
# RowCol MVP Recovery - CI Guard Script
# Prevents edits outside the MVP recovery lane

set -euo pipefail

echo "🔍 Checking for changes outside MVP recovery lane..."

# Get list of changed files
CHANGED=$(git diff --name-only origin/main...HEAD 2>/dev/null || git diff --name-only HEAD~1...HEAD 2>/dev/null || echo "")

if [ -z "$CHANGED" ]; then
    echo "✅ No changes detected"
    exit 0
fi

# Check if any changes are outside allowed paths
BLOCKED_CHANGES=$(echo "$CHANGED" | grep -v '^_clean/' | grep -v '^scripts/ci_guard.sh$' | grep -v '^README\.md$' || true)

if [ -n "$BLOCKED_CHANGES" ]; then
    echo "❌ Changes outside MVP recovery lane detected:"
    echo "$BLOCKED_CHANGES"
    echo ""
    echo "🚫 All changes must be within _clean/ directory during recovery"
    echo "📖 See _clean/mvp/recovery_build_plan.md for details"
    exit 1
fi

echo "✅ All changes are within MVP recovery lane"
exit 0
