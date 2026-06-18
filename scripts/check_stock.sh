#!/bin/bash
export GIT_DISCOVERY_ACROSS_FILESYSTEM=1

echo "=== List parent folder ==="
ls "/mnt/c/Users/USER/Claude/Projects/" 2>/dev/null || echo "Cannot access"

echo ""
echo "=== Try cd ==="
cd "/mnt/c/Users/USER/Claude/Projects/股票分析" 2>/dev/null && echo "cd OK: $(pwd)" || echo "cd FAILED"

echo ""
echo "=== Remote ==="
git -C "/mnt/c/Users/USER/Claude/Projects/股票分析" remote -v 2>/dev/null || echo "no remote"

echo ""
echo "=== Log ==="
git -C "/mnt/c/Users/USER/Claude/Projects/股票分析" log --oneline -3 2>/dev/null || echo "(no commits yet)"
