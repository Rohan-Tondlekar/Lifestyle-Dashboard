# Lifestyle Dashboard — Design Spec
Date: 2026-06-02

## Overview

A personal lifestyle dashboard web app for a 24-year-old male in Hamburg targeting lean muscle gain. Covers fitness, nutrition, supplements, hair care, and skincare. Runs locally during development, deployed publicly on Render with PostgreSQL.

User profile: Age 24 · Height 170 cm · Weight 59 kg → Target 65 kg · Program start: 2026-06-02

---

## Tech Stack

| Layer | Choice |
|---|---|
| Backend | Python 3.11+ / Flask (app factory pattern) |
| Database | PostgreSQL on Render · SQLite locally (SQLAlchemy, one config line switches) |
| Frontend | Jinja2 templates + Tailwind CSS CDN + Chart.js CDN |
| Server | gunicorn (production) · Flask dev server (local) |
| Deployment | Render free tier (Web Service + PostgreSQL add-on) |
| Exercise images | Wger REST API — URLs resolved once into exercises.json at dev time |

---

## Project File Structure

```
lifestyle-dashboard/
│
├── app.py                        # Flask app factory
├── config.py                     # Config: DB URL, secret key, program start date
├── requirements.txt              # Flask, SQLAlchemy, gunicorn, psycopg2-binary, requests
├── render.yaml                   # Render deployment config
├── .env.example                  # Template for local env vars (.env not committed)
├── .gitignore
│
├── models/
│   ├── __init__.py               # db = SQLAlchemy()
│   ├── workout.py                # WorkoutLog, ExerciseSet
│   ├── nutrition.py              # MealLog
│   └── body.py                   # BodyMetric
│
├── routes/
│   ├── __init__.py
│   ├── dashboard.py              # GET /
│   ├── schedule.py               # GET /schedule
│   ├── workouts.py               # GET /workouts, POST /workouts/log
│   ├── nutrition.py              # GET /nutrition, POST /nutrition/log
│   ├── supplements.py            # GET /supplements
│   ├── hair.py                   # GET /hair
│   ├── skin.py                   # GET /skin
│   ├── shopping.py               # GET /shopping
│   └── myths.py                  # GET /myths
│
├── scripts/
│   └── fetch_wger_images.py      # One-time script: calls Wger API, resolves image URLs → writes to exercises.json
│
├── static/
│   ├── css/custom.css
│   └── js/
│       ├── theme.js              # Dark/light toggle, persists to localStorage
│       ├── macro_tracker.js      # Live progress bars on nutrition page
│       └── charts.js             # Chart.js weight progress chart
│
├── templates/
│   ├── base.html                 # Sidebar, theme toggle, CDN includes
│   ├── dashboard/overview.html
│   ├── schedule/index.html
│   ├── workouts/plan.html
│   ├── nutrition/meals.html
│   ├── supplements/schedule.html
│   ├── hair/routine.html
│   ├── skin/routine.html
│   ├── shopping/list.html
│   └── myths/index.html
│
└── data/
    ├── exercises.json            # Exercise library with wger image_url, sets/reps, progressions
    ├── supplements.json          # Timing table, current products, missing supplements
    ├── meals.json                # Training/rest/run day plans, macro targets, food database
    └── products.json             # Hair + skin product verdicts and routines
```

---

## Database Models

```python
# models/workout.py
class WorkoutLog(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    date          = db.Column(db.String, nullable=False)   # ISO date string
    day_type      = db.Column(db.String)                   # "upper" | "lower" | "run" | "rest"
    completed     = db.Column(db.Boolean, default=False)
    notes         = db.Column(db.Text)
    sets          = db.relationship('ExerciseSet', backref='workout', lazy=True)

class ExerciseSet(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    workout_id    = db.Column(db.Integer, db.ForeignKey('workout_log.id'))
    exercise_name = db.Column(db.String, nullable=False)
    weight_kg     = db.Column(db.Float)
    reps          = db.Column(db.Integer)
    set_number    = db.Column(db.Integer)

# models/nutrition.py
class MealLog(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    date          = db.Column(db.String, nullable=False)
    meal_name     = db.Column(db.String)
    protein_g     = db.Column(db.Float, default=0)
    carbs_g       = db.Column(db.Float, default=0)
    fat_g         = db.Column(db.Float, default=0)
    kcal          = db.Column(db.Integer, default=0)
    notes         = db.Column(db.Text)

# models/body.py
class BodyMetric(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    date          = db.Column(db.String, nullable=False)
    weight_kg     = db.Column(db.Float)
    notes         = db.Column(db.Text)
```

---

## Blueprint & Route Map

| Method | Route | Blueprint | Purpose |
|---|---|---|---|
| GET | `/` | dashboard | Overview page |
| GET | `/schedule` | schedule | Weekly 7-day grid + running program |
| GET | `/workouts` | workouts | Exercise cards (Phase 1 + 2) |
| POST | `/workouts/log` | workouts | Log a completed workout set |
| GET | `/nutrition` | nutrition | Meal plans (training/rest/run day) |
| POST | `/nutrition/log` | nutrition | Log a meal/macro entry |
| GET | `/supplements` | supplements | Timing table + product verdicts |
| GET | `/hair` | hair | Routine table + product analysis |
| GET | `/skin` | skin | AM/PM routine + product verdicts |
| GET | `/shopping` | shopping | Priority shopping list |
| GET | `/myths` | myths | Claim/verdict/evidence cards |
| POST | `/body/log` | dashboard | Log a weight entry |

---

## Frontend Design System

### Navigation — Icon Sidebar

- **Width**: 56px collapsed (icons only). Expands to 200px on hover as a fixed overlay — no layout shift, content stays in place.
- **Expand behavior**: CSS `transition: width 200ms ease` on the sidebar element. Hover triggers width change. Labels (`Overview`, `Schedule`, etc.) hidden in collapsed state via `opacity: 0 / overflow: hidden`.
- **Icon order** (top to bottom): 📊 Overview · 📅 Schedule · 💪 Workouts · 🥗 Nutrition · 💊 Supplements · 💇 Hair · ✨ Skin · 🛒 Shopping · ❓ Myths
- **Bottom of sidebar**: ☾/☀ dark/light toggle
- **Active state**: highlighted pill on the current page icon

### Theme — Dark / Light Toggle

- Tailwind `darkMode: 'class'` strategy
- Toggle adds/removes `dark` class on `<html>`
- State persisted to `localStorage` key `theme`
- `theme.js` reads `localStorage` on page load and applies class before paint (prevents flash)

**Color tokens:**

| Token | Dark mode | Light mode |
|---|---|---|
| Page background | `#0f172a` (slate-900) | `#f8fafc` (slate-50) |
| Sidebar background | `#0a0f1e` | `#eef2ff` (indigo-50) |
| Card background | `#1e293b` (slate-800) | `#ffffff` |
| Accent | `#3b82f6` (blue-500) | `#6366f1` (indigo-500) |
| Primary text | `#f1f5f9` (slate-100) | `#1e1b4b` (indigo-950) |
| Secondary text | `#64748b` (slate-500) | `#64748b` (slate-500) |

### CDN Includes (in base.html)

```html
<!-- Tailwind with darkMode class config -->
<script>tailwind.config = { darkMode: 'class' }</script>
<script src="https://cdn.tailwindcss.com"></script>
<!-- Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

---

## Page Designs

### Overview (`/`)

Four zones top to bottom:

1. **Stats bar** — 3 cards: Current Weight (latest BodyMetric or default 59 kg) · BMI (weight / 1.70²) · Days Since Start (today − 2026-06-02). Inline weight-log form on the stats bar.
2. **Priority cards** — 5 numbered cards: Nutrition · Resistance Training · Hair · Skin · Running. Each card links to its section.
3. **Height myth banner** — info-styled banner. Title: "Height at 24 — Honest Answer". Content: growth plates explanation, posture correction (2–3 cm), 3 exercises (dead hangs, cat-cow, hip flexor stretches).
4. **Body weight chart** — Chart.js line chart of BodyMetric entries over time (hidden if no entries yet).

### Schedule (`/schedule`)

- 7-day card grid (Mon–Sun) with day type badge (Upper · Run · Lower · Rest)
- Daily timeline table for a training day
- 8-week running program table

### Workouts (`/workouts`)

- Phase toggle (Phase 1 / Phase 2) — JS tab switch, no page reload
- Exercise cards: image (from `image_url` in exercises.json) + name + muscle group + sets/reps + form cues + progression
- Workout log form: select exercise → weight → reps → set number → POST `/workouts/log`

### Nutrition (`/nutrition`)

- Day type selector (Training / Rest / Run day)
- Meal plan table for selected day
- Macro progress bars (protein / carbs / fat / kcal) — live JS update as meals are logged
- Food database table (price/quality ranking)
- Weekly prep checklist

### Supplements (`/supplements`)

- Daily timing table (loaded from supplements.json)
- Current product verdict cards (D3, Magnesium)
- Missing supplements table with mechanism + dose + where to buy

### Hair (`/hair`)

- Medical warning banner (AGA pattern, dermatologist recommendation)
- Product analysis cards (Cien shampoo, Ketoconazole, Pantene oil, scalp brush)
- Full routine table (8 steps with frequency + product)

### Skin (`/skin`)

- Product verdict cards (Lacura Urea, Fussbalsam, Handcreme, NIVEA, SPF)
- AM/PM routine table
- Missing product callout (face moisturizer recommendation)

### Shopping (`/shopping`)

- Priority table with colored badges (High / Medium / Discuss with doctor)
- Columns: Product · Purpose · Where · Cost · Priority

### Myths (`/myths`)

- Claim/verdict/evidence cards
- Olive oil + lemon myth: full breakdown with "what actually works" section

---

## Data Files

### `data/exercises.json` (sample entry)
```json
{
  "name": "DB Goblet Squat",
  "wger_id": 32,
  "image_url": "https://wger.de/media/exercise-images/32/Squats-1.png",
  "muscle_group": "Quads, glutes, core",
  "sets": "3",
  "reps": "10–12",
  "rest_sec": 90,
  "form_cues": "Hold 1 DB at chest, feet shoulder-width, knees track over toes, chest up",
  "progression": "10 kg → 14 kg → 21 kg → pause at bottom 3 sec",
  "phase": 1
}
```

### `data/supplements.json` (sample entry)
```json
{
  "time": "With breakfast",
  "name": "Vitamin D3 2000 IU",
  "with_food": true,
  "reason": "Fat-soluble — needs dietary fat for absorption",
  "verdict": "Excellent",
  "verdict_detail": "Hamburg at 53°N — virtually zero Vitamin D synthesis Oct–Apr"
}
```

### `data/meals.json` (sample entry)
```json
{
  "day_type": "training",
  "meals": [
    {
      "name": "Breakfast",
      "time": "07:30",
      "foods": "80g oats + 250ml milk + 3 eggs + 1 banana",
      "kcal": 580,
      "protein_g": 30
    }
  ],
  "targets": { "kcal": 2500, "protein_g": 140, "carbs_g": 280, "fat_g": 75 }
}
```

### `data/products.json` (sample entry)
```json
{
  "category": "hair",
  "name": "Cien Nature Bio-Mandel Shampoo",
  "verdict": "Good",
  "verdict_detail": "Hydrolyzed proteins reduce breakage. No silicones. Does not address AGA.",
  "usage": "Rotate with ketoconazole shampoo on non-keto wash days",
  "where": "Lidl",
  "cost": "€1.99"
}
```

---

## Deployment — Render

### Additional files

**`requirements.txt`** — include:
```
flask
flask-sqlalchemy
gunicorn
psycopg2-binary
requests
python-dotenv
```

**`render.yaml`**:
```yaml
services:
  - type: web
    name: lifestyle-dashboard
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn "app:create_app()"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: lifestyle-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: PROGRAM_START_DATE
        value: "2026-06-02"

databases:
  - name: lifestyle-db
    plan: free
```

**`.env`** (local only, add to `.gitignore`):
```
DATABASE_URL=sqlite:///dev.db
SECRET_KEY=dev-secret-change-me
PROGRAM_START_DATE=2026-06-02
```

**`config.py`**:
```python
import os
class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    PROGRAM_START_DATE = os.environ.get('PROGRAM_START_DATE', '2026-06-02')
```

Note: Render's PostgreSQL connection string starts with `postgres://` but SQLAlchemy requires `postgresql://`. Fix in `config.py`:
```python
uri = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')
if uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)
SQLALCHEMY_DATABASE_URI = uri
```

### Step-by-step deployment

1. **Push to GitHub**
   - Create a new repo on GitHub: `lifestyle-dashboard`
   - `git remote add origin https://github.com/<your-username>/lifestyle-dashboard.git`
   - `git push -u origin main`

2. **Create Render account** at render.com (free)

3. **New Web Service**
   - Dashboard → New → Web Service
   - Connect GitHub → select `lifestyle-dashboard` repo
   - Render auto-detects Python

4. **Configure the service**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn "app:create_app()"`
   - Or: just push `render.yaml` — Render reads it automatically (Blueprint deploy)

5. **Add PostgreSQL**
   - New → PostgreSQL → free plan → name it `lifestyle-db`
   - In your Web Service → Environment → add `DATABASE_URL` → link to `lifestyle-db` internal connection string

6. **Init the database on first deploy**
   - In Render Web Service → Shell (or add a one-time job):
   ```bash
   flask shell
   >>> from app import db
   >>> db.create_all()
   ```
   - Or add to `app.py` in `create_app()`: `db.create_all()` inside app context (safe for idempotent use)

7. **Every subsequent deploy**: push to GitHub → Render auto-redeploys in ~2 min → live at `https://lifestyle-dashboard.onrender.com`

### Local development workflow
```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env           # fill in values
flask run --debug
```

---

## Build Strategy

**Approach A — Full scaffold, then fill content page by page.**

Phase 1 (first session):
- Flask app factory + config
- All 4 DB models
- All 9 blueprints registered (placeholder templates for 8, full content for overview)
- Base template with sidebar, theme toggle, all nav links
- All 4 JSON data files populated with content from spec
- `render.yaml`, `requirements.txt`, `.gitignore`, `.env.example`
- `scripts/fetch_wger_images.py` — populates `image_url` in exercises.json

Then each subsequent section built fully in order:
Schedule → Workouts → Nutrition → Supplements → Hair → Skin → Shopping → Myths
