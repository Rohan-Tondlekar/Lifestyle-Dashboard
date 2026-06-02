# Lifestyle Dashboard

A personal health and fitness web app built with Python Flask. Tracks workouts, macros, supplements, hair care, and skincare — all in one place, with science-backed recommendations tailored for lean muscle gain.

Live at: `https://lifestyle-dashboard.up.railway.app/`

---

## Tech Stack

| Layer | Choice |
|---|---|
| Backend | Python 3.10+ / Flask 3.0 |
| Database | SQLite (local dev) / PostgreSQL via Supabase (production) |
| Frontend | Jinja2 + Tailwind CSS CDN + Chart.js CDN |
| Deployment | Railway (auto-deploys on git push) |
| DB Hosting | Supabase (one project, multiple schemas for future apps) |

---

## Local Setup

### Prerequisites

- Python 3.10 or higher — check with `python --version`
- Git

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/Lifestyle-Dashboard.git
cd Lifestyle-Dashboard
```

### 2. Create and activate a virtual environment

```bash
# Create
python -m venv venv

# Activate — Windows (PowerShell)
venv\Scripts\activate

# Activate — macOS / Linux
source venv/bin/activate
```

You'll see `(venv)` in your terminal prompt when active.

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

The default `.env` uses SQLite — no further setup needed for local dev:

```
DATABASE_URL=sqlite:///dev.db
SECRET_KEY=dev-secret-key-change-me
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

```bash
deactivate
```

Run `venv\Scripts\activate` again next time to resume.

---

## Environment Variables

| Variable | Local | Production (Railway) | Description |
|---|---|---|---|
| `DATABASE_URL` | `sqlite:///dev.db` | Supabase session pooler URI | Database connection string |
| `DB_SCHEMA` | *(not set — SQLite has no schemas)* | `lifestyle` | PostgreSQL schema for this app |
| `SECRET_KEY` | Any string | Generate with command below | Flask session secret |
| `PROGRAM_START_DATE` | `2026-06-02` | `2026-06-02` | ISO date the program started — used for "Day N" counter |

Generate a secure `SECRET_KEY`:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

No third-party API keys are required. Exercise images are fetched from the public **Wger REST API**.

---

## Scripts

### Fetch exercise images (run once)

Populates `image_url` fields in `data/exercises.json` from the Wger API:

```bash
python scripts/fetch_wger_images.py
```

Takes ~60 seconds. Safe to re-run — already-fetched exercises are skipped.

---

## Running Tests

```bash
pytest
```

Uses an in-memory SQLite database. Does not touch `dev.db` or Supabase.

---

## Project Structure

```
Lifestyle-Dashboard/
├── app.py                    # Flask app factory (create_app)
├── config.py                 # Config class — reads .env, sets up PostgreSQL engine options
├── requirements.txt
├── Procfile                  # gunicorn start command for Railway
├── render.yaml               # Legacy — kept for reference
├── .env                      # Local secrets — never committed
├── .env.example              # Template — copy to .env
│
├── models/
│   ├── workout.py            # WorkoutLog, ExerciseSet
│   ├── nutrition.py          # MealLog
│   └── body.py               # BodyMetric (weight entries)
│
├── routes/                   # Flask blueprints — one per page section
│   ├── dashboard.py          # GET / · POST /body/log
│   ├── workouts.py           # GET /workouts · POST /workouts/log
│   ├── nutrition.py          # GET /nutrition · POST /nutrition/log
│   ├── supplements.py        # GET /supplements
│   ├── hair.py               # GET /hair
│   ├── skin.py               # GET /skin
│   ├── shopping.py           # GET /shopping
│   ├── schedule.py           # GET /schedule
│   └── myths.py              # GET /myths
│
├── templates/
│   ├── base.html             # Sidebar, dark/light toggle — shared layout
│   ├── dashboard/overview.html
│   ├── workouts/plan.html
│   ├── nutrition/meals.html
│   ├── supplements/schedule.html
│   ├── hair/routine.html
│   ├── skin/routine.html
│   ├── shopping/list.html
│   ├── schedule/index.html
│   └── myths/index.html
│
├── static/
│   ├── css/custom.css
│   └── js/
│       ├── theme.js          # Dark/light toggle — persists via localStorage
│       ├── charts.js         # Chart.js weight progress chart
│       └── macro_tracker.js  # Live macro progress bars
│
├── data/                     # Static coaching content — edit freely, no Python changes needed
│   ├── exercises.json        # Exercise library + Wger image URLs
│   ├── supplements.json      # Timing table, current products, missing supplements
│   ├── meals.json            # Training/rest/run day meal plans, food database
│   └── products.json         # Hair + skin product verdicts
│
├── scripts/
│   └── fetch_wger_images.py  # One-time: resolves Wger exercise image URLs
│
└── tests/
    ├── conftest.py
    ├── test_models.py
    ├── test_app.py
    ├── test_routes.py
    ├── test_dashboard.py
    ├── test_workouts.py
    └── test_nutrition.py
```

`data/*.json` holds static coaching content. The database only stores user-generated logs — workout sets, meal entries, body weight over time.

---

## Deployment — Railway + Supabase

### Architecture

```
Local machine
  DATABASE_URL = sqlite:///dev.db        ← fast, offline, no setup

Railway (production web service)
  DATABASE_URL = postgresql://postgres.<ref>:[password]@aws-1-eu-central-1.pooler.supabase.com:5432/postgres
  DB_SCHEMA    = lifestyle               ← tables live in the 'lifestyle' schema

Supabase (one project, multiple schemas)
  └── schema: lifestyle   ← this app's tables
  └── schema: viage       ← future app
  └── schema: ...
```

### First-time Supabase setup

1. Sign up at **supabase.com** — free, no card required.
2. Create one project (e.g. `personal-projects`), region: **Frankfurt**.
3. In **SQL Editor**, create a schema for this app:
   ```sql
   CREATE SCHEMA IF NOT EXISTS lifestyle;
   ```
4. Go to **Project Settings → Database → Connect → Session pooler → URI**.
   Copy the connection string — it looks like:
   ```
   postgresql://postgres.<project-ref>:[YOUR-PASSWORD]@aws-1-eu-central-1.pooler.supabase.com:5432/postgres
   ```

### First-time Railway setup

1. Push the repo to GitHub.
2. Go to **railway.app** → **New Project → Deploy from GitHub repo** → select this repo.
3. Railway detects Python and reads the `Procfile` automatically.
4. Go to your service → **Variables** tab → add these four:

   | Variable | Value |
   |---|---|
   | `DATABASE_URL` | Supabase session pooler URI (from step 4 above) |
   | `DB_SCHEMA` | `lifestyle` |
   | `SECRET_KEY` | Output of `python -c "import secrets; print(secrets.token_hex(32))"` |
   | `PROGRAM_START_DATE` | `2026-06-02` |

5. Railway redeploys automatically after saving variables.
6. **Settings → Networking → Generate Domain** to get your public URL.

Tables are created automatically on first startup — no manual `db.create_all()` needed.

### Every subsequent deploy

```bash
git add .
git commit -m "describe your change"
git push
```

Railway detects the push → rebuilds → live in ~2 minutes.

### Adding a future app to the same Supabase project

In Supabase SQL Editor:
```sql
CREATE SCHEMA IF NOT EXISTS viage;
```

In the new app's Railway service, set:
```
DATABASE_URL = postgresql://postgres.<ref>:[password]@aws-1-eu-central-1.pooler.supabase.com:5432/postgres
DB_SCHEMA    = viage
```

Same Supabase project, completely separate tables. Uses only 1 of your 2 free Supabase project slots.

### Supabase free tier notes

- Database **pauses after 7 days of inactivity** — log in to Supabase and click **Restore** to wake it up.
- Free tier: 500 MB storage, 2 active projects.
- Your data persists across Railway redeploys — only the Supabase database pause can interrupt access.

### Railway free tier notes

- Hobby plan ($5/month) — small personal apps typically use $0–1 of usage credit per month.
- No sleep/inactivity limits (unlike Render free tier).
- Auto-deploys on every push to `main`.

---

## Updating Content

All coaching content (exercises, meal plans, supplement schedules, product analysis) lives in `data/*.json`. Edit those files directly and push — no Python changes needed. The database only stores what you log.
