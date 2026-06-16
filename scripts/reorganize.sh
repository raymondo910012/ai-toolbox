#!/bin/bash
# Full ai-toolbox reorganization:
# - Move work projects into work/
# - Create lab/ with README.md
# - Create root README.md
# - Update push_project.sh with auto README update
# - Commit & push

REPO="/mnt/c/Projects/ai-toolbox"
cd "$REPO" || { echo "ERROR: cannot cd to $REPO"; exit 1; }

echo "=== Step 1: git mv work projects ==="
git mv GBC-2F-OA-network work/ 2>/dev/null || echo "  (already moved or not found)"
git mv ppt_create work/          2>/dev/null || echo "  (already moved or not found)"
git mv pptx work/                2>/dev/null || echo "  (already moved or not found)"
git mv skill-auto-sync work/     2>/dev/null || echo "  (already moved or not found)"
git mv README.md work/README.md  2>/dev/null || echo "  (already moved or not found)"

git status --short | grep "^R"

echo ""
echo "=== Step 2: Create lab/README.md ==="
cat > lab/README.md << 'LABREADME'
# 🧪 Lab — Ray 的個人實驗室

這裡放我平常在工作以外，因為興趣或學習動機做的專案。
不一定有實用目的，但都是我在探索、嘗試的東西。

## 結構

每個專案放在獨立子資料夾，包含：
- `README.md` — 簡單說明這個專案是什麼
- `script/` 或 `src/` — 程式碼
- 其他相關設定

## 專案清單

> 目前沒有專案，等你建立第一個！

---
*最後更新: 2026-06-16*
LABREADME
git add lab/README.md
echo "  lab/README.md created"

echo ""
echo "=== Step 3: Create root README.md ==="
cat > README.md << 'ROOTREADME'
# ai-toolbox

Ray 的 AI 工具與腳本集合，分為兩個主要區域：

## 📁 work/ — 工作專案

公司 IT 相關的自動化工具、網路管理腳本、簡報生成等。

| 專案 | 說明 |
|------|------|
| `GBC-2F-OA-network/` | 普生二樓 OA 網路拓譜設定備份與快速恢復 |
| `ppt_create/` | EC (Edgecore) 模板 PPT 自動生成 |
| `pptx/` | python-pptx 操作 skill |
| `skill-auto-sync/` | 每日自動 sync skills 到 GitHub |

## 🧪 lab/ — 個人實驗室

工作以外，因興趣或學習所做的探索性專案。

## 🛠️ scripts/ — 推送工具

Claude 自動推送用的 WSL 腳本（不含業務邏輯）。

---
*最後更新: 2026-06-16*
ROOTREADME
git add README.md
echo "  root README.md created"

echo ""
echo "=== Step 4: Commit & push ==="
git add -A
git status --short

git commit -m "refactor: reorganize into work/ and lab/ folders, add READMEs"
git push

echo ""
echo "=== Done ==="
