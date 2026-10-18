# Upload the portfolio project to GitHub

The folder in this ZIP **is not itself a live GitHub repository**. You need a GitHub account and must create and push the repo.

## Recommended approach — Git command line

1. Extract the ZIP somewhere on Windows. Install Git for Windows and open PowerShell or Git Bash.
2. On github.com select **New repository**, set its name to `supply-chain-inventory-performance-dashboard`, choose Public and **do not initialise** it with another README/.gitignore (this ZIP already includes README).
3. In terminal, inside the extracted project folder:

```powershell
git init
git add .
git commit -m "Add synthetic NZ supply-chain and inventory analytics portfolio"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/supply-chain-inventory-performance-dashboard.git
git push -u origin main
```

Authentication may open a browser. Substitute YOUR-USERNAME. If Git asks for identity, configure `git config --global user.name` and `user.email` first. GitHub does not normally accept an account password directly for command-line HTTPS pushes; use the prompted supported sign-in or appropriate credential method.

## Alternative — GitHub web upload

Create an empty public repository and choose **Add file → Upload files**. For this many files, the Git command line or GitHub Desktop is more reliable than uploading files individually. Keep the directory hierarchy, not a single zipped blob if you want GitHub to display the README and SQL scripts.

## Post-upload checks

- README images display and links to markdown docs work.
- `data/processed/OrderLines.csv` has 153,503 body rows (approx 14 MB) and no single CSV exceeds GitHub's 100 MB hard file limit.
- `.xlsx`, 7 `.sql` scripts, DAX measures and six concept previews exist.
- Never call the concept previews actual Power BI screenshots or claim `.pbix` was delivered.
- Add your finished `.pbix` after creating and validating it in Microsoft Power BI Desktop; update its status in README.

## Add to LinkedIn

Open your LinkedIn profile, find **Add profile section → Recommended → Add featured** (the layout may change), select **Add link**, paste your public GitHub repo URL, and set a project title and short description. Alternatively add it in **Projects** in Accomplishments if your profile offers that section. Paste the prepared public announcement from `linkedin/profile_kit.md`, with your *actual verified URL*.
