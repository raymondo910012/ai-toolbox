@echo off
del /F "C:\Projects\ai-toolbox\.git\index.lock" 2>nul
wsl bash /mnt/c/Projects/ai-toolbox/scripts/reorganize.sh > C:\Projects\ai-toolbox\scripts\reorg_result.txt 2>&1
type C:\Projects\ai-toolbox\scripts\reorg_result.txt
pause
