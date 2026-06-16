#!/bin/bash
# Usage: push_project.sh "<windows_path>" "<commit_message>"
# Called by Claude when user says "push to git"

WIN_PATH="$1"
COMMIT_MSG="$2"

if [ -z "$WIN_PATH" ] || [ -z "$COMMIT_MSG" ]; then
    echo "ERROR: Missing arguments."
    echo "Usage: push_project.sh <windows_path> <commit_message>"
    exit 1
fi

# Convert Windows path to WSL path (C:\foo -> /mnt/c/foo)
WSL_PATH=$(echo "$WIN_PATH" | sed 's|\\|/|g' | sed 's|^\([A-Za-z]\):|/mnt/\L\1|')

echo "=== Pushing: $WSL_PATH ==="
cd "$WSL_PATH" || { echo "ERROR: Cannot cd to $WSL_PATH"; exit 1; }

# Auto-update README.md timestamps before commit
TODAY=$(date "+%Y-%m-%d")
REPO_ROOT="$WSL_PATH"

# Update root README.md
if [ -f "$REPO_ROOT/README.md" ]; then
    sed -i "s|\*最後更新:.*|\*最後更新: $TODAY\*|g" "$REPO_ROOT/README.md"
fi

# Update work/README.md if it exists
if [ -f "$REPO_ROOT/work/README.md" ]; then
    sed -i "s|\*最後更新:.*|\*最後更新: $TODAY\*|g" "$REPO_ROOT/work/README.md"
fi

# Update lab/README.md if it exists
if [ -f "$REPO_ROOT/lab/README.md" ]; then
    sed -i "s|\*最後更新:.*|\*最後更新: $TODAY\*|g" "$REPO_ROOT/lab/README.md"
fi

git add .
git status --short

if git diff --cached --quiet; then
    echo "Nothing to commit."
else
    git commit -m "$COMMIT_MSG"
    git push
    echo "=== Push complete ==="
fi
