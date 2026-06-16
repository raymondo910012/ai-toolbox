@echo off
del /F "C:\Projects\ai-toolbox\.git\index.lock" 2>nul
wsl bash -c "cd /mnt/c/Projects/ai-toolbox && git mv lab personal_lab && git add -A && git commit -m 'refactor: rename lab to personal_lab' && git push" > C:\Projects\ai-toolbox\scripts\push_result.txt 2>&1
type C:\Projects\ai-toolbox\scripts\push_result.txt
pause
