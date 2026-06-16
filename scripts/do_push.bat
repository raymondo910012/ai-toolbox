@echo off
wsl bash /mnt/c/Projects/ai-toolbox/scripts/push_project.sh "C:\Projects\ai-toolbox" "feat: add WSL auto-push scripts and environment setup" > C:\Projects\ai-toolbox\scripts\push_result.txt 2>&1
type C:\Projects\ai-toolbox\scripts\push_result.txt
pause
