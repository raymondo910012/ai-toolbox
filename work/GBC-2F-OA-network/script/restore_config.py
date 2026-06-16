#!/usr/bin/env python3
"""
GBC 2F OA Network - VLAN 設定恢復腳本
用途：當交換機設定遺失或錯誤時，快速恢復 VLAN 設定
使用：python3 restore_config.py [a|b|c|all]
"""

import paramiko
import time
import sys

# === 設備資訊 ===
SWITCHES = {
    'a': {'host': '10.100.203.220', 'name': 'A 機櫃 (ECS5520-18X)'},
    'b': {'host': '10.100.203.221', 'name': 'B 機櫃 (54 port)'},
    'c': {'host': '10.100.203.222', 'name': 'C 機櫃 (54 port)'},
}
USERNAME = 'admin'
PASSWORD = 'admin'

# === VLAN 設定 ===
# 格式: (vlan_id, name, {switch: [ports]})
VLAN_CONFIG = [
    (25, 'IT_Admin', {
        'a': ['Eth1/1', 'Eth1/2', 'Eth1/16'],
        'b': ['Eth1/36', 'Eth1/37', 'Eth1/38', 'Eth1/49'],
    }),
    (51, 'ACCWIFI', {
        'a': ['Eth1/1', 'Eth1/2', 'Eth1/16'],
        'b': ['Eth1/1', 'Eth1/2', 'Eth1/3', 'Eth1/4', 'Eth1/5', 'Eth1/6', 'Eth1/7', 'Eth1/8',
              'Eth1/9', 'Eth1/10', 'Eth1/11', 'Eth1/12', 'Eth1/13', 'Eth1/14', 'Eth1/15', 'Eth1/16', 'Eth1/49'],
        'c': ['Eth1/1', 'Eth1/2', 'Eth1/3', 'Eth1/4', 'Eth1/5', 'Eth1/6', 'Eth1/7', 'Eth1/8',
              'Eth1/9', 'Eth1/10', 'Eth1/11', 'Eth1/12', 'Eth1/13', 'Eth1/14', 'Eth1/15', 'Eth1/16', 'Eth1/49'],
    }),
    (100, 'ACCGUEST', {
        'a': ['Eth1/1', 'Eth1/2', 'Eth1/16'],
        'b': ['Eth1/1', 'Eth1/2', 'Eth1/3', 'Eth1/4', 'Eth1/5', 'Eth1/6', 'Eth1/7', 'Eth1/8',
              'Eth1/9', 'Eth1/10', 'Eth1/11', 'Eth1/12', 'Eth1/13', 'Eth1/14', 'Eth1/15', 'Eth1/16',
              'Eth1/39', 'Eth1/40', 'Eth1/41', 'Eth1/42', 'Eth1/49'],
        'c': ['Eth1/1', 'Eth1/2', 'Eth1/3', 'Eth1/4', 'Eth1/5', 'Eth1/6', 'Eth1/7', 'Eth1/8',
              'Eth1/9', 'Eth1/10', 'Eth1/11', 'Eth1/12', 'Eth1/13', 'Eth1/14', 'Eth1/15', 'Eth1/16',
              'Eth1/41', 'Eth1/42', 'Eth1/49'],
    }),
    (119, 'Maintenance', {
        'a': ['Eth1/1', 'Eth1/2', 'Eth1/15', 'Eth1/16'],
        'b': ['Eth1/35', 'Eth1/49'],
    }),
    (160, 'Printer_DoorAccess', {
        'a': ['Eth1/1', 'Eth1/2', 'Eth1/16'],
        'b': ['Eth1/33', 'Eth1/34', 'Eth1/49'],
        'c': ['Eth1/33', 'Eth1/34', 'Eth1/35', 'Eth1/36', 'Eth1/37', 'Eth1/38', 'Eth1/39', 'Eth1/40',
              'Eth1/43', 'Eth1/44', 'Eth1/45', 'Eth1/49'],
    }),
    (168, 'IPCAM', {
        'a': ['Eth1/1', 'Eth1/2', 'Eth1/16'],
        'b': ['Eth1/17', 'Eth1/18', 'Eth1/19', 'Eth1/20', 'Eth1/21', 'Eth1/22', 'Eth1/23', 'Eth1/24',
              'Eth1/25', 'Eth1/26', 'Eth1/27', 'Eth1/28', 'Eth1/29', 'Eth1/30', 'Eth1/31', 'Eth1/32', 'Eth1/49'],
        'c': ['Eth1/17', 'Eth1/18', 'Eth1/19', 'Eth1/20', 'Eth1/21', 'Eth1/22', 'Eth1/23', 'Eth1/24',
              'Eth1/25', 'Eth1/26', 'Eth1/27', 'Eth1/28', 'Eth1/29', 'Eth1/30', 'Eth1/31', 'Eth1/32', 'Eth1/49'],
    }),
    (203, 'MGMT', {
        'a': ['Eth1/1', 'Eth1/2', 'Eth1/16'],
        'b': ['Eth1/1', 'Eth1/2', 'Eth1/3', 'Eth1/4', 'Eth1/5', 'Eth1/6', 'Eth1/7', 'Eth1/8',
              'Eth1/9', 'Eth1/10', 'Eth1/11', 'Eth1/12', 'Eth1/13', 'Eth1/14', 'Eth1/15', 'Eth1/16', 'Eth1/49'],
        'c': ['Eth1/1', 'Eth1/2', 'Eth1/3', 'Eth1/4', 'Eth1/5', 'Eth1/6', 'Eth1/7', 'Eth1/8',
              'Eth1/9', 'Eth1/10', 'Eth1/11', 'Eth1/12', 'Eth1/13', 'Eth1/14', 'Eth1/15', 'Eth1/16', 'Eth1/49'],
    }),
]

# A 機櫃 Port 名稱
PORT_NAMES_A = {
    'Eth1/1': 'Downlink_to_Cabinet-B_IT',
    'Eth1/2': 'Downlink_to_Cabinet-C_IT',
    'Eth1/3': 'LAG',
    'Eth1/15': 'RJ45',
    'Eth1/16': 'Uplink_to_4F-MIS',
}


def send_cmd(shell, cmd, wait=1):
    shell.send(cmd + '\n')
    time.sleep(wait)
    output = ''
    while shell.recv_ready():
        output += shell.recv(65535).decode('utf-8', errors='ignore')
    return output


def connect(host):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=USERNAME, password=PASSWORD, timeout=10)
    shell = ssh.invoke_shell()
    time.sleep(2)
    while shell.recv_ready():
        shell.recv(65535)
    return ssh, shell


def restore_vlans(switch_key):
    info = SWITCHES[switch_key]
    print(f"\n{'='*60}")
    print(f"恢復 {info['name']} ({info['host']})")
    print(f"{'='*60}")

    try:
        ssh, shell = connect(info['host'])
    except Exception as e:
        print(f"  ❌ 連線失敗: {e}")
        return False

    # 進入 VLAN 設定模式
    send_cmd(shell, 'configure')
    send_cmd(shell, 'vlan database')

    # 建立/命名 VLAN
    for vlan_id, name, ports_map in VLAN_CONFIG:
        if switch_key in ports_map:
            result = send_cmd(shell, f'vlan {vlan_id} name {name} media ethernet')
            print(f"  ✅ VLAN {vlan_id} ({name}) - 已設定")

    send_cmd(shell, 'end')

    # 設定 port VLAN membership
    send_cmd(shell, 'configure')
    for vlan_id, name, ports_map in VLAN_CONFIG:
        if switch_key in ports_map:
            for port in ports_map[switch_key]:
                # 格式化 port 名稱 (Eth1/1 -> ethernet 1/1)
                port_num = port.replace('Eth', 'ethernet ')
                send_cmd(shell, f'interface {port_num}')
                send_cmd(shell, f'switchport allowed vlan add {vlan_id} tagged')
                send_cmd(shell, 'exit')

    send_cmd(shell, 'end')

    # 存檔
    print(f"  💾 儲存設定...")
    shell.send('copy running-config startup-config\n')
    time.sleep(2)
    output = ''
    while shell.recv_ready():
        output += shell.recv(65535).decode('utf-8', errors='ignore')
    shell.send('\n')  # confirm filename
    time.sleep(5)
    while shell.recv_ready():
        output += shell.recv(65535).decode('utf-8', errors='ignore')

    if 'Success' in output or 'completed' in output:
        print(f"  ✅ 設定已儲存")
    else:
        print(f"  ⚠️  儲存結果請確認")

    ssh.close()
    return True


def verify_switch(switch_key):
    """驗證交換機目前的 VLAN 設定"""
    info = SWITCHES[switch_key]
    print(f"\n{'='*60}")
    print(f"驗證 {info['name']} ({info['host']})")
    print(f"{'='*60}")

    try:
        ssh, shell = connect(info['host'])
    except Exception as e:
        print(f"  ❌ 連線失敗: {e}")
        return

    shell.send('show vlan\n')
    time.sleep(3)
    output = ''
    while shell.recv_ready():
        output += shell.recv(65535).decode('utf-8', errors='ignore')
    for _ in range(10):
        if 'Next page' in output[-200:] or '--- [' in output[-200:]:
            shell.send('a')
            time.sleep(2)
            while shell.recv_ready():
                output += shell.recv(65535).decode('utf-8', errors='ignore')
        else:
            break

    print(output)
    ssh.close()


def main():
    if len(sys.argv) < 2:
        print("用法: python3 restore_config.py [a|b|c|all|verify]")
        print("")
        print("  a       - 恢復 A 機櫃 (10.100.203.220)")
        print("  b       - 恢復 B 機櫃 (10.100.203.221)")
        print("  c       - 恢復 C 機櫃 (10.100.203.222)")
        print("  all     - 恢復全部三台")
        print("  verify  - 驗證目前設定")
        sys.exit(1)

    target = sys.argv[1].lower()

    if target == 'verify':
        for key in ['a', 'b', 'c']:
            verify_switch(key)
    elif target == 'all':
        for key in ['a', 'b', 'c']:
            restore_vlans(key)
    elif target in SWITCHES:
        restore_vlans(target)
    else:
        print(f"未知目標: {target}")
        sys.exit(1)


if __name__ == '__main__':
    main()
