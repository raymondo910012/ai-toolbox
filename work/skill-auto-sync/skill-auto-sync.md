---
name: skill-auto-sync
description: 每天中午 12 點自動檢查 skills 資料夾是否有變更，若有則自動 commit 並 push 到 GitHub repo (raymondo910012/ai-toolbox)。
---

# skill-auto-sync

自動同步 skills 到 GitHub。

## 功能
- 每天中午 12:00 自動執行
- 檢查 `~/.kiro/skills/` 是否有新增或修改的檔案
- 若有變更，自動 commit + push 到 GitHub

## 設定
- GitHub Repo: `raymondo910012/ai-toolbox`
- Branch: `main`
- Crontab: `5 12 * * *`（12:05 執行，避免跟 daily_monitor 衝突）

## 手動執行
```bash
python3 ~/.kiro/skills/skill-auto-sync/script/auto_sync.py
```
