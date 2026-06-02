# Lifestyle Dashboard

A personal health and fitness web app built with Python Flask. Tracks workouts, macros, supplements, hair care, and skincare — all in one place, with science-backed recommendations tailored for lean muscle gain.

Runs locally for development and deploys to Render for always-on access.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Backend | Python 3.10+ / Flask |
| Database | SQLite (local) / PostgreSQL (Render) |
| Frontend | Jinja2 + Tailwind CSS CDN + Chart.js CDN |
| Deployment | Render (free tier) |

---

## Local Setup

### Prerequisites

- Python 3.10 or higher — check with `python --version`
- Git

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/lifestyle-dashboard.git
cd lifestyle-dashboard
```

### 2. Create and activate a virtual environment

```bash
# Create the environment
python -m venv venv

# Activate — Windows (PowerShell)
venv\Scripts\activate

# Activate — macOS / Linux
source venv/bin/activate
```

You'll see `(venv)` in your terminal prompt when the environment is active.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` — the defaults work for local dev, but set a real `SECRET_KEY`:

```
DATABASE_URL=sqlite:///dev.db
SECRET_KEY=change-me-to-any-long-random-string
PROGRAM_START_DATE=2026-06-02
```

### 5. Run the app

```bash
flask --app app:create_app run --debug
```

Open **http://127.0.0.1:5000** in your browser.

---

## Stopping the App

Press **Ctrl + C** in the terminal where the server is running.

---

## Deactivating the Virtual Environment

When you're done working:

```bash
deactivate
```

The `(venv)` prefix disappears from your prompt. Run `venv\Scripts\activate` again next time to resume.

---

## Environment Variables

No paid API keys are required. The only variables you need to set are:

| Variable | Required | What it does |
|---|---|---|
| `DATABASE_URL` | Yes | `sqlite:///dev.db` locally. Render sets this automatically to PostgreSQL. |
| `SECRET_KEY` | Yes | Flask session secret. Any long random string works locally. Render auto-generates one. |
| `PROGRAM_START_DATE` | Yes | ISO date when you started the program (`YYYY-MM-DD`). Used to calculate "Day N" on the overview. |

Exercise images are fetched from the public **Wger REST API** — no account or API key needed.

---

## Scripts

### Fetch exercise images

Run once after setup to populate image URLs in `data/exercises.json`:

```bash
python scripts/fetch_wger_images.py
```

Hits the public Wger API, stores image URLs directly in the JSON file. Takes ~60 seconds. Safe to re-run — already-fetched exercises are skipped.

---

## Running Tests

```bash
pytest
```

Uses an in-memory SQLite database. Does not touch `dev.db`.

---

## Project Structure

```
lifestyle-dashboard/
├── app.py                  # Flask app factory (create_app)
├── config.py               # Config class (reads .env)
├── requirements.txt
├── render.yaml             # Render deployment config (auto-read on deploy)
├── .env.example            # Template — copy to .env and fill in
│
├── models/                 # SQLAlchemy models (user logs only)
│   ├── workout.py          # WorkoutLog, ExerciseSet
│   ├── nutrition.py        # MealLog
│   └── body.py             # BodyMetric (weight entries)
│
├── routes/                 # Flask blueprints — one per section
│   ├── dashboard.py        # GET / and POST /body/log
│   ├── workouts.py
│   ├── nutrition.py
│   └── ...
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Sidebar, theme toggle — shared by all pages
│   └── dashboard/
│       └── overview.html
│
├── static/
│   ├── css/custom.css
│   └── js/
│       ├── theme.js        # Dark/light toggle (persists via localStorage)
│       ├── charts.js       # Chart.js weight progress chart
│       └── macro_tracker.js
│
├── data/                   # Static coaching content — edit freely
│   ├── exercises.json      # Exercise library + Wger image URLs
│   ├── supplements.json    # Timing table + product verdicts
│   ├── meals.json          # Training/rest/run day meal plans
│   └── products.json       # Hair + skin product analysis
│
├── scripts/
│   └── fetch_wger_images.py  # One-time: fetches exercise images from Wger
│
└── tests/
    ├── conftest.py
    ├── test_models.py
    ├── test_app.py
    ├── test_routes.py
    └── test_dashboard.py
```

**Key distinction:** `data/*.json` holds static coaching content (exercises, plans, recommendations). The database only stores what you actually log — workout sets, meal entries, body weight over time.

---

## Deployment on Render

### First deploy

1. Push the repo to GitHub.

2. Go to [render.com](https://render.com) → **New → PostgreSQL** → free plan → name it `lifestyle-db`.

3. Go to **New → Web Service** → connect your GitHub repo. Render reads `render.yaml` automatically — no manual config needed.

4. After the first successful deploy, open the Render **Shell** tab and initialise the database:
   ```python
   from models import db
   db.create_all()
   ```
   *(One-time only. Future deploys preserve the data.)*

5. App is live at `https://lifestyle-dashboard.onrender.com`.

### Every subsequent deploy

```bash
git add .
git commit -m "describe your change"
git push
```

Render detects the push and redeploys in ~2 minutes automatically.

### Render free tier notes

- The web service **sleeps after 15 min of inactivity** — the first request after sleep takes ~30 sec to wake up.
- The free PostgreSQL instance **expires after 90 days** — Render emails you before expiry. Upgrade or recreate to continue.
- `dev.db` is for local use only and is not deployed to Render.
