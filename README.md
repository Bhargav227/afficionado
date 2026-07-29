# Afficionado Coffee Roasters — Sales Intelligence (Streamlit)

A Streamlit dashboard for the *Product Optimization & Revenue Contribution Analysis*
project: KPI cards, category/store/time-slot breakdowns, Top-N product rankings,
a popularity-vs-revenue scatter plot, Pareto (80/20) analysis, ABC classification,
product segmentation, and a searchable/downloadable product drill-down table —
all filterable by store, category, and product type from the sidebar.

Every number is computed live from the actual project dataset (`data/coffee_features.csv`,
`data/product_summary.csv`, `data/store_summary.csv`) — nothing is hard-coded.

---

## 1. Run it locally first (optional, but recommended)

```bash
pip install -r requirements.txt
streamlit run app.py
```

This opens the dashboard at `http://localhost:8501` in your browser. Confirm it looks right
before deploying.

---

## 2. Get a live public URL — deploy to Streamlit Community Cloud (free)

This is the fastest way to turn this folder into a real, shareable link.

### Step A — Put this folder on GitHub
1. Go to [github.com](https://github.com) and sign in (create a free account if needed).
2. Click **New repository** (top-right `+` icon → "New repository").
3. Name it something like `afficionado-coffee-dashboard`, set it to **Public**, click **Create repository**.
4. On the new repo's page, click **uploading an existing file** (or use the "Add file → Upload files" button).
5. Drag in **all the files and folders from this package** — `app.py`, `requirements.txt`,
   the `data/` folder, and the `.streamlit/` folder — keeping the same folder structure.
   (If GitHub's uploader hides the `.streamlit` folder because it starts with a dot, use
   `git` from a terminal instead — see "Step A (alternative)" below.)
6. Click **Commit changes**.

**Step A (alternative, using git from a terminal):**
```bash
cd path/to/this/folder
git init
git add .
git commit -m "Initial commit — Afficionado Coffee dashboard"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/afficionado-coffee-dashboard.git
git push -u origin main
```

### Step B — Deploy on Streamlit Community Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with your GitHub account.
2. Click **Create app** (or **New app**).
3. Choose **"Deploy a public app from GitHub"**.
4. Pick your repository (`afficionado-coffee-dashboard`), branch `main`, and set the
   main file path to `app.py`.
5. Click **Deploy**.

Streamlit will install everything from `requirements.txt` and build the app automatically.
This takes 1–3 minutes the first time.

### Step C — Get your link
Once deployed, you'll land on a URL that looks like:

```
https://afficionado-coffee-dashboard-yourname.streamlit.app
```

That's the link to submit. It's live, public, and updates automatically any time you
push changes to the GitHub repo.

---

## 3. Folder contents

```
app.py                     — the Streamlit application (single file)
requirements.txt           — Python dependencies for deployment
.streamlit/config.toml     — brand theme (colors)
data/coffee_features.csv   — transaction-level dataset (149,116 rows)
data/product_summary.csv   — per-product summary (ABC class, segment, ranks)
data/store_summary.csv     — per-store summary
```

## 4. If deployment fails
- **"Module not found"** → check `requirements.txt` was uploaded and matches this one exactly.
- **"File not found: data/coffee_features.csv"** → confirm the `data/` folder was uploaded
  with the same name and sits next to `app.py`, not inside another subfolder.
- **App loads but looks unstyled** → confirm `.streamlit/config.toml` was included; GitHub's
  drag-and-drop uploader sometimes skips dot-folders, so use the git method above if this happens.
