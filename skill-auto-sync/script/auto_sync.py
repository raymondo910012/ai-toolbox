#!/usr/bin/env python3
"""
Skill Auto Sync - 自動檢查 skills 變更並 push 到 GitHub
用法: python3 auto_sync.py
"""

import subprocess
import os
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


def main():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now}] 開始檢查 skills 變更...")

    # 確保 remote URL 是最新的
    run(f'git remote set-url origin {get_remote_url()}')

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
