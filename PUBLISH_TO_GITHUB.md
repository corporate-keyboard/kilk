# Push this repo to GitHub

Two paths — pick one. Run all commands from the `kilk/` directory.

## Option A — with the `gh` CLI (recommended)

Requires the GitHub CLI installed and authenticated (`gh auth login`).

```bash
cd kilk

git init
git add .
git commit -m "Initial Kilk"

gh repo create kilk \
  --public \
  --description "Read-only MCP server exposing the Subby project's docs." \
  --source=. \
  --remote=origin \
  --push
```

Swap `--public` for `--private` if you'd rather start private.

## Option B — without `gh` (manual)

1. Go to https://github.com/new and create an **empty** repo named `kilk` (no README, no .gitignore, no license — the local repo provides those).
2. Then:

```bash
cd kilk

git init
git add .
git commit -m "Initial Kilk"
git branch -M main
git remote add origin git@github.com:YOUR-USERNAME/kilk.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub handle (or org name).

## After pushing

Update the two `corporate-keyboard` placeholders in `pyproject.toml` and the `git clone` line in `README.md` to point at your actual repo URL, then commit and push that change.
