#!/bin/bash
# GitHub Push Instructions
# Replace YOUR_USERNAME with your actual GitHub username
# Replace YOUR_REPO_NAME with your repository name

# Add GitHub remote (replace with your actual repository URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Rename master to main (GitHub's default)
git branch -M main

# Push to GitHub
git push -u origin main

# After running these commands, your code will be on GitHub!
