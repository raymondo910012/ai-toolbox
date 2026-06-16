@echo off
REM Usage: git_push.bat "C:\Projects\project-name" "commit message"
REM Auto-called by Claude when user says "push to git"

set REPO_PATH=%~1
set COMMIT_MSG=%~2

if "%REPO_PATH%"=="" (
    echo ERROR: No repo path provided.
    pause
    exit /b 1
)
if "%COMMIT_MSG%"=="" (
    echo ERROR: No commit message provided.
    pause
    exit /b 1
)

echo Pushing %REPO_PATH% ...
cd /d %REPO_PATH%
git add .
git commit -m "%COMMIT_MSG%"
git push
echo.
echo Push complete: %REPO_PATH%
timeout /t 3 >nul
