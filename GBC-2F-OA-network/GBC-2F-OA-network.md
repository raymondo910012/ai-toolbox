---
name: GBC-2F-OA-network
description: 普生二樓 OA 網路拓譜設定備份與快速恢復。包含 A/B/C 三台機櫃交換機的 VLAN 設定、Port 分配、Uplink 連線關係。當網路出問題時可用此 skill 快速恢復為正確設定。
---

# GBC-2F-OA-network

普生二樓 OA 網路架構與設定備份，用於網路故障時快速恢復。

## 網路拓譜

```
                    ┌─────────────────────────────┐
                    │        4F-MIS 機房           │
                    └──────────────┬──────────────┘
                                   │ 10G SFP+
                                   │
                    ┌──────────────┴──────────────┐
                    │  A 機櫃 - ECS5520-18X       │
                    │  10.100.203.220              │
                    │  (核心匯聚層, 18 port 10G)   │
                    ├─────────────┬───────────────┤
                    │ Eth1/16     │               │
                    │ Uplink      │               │
                    │ to 4F-MIS   │               │
                    ├─────────────┼───────────────┤
              Eth1/1│             │Eth1/2         │
                    └─────┬───────┴────┬──────────┘
                          │            │
                 10G SFP+ │            │ 10G SFP+
                          │            │
           ┌──────────────┴──┐   ┌─────┴──────────────┐
           │  B 機櫃 (54 port)│   │  C 機櫃 (54 port)  │
           │  10.100.203.221  │   │  10.100.203.222    │
           │  Uplink: Eth1/49 │   │  Uplink: Eth1/49   │
           └──────────────────┘   └────────────────────┘
```

## 設備資訊

| 項目 | A 機櫃 | B 機櫃 | C 機櫃 |
|------|--------|--------|--------|
| IP | 10.100.203.220 | 10.100.203.221 | 10.100.203.222 |
| 型號 | ECS5520-18X | 54 port GbE | 54 port GbE |
| 角色 | 核心匯聚層 | 接入層 | 接入層 |
| Port 速度 | 10G SFP+ (1-16), 40G QSFP (17-18) | 1G (1-48), 10G SFP+ (49-54) | 1G (1-48), 10G SFP+ (49-54) |
| 帳號/密碼 | admin / admin | admin / admin | admin / admin |
| Uplink Port | Eth1/16 (to 4F-MIS) | Eth1/49 (to A Eth1/1) | Eth1/49 (to A Eth1/2) |

## VLAN 設定

### VLAN 1 — DefaultVlan

| 機櫃 | Ports |
|------|-------|
| A | Eth1/3-18 |
| B | Eth1/1-16, 43-45, 48, 50-54 |
| C | Eth1/1-16, 46-48, 50-54 |

### VLAN 25 — IT_Admin

| 機櫃 | Ports |
|------|-------|
| A | Eth1/1, 2, 16 |
| B | Eth1/36-38, 49 |
| C | 未設定 |

### VLAN 51 — ACCWIFI

| 機櫃 | Ports |
|------|-------|
| A | Eth1/1, 2, 16 |
| B | Eth1/1-16, 49 |
| C | Eth1/1-16, 49 |

### VLAN 100 — ACCGUEST

| 機櫃 | Ports |
|------|-------|
| A | Eth1/1, 2, 16 |
| B | Eth1/1-16, 39-42, 49 |
| C | Eth1/1-16, 41-42, 49 |

### VLAN 119 — Maintenance

| 機櫃 | Ports |
|------|-------|
| A | Eth1/1, 2, 15, 16 |
| B | Eth1/35, 43(Access), 49 |
| C | 未設定 |

### VLAN 160 — Printer_DoorAccess

| 機櫃 | Ports |
|------|-------|
| A | Eth1/1, 2, 16 |
| B | Eth1/33-34, 46-47(Access), 49 |
| C | Eth1/33-40, 43-45, 49 |

### VLAN 168 — IPCAM

| 機櫃 | Ports |
|------|-------|
| A | Eth1/1, 2, 16 |
| B | Eth1/17-32, 49 |
| C | Eth1/17-32, 49 |

### VLAN 203 — MGMT

| 機櫃 | Ports |
|------|-------|
| A | Eth1/1, 2, 16 |
| B | Eth1/1-16, 49 |
| C | Eth1/1-16, 49 |

## Port 用途說明

### A 機櫃 (ECS5520-18X)
| Port | 名稱 | 用途 |
|------|------|------|
| Eth1/1 | Downlink_to_Cabinet-B_IT | 下行到 B 機櫃 (trunk) |
| Eth1/2 | Downlink_to_Cabinet-C_IT | 下行到 C 機櫃 (trunk) |
| Eth1/3 | LAG | (Link Down) |
| Eth1/15 | RJ45 | Maintenance 用 |
| Eth1/16 | Uplink_to_4F-MIS | 上行到 4F MIS 機房 (trunk) |
| Eth1/17-18 | 40G QSFP | (未使用) |

### B 機櫃 (54 port)
| Port 範圍 | VLAN | 用途 |
|-----------|------|------|
| Eth1/1-16 | 51, 100, 203 | AP / WiFi 接入 |
| Eth1/17-32 | 168 | IPCAM 攝影機 |
| Eth1/33-34 | 160 | Printer / 門禁 |
| Eth1/35 | 119 | Maintenance (Access) |
| Eth1/36-38 | 25 | IT Admin |
| Eth1/39-42 | 100 | ACCGUEST |
| Eth1/43 | 119 | Maintenance (Access) |
| Eth1/44-45 | 1 | DefaultVlan |
| Eth1/46-47 | 160 | Printer / 門禁 (Access) |
| Eth1/49 | trunk | Uplink to A 機櫃 |

### C 機櫃 (54 port)
| Port 範圍 | VLAN | 用途 |
|-----------|------|------|
| Eth1/1-16 | 51, 100, 203 | AP / WiFi 接入 |
| Eth1/17-32 | 168 | IPCAM 攝影機 |
| Eth1/33-40 | 160 | Printer / 門禁 |
| Eth1/41-42 | 100 | ACCGUEST |
| Eth1/43-45 | 160 | Printer / 門禁 |
| Eth1/49 | trunk | Uplink to A 機櫃 |

## 恢復指令語法

此設備使用以下 CLI 語法：

```
configure
vlan database
vlan <ID> name <NAME> media ethernet
end
copy running-config startup-config
```

## 恢復腳本

使用 `script/restore_config.py` 可自動恢復三台交換機的 VLAN 設定。

```bash
python3 script/restore_config.py [a|b|c|all]
```

## 注意事項

- SSH 連線需使用互動式 shell（paramiko invoke_shell），不支援 exec_command
- 設備有分頁顯示，需送 'a' 取得全部輸出
- 存檔指令 `copy running-config startup-config` 會提示檔名，直接按 Enter 確認
- B/C 機櫃的 Eth1/48 有 FCS Error（約 2000+），線路品質需注意
