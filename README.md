# InboxIQ — Static Demo Site (GitHub Pages Build)

This folder is a **ready-to-deploy static build** of the InboxIQ landing + interactive demo. No backend, no Node build step — pure HTML/CSS/JS so GitHub Pages serves it instantly.

## 🚀 Deploy to GitHub Pages (3 ways)

### Option A — Easiest: serve from `/docs`
1. Copy the **contents** of this folder into a folder called `docs/` at the **root** of your repository.
2. Push to `main`.
3. On GitHub → **Settings → Pages** → Source = `Deploy from a branch` → Branch = `main` → Folder = `/docs` → **Save**.
4. Wait ~30 seconds. Site is live at:
   `https://mahammadriyazshek.github.io/InboxIQ-The-Agentic-Productivity-Layer-for-Microsoft-365/`

### Option B — Serve from repo root
1. Copy the **contents** of this folder into the **root** of your repository (replacing/adding files alongside `index.html`).
2. Settings → Pages → Branch = `main` → Folder = `/ (root)` → Save.

### Option C — Use a `gh-pages` branch
1. Create an orphan branch: `git checkout --orphan gh-pages`
2. Copy these files in, commit, push.
3. Settings → Pages → Branch = `gh-pages` → Folder = `/ (root)` → Save.

## 📂 What's in here

```
.
├── index.html            ← Full single-page site (hero, problem, solution, demo, architecture, results)
├── 404.html              ← Redirects unknown routes back to /
├── .nojekyll             ← Tells GitHub Pages to skip Jekyll (serves files as-is)
└── assets/
    ├── logo.png
    ├── dashboard.png
    ├── mockup_mobile.png
    ├── architecture.png
    ├── InboxIQ_Deck.pdf
    └── InboxIQ_Deck.pptx
```

## ✅ Why the previous deploy didn't work

Your repo contains a **React + Vite + FastAPI** app. GitHub Pages only serves **static files** — it can't run the FastAPI backend (`uvicorn main:app`), and the Vite source (`.tsx`) is not browser-readable until you `npm run build`. The compiled `dist/` was never pushed, so Pages had nothing to render → blank page.

This build avoids both problems:
- **Pre-rendered HTML** — works the moment Pages picks it up.
- **Mock data baked in** — the interactive dashboard + chat demo work fully client-side, no API calls.
- **All assets self-contained** — under `./assets/`, no CDN dependencies beyond Google Fonts.

## 🛠 Local preview
```bash
# any static server works
python3 -m http.server 8080
# then open http://localhost:8080
```
