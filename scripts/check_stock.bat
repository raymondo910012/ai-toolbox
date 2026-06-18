@echo off
wsl bash /mnt/c/Projects/ai-toolbox/scripts/check_stock.sh > C:\Projects\ai-toolbox\scripts\stock_check.txt 2>&1
type C:\Projects\ai-toolbox\scripts\stock_check.txt
pause
