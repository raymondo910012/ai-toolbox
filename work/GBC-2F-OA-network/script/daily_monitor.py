#!/usr/bin/env python3
"""
GBC 2F OA Network - 每日 Port 狀態監控
每天早上執行，比對前一天的 port 狀態，回報變化。

用法: python3 daily_monitor.py
設定 crontab: 0 8 * * * python3 /home/ray_wang/.kiro/skills/GBC-2F-OA-network/script/daily_monitor.py

狀態檔存放: /tmp/gbc_port_status.json
報告檔存放: /tmp/gbc_daily_report.txt
"""

import paramiko
import time
import json
import os
import re
from datetime import datetime

SWITCHES = {
    'a': {'host': '10.100.203.220', 'name': 'A 機櫃'},
    'b': {'host': '10.100.203.221', 'name': 'B 機櫃'},
    'c': {'host': '10.100.203.222', 'name': 'C 機櫃'},
}

STATE_FILE = '/tmp/gbc_port_status.json'
REPORT_DIR = '/tmp/gbc_oa_daily_report'
REPORT_FILE = '/tmp/gbc_daily_report.txt'

# VLAN 25 (IT_Admin) 和 VLAN 119 (Maintenance) 的 port 常插拔，不告警
IGNORE_PORTS = {
    'a': ['Eth1/15'],
    'b': ['Eth1/35', 'Eth1/36', 'Eth1/37', 'Eth1/38'],
    'c': [],
}


def connect(host):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username='admin', password='admin', timeout=10)
    shell = ssh.invoke_shell()
    time.sleep(2)
    while shell.recv_ready():
        shell.recv(65535)
    return ssh, shell


def send_cmd(shell, cmd, wait=3):
    shell.send(cmd + '\n')
    time.sleep(wait)
    output = ''
    while shell.recv_ready():
        output += shell.recv(65535).decode('utf-8', errors='ignore')
    for _ in range(50):
        if 'Next page' in output[-200:] or '--- [' in output[-200:]:
            shell.send('a')
            time.sleep(2)
            while shell.recv_ready():
                output += shell.recv(65535).decode('utf-8', errors='ignore')
        else:
            break
    return output


def get_port_status(host):
    """取得所有 port 的 link status 和 error count"""
    ssh, shell = connect(host)
    raw = send_cmd(shell, 'show interfaces counters')

    # 也取得 link status
    raw_status = send_cmd(shell, 'show interfaces status')
    ssh.close()

    ports = {}
    # 解析 counters
    blocks = re.split(r'(Ethernet \d+/\s*\d+)', raw)
    for i in range(1, len(blocks), 2):
        port_name = blocks[i].strip().replace('Ethernet ', 'Eth')
        port_name = re.sub(r'\s+', '', port_name)
        data = blocks[i+1] if i+1 < len(blocks) else ''

        def val(pattern):
            m = re.search(r'(\d+)\s+' + pattern, data)
            return int(m.group(1)) if m else 0

        m_in = re.search(r'(\d+)\s+Octets Input\s*\n', data)
        m_out = re.search(r'(\d+)\s+Octets Output\s*\n', data)

        ports[port_name] = {
            'octets_in': int(m_in.group(1)) if m_in else 0,
            'octets_out': int(m_out.group(1)) if m_out else 0,
            'err_in': val(r'Error Input'),
            'fcs': val(r'FCS Errors'),
        }

    # 解析 link status
    for m in re.finditer(r'Information of (Eth \d+/\d+).*?Link Status\s+:\s+(\w+)', raw_status, re.DOTALL):
        port_name = m.group(1).replace(' ', '')
        link = m.group(2)
        if port_name in ports:
            ports[port_name]['link'] = link

    return ports


def load_previous():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return None


def save_current(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def compare(prev, curr, switch_name):
    """比對前後狀態，回傳變化清單"""
    changes = []
    prev_ports = prev.get('ports', {})
    curr_ports = curr.get('ports', {})

    for port, cdata in curr_ports.items():
        pdata = prev_ports.get(port, {})

        # Link 狀態變化
        prev_link = pdata.get('link', 'Unknown')
        curr_link = cdata.get('link', 'Unknown')
        if prev_link != curr_link:
            changes.append(f"  🔄 {port}: Link {prev_link} → {curr_link}")

        # 新增 Error
        prev_fcs = pdata.get('fcs', 0)
        curr_fcs = cdata.get('fcs', 0)
        if curr_fcs > prev_fcs:
            changes.append(f"  ⚠️  {port}: FCS Error 增加 {curr_fcs - prev_fcs} (總計 {curr_fcs})")

        prev_err = pdata.get('err_in', 0)
        curr_err = cdata.get('err_in', 0)
        if curr_err > prev_err:
            changes.append(f"  ⚠️  {port}: Input Error 增加 {curr_err - prev_err} (總計 {curr_err})")

    return changes


def main():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    report = []
    report.append(f"{'='*60}")
    report.append(f" GBC 2F OA 每日監控報告")
    report.append(f" 時間: {now}")
    report.append(f"{'='*60}")

    previous = load_previous()
    current = {'timestamp': now, 'switches': {}}

    for key, info in SWITCHES.items():
        report.append(f"\n--- {info['name']} ({info['host']}) ---")
        ignore = IGNORE_PORTS.get(key, [])
        try:
            ports = get_port_status(info['host'])
            current['switches'][key] = {'ports': ports}

            if previous and key in previous.get('switches', {}):
                changes = compare(previous['switches'][key], current['switches'][key], info['name'])
                # 過濾掉 IT/Maintenance port 的 link 變化
                changes = [c for c in changes if not any(p in c and '🔄' in c for p in ignore)]
                if changes:
                    report.append(f"  ❗ 發現 {len(changes)} 項變化:")
                    report.extend(changes)
                else:
                    report.append(f"  ✅ 無變化，一切正常")
            else:
                report.append(f"  📝 首次記錄，已儲存基準狀態")

            # 顯示目前 link down 的 port（有歷史流量的，排除 IT/Maintenance）
            down_ports = [p for p, d in ports.items()
                         if d.get('link') == 'Down' and (d['octets_in'] > 0 or d['octets_out'] > 0)
                         and p not in ignore]
            if down_ports:
                report.append(f"  📴 目前 Link Down (曾有流量): {', '.join(sorted(down_ports))}")

        except Exception as e:
            report.append(f"  ❌ 連線失敗: {e}")
            if previous and key in previous.get('switches', {}):
                current['switches'][key] = previous['switches'][key]

    # 儲存目前狀態
    save_current(current)

    # 輸出報告
    report_text = '\n'.join(report)
    print(report_text)

    # 存到固定位置
    with open(REPORT_FILE, 'w') as f:
        f.write(report_text + '\n')

    # 存到日期資料夾
    os.makedirs(REPORT_DIR, exist_ok=True)
    date_str = datetime.now().strftime('%Y-%m-%d')
    dated_file = os.path.join(REPORT_DIR, f'report_{date_str}.txt')
    with open(dated_file, 'w') as f:
        f.write(report_text + '\n')

    print(f"\n📄 報告已存至: {dated_file}")
    print(f"💾 狀態已存至: {STATE_FILE}")


if __name__ == '__main__':
    main()
