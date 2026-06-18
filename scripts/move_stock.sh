#!/bin/bash
export GIT_DISCOVERY_ACROSS_FILESYSTEM=1

SRC="/mnt/c/Users/USER/Claude/Projects/股票分析"
DST="/mnt/c/Projects/stock-analysis"
GITHUB_USER="raymondo910012"
REPO_NAME="stock-analysis"

# ── Step 1: Copy files (skip old .git) ───────────────────────────────
echo "=== Step 1: Copy files to $DST ==="
mkdir -p "$DST"
rsync -av --exclude='.git' --exclude='git_push' --exclude='commit_msg' "$SRC/" "$DST/"
echo ""

# ── Step 2: Create GitHub repo via API ───────────────────────────────
echo "=== Step 2: Create GitHub repo ==="
PAT=$(grep -oP 'ghp_[^@]+' ~/.git-credentials 2>/dev/null | head -1)
if [ -z "$PAT" ]; then
    echo "ERROR: PAT not found in ~/.git-credentials"
    exit 1
fi

HTTP=$(curl -s -o /tmp/gh_resp.json -w "%{http_code}" \
    -X POST \
    -H "Authorization: token $PAT" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$REPO_NAME\",\"description\":\"台股市場分析工具與資料\",\"private\":false}" \
    https://api.github.com/user/repos)

echo "HTTP Status: $HTTP"
grep -E '"full_name"|"html_url"|"message"' /tmp/gh_resp.json
echo ""

# ── Step 3: git init + first commit + push ───────────────────────────
echo "=== Step 3: Git init & push ==="
cd "$DST" || { echo "ERROR: cannot cd to $DST"; exit 1; }

git init
git config user.name "raymondo910012"
git config user.email "raymondo910012@gmail.com"
git add .
git status --short
git commit -m "feat: initial commit - 台股分析工具移轉"
git branch -M main
git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
git push -u origin main

echo ""
echo "=== Done: https://github.com/$GITHUB_USER/$REPO_NAME ==="
