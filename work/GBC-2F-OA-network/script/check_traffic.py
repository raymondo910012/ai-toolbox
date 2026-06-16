#!/usr/bin/env python3
"""
GBC 2F OA Network - Port 流量/網速/Error 快速查詢
用法: python3 check_traffic.py [a|b|c|all]
"""

import paramiko
import time
import sys
import re

SWITCHES = {
    'a': {'host': '10.100.203.220', 'name': 'A 機櫃'},
    'b': {'host': '10.100.203.221', 'name': 'B 機櫃'},
    'c': {'host': '10.100.203.222', 'name': 'C 機櫃'},
}

# Port to VLAN mapping
VLAN_MAP = {
    'a': {
        'Eth1/1': ('25,51,100,119,160,168,203', 'Downlink_to_Cabinet-B'),
        'Eth1/2': ('25,51,100,119,160,168,203', 'Downlink_to_Cabinet-C'),
        'Eth1/3': ('1', 'DefaultVlan'),
        'Eth1/4': ('1', 'DefaultVlan'),
        'Eth1/5': ('1', 'DefaultVlan'),
        'Eth1/6': ('1', 'DefaultVlan'),
        'Eth1/7': ('1', 'DefaultVlan'),
        'Eth1/8': ('1', 'DefaultVlan'),
        'Eth1/9': ('1', 'DefaultVlan'),
        'Eth1/10': ('1', 'DefaultVlan'),
        'Eth1/11': ('1', 'DefaultVlan'),
        'Eth1/12': ('1', 'DefaultVlan'),
        'Eth1/13': ('1', 'DefaultVlan'),
        'Eth1/14': ('1', 'DefaultVlan'),
        'Eth1/15': ('1,119', 'DefaultVlan/Maintenance'),
        'Eth1/16': ('25,51,100,119,160,168,203', 'Uplink_to_4F-MIS'),
        'Eth1/17': ('1', 'DefaultVlan'),
        'Eth1/18': ('1', 'DefaultVlan'),
    },
    'b': {
        'Eth1/1': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/2': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/3': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/4': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/5': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/6': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/7': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/8': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/9': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/10': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/11': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/12': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/13': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/14': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/15': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/16': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/17': ('168', 'IPCAM'),
        'Eth1/18': ('168', 'IPCAM'),
        'Eth1/19': ('168', 'IPCAM'),
        'Eth1/20': ('168', 'IPCAM'),
        'Eth1/21': ('168', 'IPCAM'),
        'Eth1/22': ('168', 'IPCAM'),
        'Eth1/23': ('168', 'IPCAM'),
        'Eth1/24': ('168', 'IPCAM'),
        'Eth1/25': ('168', 'IPCAM'),
        'Eth1/26': ('168', 'IPCAM'),
        'Eth1/27': ('168', 'IPCAM'),
        'Eth1/28': ('168', 'IPCAM'),
        'Eth1/29': ('168', 'IPCAM'),
        'Eth1/30': ('168', 'IPCAM'),
        'Eth1/31': ('168', 'IPCAM'),
        'Eth1/32': ('168', 'IPCAM'),
        'Eth1/33': ('160', 'Printer_DoorAccess'),
        'Eth1/34': ('160', 'Printer_DoorAccess'),
        'Eth1/35': ('119', 'Maintenance'),
        'Eth1/36': ('25', 'IT_Admin'),
        'Eth1/37': ('25', 'IT_Admin'),
        'Eth1/38': ('25', 'IT_Admin'),
        'Eth1/39': ('100', 'ACCGUEST'),
        'Eth1/40': ('100', 'ACCGUEST'),
        'Eth1/41': ('100', 'ACCGUEST'),
        'Eth1/42': ('100', 'ACCGUEST'),
        'Eth1/43': ('1', 'DefaultVlan'),
        'Eth1/44': ('1', 'DefaultVlan'),
        'Eth1/45': ('1', 'DefaultVlan'),
        'Eth1/46': ('1', 'DefaultVlan'),
        'Eth1/47': ('1', 'DefaultVlan'),
        'Eth1/48': ('1', 'DefaultVlan'),
        'Eth1/49': ('trunk', 'Uplink to A 機櫃'),
        'Eth1/50': ('1', 'DefaultVlan'),
        'Eth1/51': ('1', 'DefaultVlan'),
        'Eth1/52': ('1', 'DefaultVlan'),
        'Eth1/53': ('1', 'DefaultVlan'),
        'Eth1/54': ('1', 'DefaultVlan'),
    },
    'c': {
        'Eth1/1': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/2': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/3': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/4': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/5': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/6': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/7': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/8': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/9': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/10': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/11': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/12': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/13': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/14': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/15': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/16': ('51,100,203', 'ACCWIFI/ACCGUEST/MGMT'),
        'Eth1/17': ('168', 'IPCAM'),
        'Eth1/18': ('168', 'IPCAM'),
        'Eth1/19': ('168', 'IPCAM'),
        'Eth1/20': ('168', 'IPCAM'),
        'Eth1/21': ('168', 'IPCAM'),
        'Eth1/22': ('168', 'IPCAM'),
        'Eth1/23': ('168', 'IPCAM'),
        'Eth1/24': ('168', 'IPCAM'),
        'Eth1/25': ('168', 'IPCAM'),
        'Eth1/26': ('168', 'IPCAM'),
        'Eth1/27': ('168', 'IPCAM'),
        'Eth1/28': ('168', 'IPCAM'),
        'Eth1/29': ('168', 'IPCAM'),
        'Eth1/30': ('168', 'IPCAM'),
        'Eth1/31': ('168', 'IPCAM'),
        'Eth1/32': ('168', 'IPCAM'),
        'Eth1/33': ('160', 'Printer_DoorAccess'),
        'Eth1/34': ('160', 'Printer_DoorAccess'),
        'Eth1/35': ('160', 'Printer_DoorAccess'),
        'Eth1/36': ('160', 'Printer_DoorAccess'),
        'Eth1/37': ('160', 'Printer_DoorAccess'),
        'Eth1/38': ('160', 'Printer_DoorAccess'),
        'Eth1/39': ('160', 'Printer_DoorAccess'),
        'Eth1/40': ('160', 'Printer_DoorAccess'),
        'Eth1/41': ('100', 'ACCGUEST'),
        'Eth1/42': ('100', 'ACCGUEST'),
        'Eth1/43': ('160', 'Printer_DoorAccess'),
        'Eth1/44': ('160', 'Printer_DoorAccess'),
        'Eth1/45': ('160', 'Printer_DoorAccess'),
        'Eth1/46': ('1', 'DefaultVlan'),
        'Eth1/47': ('1', 'DefaultVlan'),
        'Eth1/48': ('1', 'DefaultVlan'),
        'Eth1/49': ('trunk', 'Uplink to A 機櫃'),
        'Eth1/50': ('1', 'DefaultVlan'),
        'Eth1/51': ('1', 'DefaultVlan'),
        'Eth1/52': ('1', 'DefaultVlan'),
        'Eth1/53': ('1', 'DefaultVlan'),
        'Eth1/54': ('1', 'DefaultVlan'),
    },
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


def parse_counters(raw):
    ports = []
    blocks = re.split(r'(Ethernet \d+/\s*\d+)', raw)
    for i in range(1, len(blocks), 2):
        port_name = blocks[i].strip().replace('Ethernet ', 'Eth')
        port_name = re.sub(r'\s+', '', port_name)
        data = blocks[i+1] if i+1 < len(blocks) else ''

        def val(pattern):
            m = re.search(r'(\d+)\s+' + pattern, data)
            return int(m.group(1)) if m else 0

        in_kbps = val(r'Octets Input in kbits per second')
        out_kbps = val(r'Octets Output in kbits per second')
        out_util = re.search(r'([\d.]+)\s+% Output Utilization', data)
        out_util = float(out_util.group(1)) if out_util else 0.0
        m_in = re.search(r'(\d+)\s+Octets Input\s*\n', data)
        m_out = re.search(r'(\d+)\s+Octets Output\s*\n', data)
        octets_in = int(m_in.group(1)) if m_in else 0
        octets_out = int(m_out.group(1)) if m_out else 0
        err_in = val(r'Error Input')
        fcs = val(r'FCS Errors')

        ports.append({
            'port': port_name,
            'in_kbps': in_kbps, 'out_kbps': out_kbps,
            'out_util': out_util,
            'octets_in': octets_in, 'octets_out': octets_out,
            'err_in': err_in, 'fcs': fcs,
        })
    return ports


def port_sort_key(port_name):
    m = re.match(r'Eth(\d+)/(\d+)', port_name)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    return (999, 999)


def fmt_bytes(b):
    if b >= 1e12: return f"{b/1e12:.2f} TB"
    if b >= 1e9: return f"{b/1e9:.1f} GB"
    if b >= 1e6: return f"{b/1e6:.1f} MB"
    if b > 0: return f"{b} B"
    return "—"


def fmt_speed(k):
    if k >= 1000: return f"{k/1000:.1f} Mbps"
    if k > 0: return f"{k} kbps"
    return "閒置"


def check_switch(switch_key, output_file=None):
    info = SWITCHES[switch_key]
    vlan_map = VLAN_MAP.get(switch_key, {})

    lines = []
    lines.append(f"\n{'='*100}")
    lines.append(f" {info['name']} ({info['host']})")
    lines.append(f"{'='*100}")

    try:
        ssh, shell = connect(info['host'])
    except Exception as e:
        lines.append(f"  ❌ 連線失敗: {e}")
        for l in lines:
            print(l)
        return lines

    raw = send_cmd(shell, 'show interfaces counters')
    ssh.close()

    ports = parse_counters(raw)
    active = [p for p in ports if p['in_kbps'] > 0 or p['out_kbps'] > 0 or p['octets_in'] > 0]
    active.sort(key=lambda p: port_sort_key(p['port']))

    lines.append(f"  {'Port':<9} {'VLAN':<16} {'VLAN名稱':<24} {'In Speed':<12} {'Out Speed':<12} {'Out%':<7} {'累計 In':<10} {'累計 Out':<10} {'Error'}")
    lines.append(f"  {'-'*110}")

    for p in active:
        vlan_id, vlan_name = vlan_map.get(p['port'], ('?', '?'))
        err_str = '—'
        if p['fcs'] > 0:
            err_str = f"⚠️ FCS:{p['fcs']}"
        elif p['err_in'] > 0:
            err_str = f"Err:{p['err_in']}"

        lines.append(f"  {p['port']:<9} {vlan_id:<16} {vlan_name:<24} "
              f"{fmt_speed(p['in_kbps']):<12} {fmt_speed(p['out_kbps']):<12} "
              f"{p['out_util']:<7.2f} {fmt_bytes(p['octets_in']):<10} "
              f"{fmt_bytes(p['octets_out']):<10} {err_str}")

    # 逐行印出避免被摺疊
    for l in lines:
        print(l, flush=True)

    return lines


def main():
    if len(sys.argv) < 2:
        print("用法: python3 check_traffic.py [a|b|c|all]")
        sys.exit(1)

    target = sys.argv[1].lower()
    all_lines = []

    if target == 'all':
        for key in ['a', 'b', 'c']:
            all_lines += check_switch(key)
    elif target in SWITCHES:
        all_lines += check_switch(target)
    else:
        print(f"未知目標: {target}")
        sys.exit(1)

    # 同時寫入檔案方便查看
    outfile = '/tmp/gbc_traffic_report.txt'
    with open(outfile, 'w') as f:
        for l in all_lines:
            f.write(l + '\n')
    print(f"\n📄 報告已存至: {outfile}")


if __name__ == '__main__':
    main()
