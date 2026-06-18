#!/usr/bin/env python3
"""
Skill Auto Sync - 自動檢查 skills 變更並 push 到 GitHub
用法: python3 auto_sync.py
"""

import subprocess
import os
import re
from datetime import datetime

SKILLS_DIR = os.path.expanduser('~/.kiro/skills')
TOKEN_FILE = os.path.expanduser('~/.kiro/.github_token')


def get_remote_url():
    with open(TOKEN_FILE, 'r') as f:
        token = f.read().strip()
    return f'https://raymondo910012:{token}@github.com/raymondo910012/ai-toolbox.git'


def run(cmd, cwd=SKILLS_DIR):
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def generate_readme():
    """掃描所有 skill 的 .md 檔，產生 README.md"""
    skills = []
    for entry in sorted(os.listdir(SKILLS_DIR)):
        skill_dir = os.path.join(SKILLS_DIR, entry)
        if not os.path.isdir(skill_dir) or entry.startswith('.'):
            continue
        # 找 skill markdown
        for f in os.listdir(skill_dir):
            if f.endswith('.md'):
                md_path = os.path.join(skill_dir, f)
                with open(md_path, 'r') as fh:
                    content = fh.read()
                # 解析 frontmatter
                name = entry
                desc = ''
                m = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
                if m:
                    name = m.group(1).strip()
                m = re.search(r'^description:\s*(.+?)(?:\n---|\n\n)', content, re.MULTILINE | re.DOTALL)
                if m:
                    desc = m.group(1).strip().replace('\n', ' ')
                # 找 scripts
                scripts = []
                script_dir = os.path.join(skill_dir, 'script')
                if os.path.isdir(script_dir):
                    scripts = sorted(os.listdir(script_dir))
                skills.append({'name': name, 'dir': entry, 'desc': desc, 'scripts': scripts})
                break

    # 取得 crontab
    cron_out, _, _ = run('crontab -l', cwd='/tmp')
    cron_lines = [l for l in cron_out.split('\n') if l.strip() and not l.startswith('#')]

    # 產生 README
    lines = []
    lines.append('# ai-toolbox')
    lines.append('')
    lines.append('Kiro CLI Skills 集合 — 自動化工具與網路管理腳本。')
    lines.append('')
    lines.append('## Skills 列表')
    lines.append('')
    for s in skills:
        lines.append(f"### {s['name']}")
        lines.append(f"📁 `{s['dir']}/`")
        lines.append('')
        lines.append(f"{s['desc']}")
        lines.append('')
        if s['scripts']:
            lines.append('**Scripts:**')
            for sc in s['scripts']:
                lines.append(f"- `{s['dir']}/script/{sc}`")
            lines.append('')

    if cron_lines:
        lines.append('## 排程 (Crontab)')
        lines.append('')
        lines.append('| 時間 | 腳本 | 說明 |')
        lines.append('|------|------|------|')
        for cl in cron_lines:
            parts = cl.split()
            if len(parts) >= 6:
                schedule = ' '.join(parts[:5])
                cmd = ' '.join(parts[5:])
                # 取得腳本名稱
                script_name = [p for p in parts if '.py' in p]
                script_name = os.path.basename(script_name[0]) if script_name else cmd
                # 解析時間
                minute, hour = parts[0], parts[1]
                time_str = f"每天 {hour}:{minute.zfill(2)}"
                lines.append(f"| {time_str} | `{script_name}` | {cmd.split('>>')[0].strip()} |")
        lines.append('')

    lines.append('---')
    lines.append(f"*最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    lines.append('')

    readme_path = os.path.join(SKILLS_DIR, 'README.md')
    with open(readme_path, 'w') as f:
        f.write('\n'.join(lines))
    print(f"  📄 README.md 已更新")


def main():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now}] 開始檢查 skills 變更...")

    # 確保 remote URL 是最新的
    run(f'git remote set-url origin {get_remote_url()}')

    # 更新 README.md
    generate_readme()

    # 檢查是否有變更
    run('git add -A')
    status, _, _ = run('git status --porcelain')

    if not status:
        print(f"[{now}] ✅ 無變更，不需要同步")
        return

    # 有變更，列出變更檔案
    print(f"[{now}] 📝 偵測到變更:")
    for line in status.split('\n'):
        print(f"  {line}")

    # Commit
    date_str = datetime.now().strftime('%Y-%m-%d')
    commit_msg = f"auto-sync: {date_str} skills update"
    _, err, code = run(f'git commit -m "{commit_msg}"')
    if code != 0:
        print(f"[{now}] ❌ Commit 失敗: {err}")
        return

    # Push
    _, err, code = run('git push origin main')
    if code != 0:
        print(f"[{now}] ❌ Push 失敗: {err}")
        return

    print(f"[{now}] ✅ 已同步到 GitHub")


if __name__ == '__main__':
    main()
