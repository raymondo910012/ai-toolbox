#!/bin/bash
echo "=== Setting up Git in WSL ==="

# Git global config
git config --global user.name "raymondo910012"
git config --global user.email "raymondo910012@gmail.com"
git config --global credential.helper store
git config --global core.autocrlf input

# Store GitHub PAT
# Replace YOUR_PAT_HERE with your token (generate at https://github.com/settings/tokens)
# Run this script once after rotating your PAT
PAT="${GITHUB_PAT:-YOUR_PAT_HERE}"
echo "https://raymondo910012:${PAT}@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials

echo "Git config done."
echo "Name:  $(git config --global user.name)"
echo "Email: $(git config --global user.email)"
echo "Cred:  $(git config --global credential.helper)"
echo ""

# Test: clone access check
echo "=== Testing GitHub access ==="
git ls-remote https://github.com/raymondo910012/ai-toolbox.git HEAD 2>&1 | head -2
echo ""
echo "=== Setup complete! ==="
