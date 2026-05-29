# ai-toolbox

Kiro CLI Skills 集合 — 自動化工具與網路管理腳本。

## Skills 列表

### GBC-2F-OA-network
📁 `GBC-2F-OA-network/`

普生二樓 OA 網路拓譜設定備份與快速恢復。包含 A/B/C 三台機櫃交換機的 VLAN 設定、Port 分配、Uplink 連線關係。當網路出問題時可用此 skill 快速恢復為正確設定。

**Scripts:**
- `GBC-2F-OA-network/script/check_traffic.py`
- `GBC-2F-OA-network/script/daily_monitor.py`
- `GBC-2F-OA-network/script/restore_config.py`

### create_ppt
📁 `ppt_create/`

使用 python-pptx 建立或修改 PPT 簡報。套用 EC (Edgecore) 模板背景，內容排版參考 Kiro_Introduction 風格。適用於需要產生投影片的場景。

**Scripts:**
- `ppt_create/script/create_ppt.py`

### skill-auto-sync
📁 `skill-auto-sync/`

每天中午 12 點自動檢查 skills 資料夾是否有變更，若有則自動 commit 並 push 到 GitHub repo (raymondo910012/ai-toolbox)。

**Scripts:**
- `skill-auto-sync/script/auto_sync.py`

## 排程 (Crontab)

| 時間 | 腳本 | 說明 |
|------|------|------|
| 每天 12:00 | `daily_monitor.py` | /usr/bin/python3 /home/ray_wang/.kiro/skills/GBC-2F-OA-network/script/daily_monitor.py |
| 每天 12:05 | `auto_sync.py` | /usr/bin/python3 /home/ray_wang/.kiro/skills/skill-auto-sync/script/auto_sync.py |

---
*最後更新: 2026-05-29 12:05*
