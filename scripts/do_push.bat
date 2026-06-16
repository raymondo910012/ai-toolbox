@echo off
del /F "C:\Projects\ai-toolbox\.git\index.lock" 2>nul
wsl bash /mnt/c/Projects/ai-toolbox/scripts/push_project.sh "C:\Projects\ai-toolbox" "chore: remove obsolete bat files" > C:\Projects\ai-toolbox\scripts\push_result.txt 2>&1
type C:\Projects\ai-toolbox\scripts\push_result.txt
pause
