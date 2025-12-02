---
description: Guide to initializing a Git repository and pushing to GitHub
---

# How to Push Your Code to GitHub from Scratch

Follow these steps to version control your project and push it to GitHub.

## 1. Initialize Git
Open your terminal in the project directory (`C:\Users\13015646\Desktop\emt_app`) and run:
```powershell
git init
```

## 2. Create a .gitignore File
It is critical to ignore unnecessary files (like virtual environments, compiled python files, and secrets).
Create a file named `.gitignore` and add the following content:
```text
__pycache__/
*.pyc
instance/
.pytest_cache/
.env
venv/
env/
.vscode/
.idea/
*.db
*.sqlite3
```

## 3. Stage and Commit Your Files
Add all your files to the staging area:
```powershell
git add .
```

Commit them with a message:
```powershell
git commit -m "Initial commit of EMT App"
```

## 4. Create a Repository on GitHub
1. Go to [GitHub.com](https://github.com) and log in.
2. Click the **+** icon in the top right and select **New repository**.
3. Name it `emt_app` (or whatever you prefer).
4. **Do not** check "Initialize with README", "Add .gitignore", or "Add license" (since we are importing an existing repository).
5. Click **Create repository**.

## 5. Link and Push
Copy the URL of your new repository (e.g., `https://github.com/YOUR_USERNAME/emt_app.git`).
Run the following commands in your terminal (replace the URL with yours):

```powershell
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/emt_app.git
git push -u origin main
```

## 6. Verify
Refresh your GitHub repository page to see your code!
