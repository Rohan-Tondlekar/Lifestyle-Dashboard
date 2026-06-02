# Lifestyle Dashboard Phase 1 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold the complete Flask application with all 9 blueprint routes, SQLite/PostgreSQL database models, 4 fully populated JSON data files, a working overview dashboard page with dark/light theme toggle and hover-expanding sidebar, and Render deployment config.

**Architecture:** `create_app()` factory in `app.py` registers 9 blueprints and initializes Flask-SQLAlchemy. All static coaching content lives in `data/*.json` and is loaded per-request in route functions. User-generated data (logs, body metrics) is stored in SQLite locally and PostgreSQL on Render. The base Jinja2 template implements a 56px icon sidebar that expands to 200px on hover (CSS overlay, no layout shift) using Tailwind's `group-hover` class, with dark/light mode driven by a `dark` class on `<html>`.

**Tech Stack:** Python 3.11+ · Flask 3.0 · Flask-SQLAlchemy 3.1 · SQLite (local) / PostgreSQL (Render) · Jinja2 · Tailwind CSS Play CDN · Chart.js CDN · gunicorn · pytest + pytest-flask

---

## File Map

```
app.py
config.py
requirements.txt
pytest.ini
render.yaml                        ← overwrite existing
.env.example
.gitignore
models/__init__.py
models/workout.py
models/nutrition.py
models/body.py
routes/__init__.py
routes/dashboard.py
routes/schedule.py
routes/workouts.py
routes/nutrition.py
routes/supplements.py
routes/hair.py
routes/skin.py
routes/shopping.py
routes/myths.py
templates/base.html
templates/dashboard/overview.html
templates/schedule/index.html
templates/workouts/plan.html
templates/nutrition/meals.html
templates/supplements/schedule.html
templates/hair/routine.html
templates/skin/routine.html
templates/shopping/list.html
templates/myths/index.html
static/css/custom.css
static/js/theme.js
static/js/charts.js
static/js/macro_tracker.js
data/exercises.json
data/supplements.json
data/meals.json
data/products.json
scripts/fetch_wger_images.py
tests/__init__.py
tests/conftest.py
tests/test_models.py
tests/test_app.py
tests/test_routes.py
tests/test_dashboard.py
```

---

### Task 1: Project Scaffold

**Files:** `requirements.txt`, `pytest.ini`, `.env.example`, `.gitignore`, `config.py`, `render.yaml`

- [ ] **Step 1: Write requirements.txt**

```
flask==3.0.3
flask-sqlalchemy==3.1.1
gunicorn==22.0.0
psycopg2-binary==2.9.9
requests==2.32.3
python-dotenv==1.0.1
pytest==8.2.2
pytest-flask==1.3.0
```

- [ ] **Step 2: Write pytest.ini**

```ini
[pytest]
testpaths = tests
```

- [ ] **Step 3: Write .env.example**

```
DATABASE_URL=sqlite:///dev.db
SECRET_KEY=dev-secret-key-change-me
PROGRAM_START_DATE=2026-06-02
```

- [ ] **Step 4: Write .gitignore**

```
venv/
__pycache__/
*.pyc
*.pyo
.env
instance/
dev.db
.pytest_cache/
*.egg-info/
dist/
build/
.superpowers/
```

- [ ] **Step 5: Write config.py**

```python
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    _uri = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')
    if _uri.startswith('postgres://'):
        _uri = _uri.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = _uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
    PROGRAM_START_DATE = os.environ.get('PROGRAM_START_DATE', '2026-06-02')
```

- [ ] **Step 6: Overwrite render.yaml**

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

- [ ] **Step 7: Create and activate virtual environment, install deps**

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Expected: no errors, all 8 packages installed.

---

### Task 2: Database Models

**Files:** `models/__init__.py`, `models/workout.py`, `models/nutrition.py`, `models/body.py`, `tests/__init__.py`, `tests/conftest.py`, `tests/test_models.py`

- [ ] **Step 1: Write models/__init__.py**

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```

- [ ] **Step 2: Write models/workout.py**

```python
from models import db


class WorkoutLog(db.Model):
    __tablename__ = 'workout_log'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    day_type = db.Column(db.String(20))
    completed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    sets = db.relationship('ExerciseSet', backref='workout', lazy=True,
                           cascade='all, delete-orphan')


class ExerciseSet(db.Model):
    __tablename__ = 'exercise_set'
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout_log.id'), nullable=False)
    exercise_name = db.Column(db.String(100), nullable=False)
    weight_kg = db.Column(db.Float)
    reps = db.Column(db.Integer)
    set_number = db.Column(db.Integer)
```

- [ ] **Step 3: Write models/nutrition.py**

```python
from models import db


class MealLog(db.Model):
    __tablename__ = 'meal_log'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    meal_name = db.Column(db.String(50))
    protein_g = db.Column(db.Float, default=0)
    carbs_g = db.Column(db.Float, default=0)
    fat_g = db.Column(db.Float, default=0)
    kcal = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)
```

- [ ] **Step 4: Write models/body.py**

```python
from models import db


class BodyMetric(db.Model):
    __tablename__ = 'body_metric'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    weight_kg = db.Column(db.Float)
    notes = db.Column(db.Text)
```

- [ ] **Step 5: Write tests/__init__.py** (empty file for package discovery)

```python
```

- [ ] **Step 6: Write tests/conftest.py**

Note: imports `app` which doesn't exist until Task 3 — this file will cause import errors until then.

```python
import pytest
from app import create_app
from models import db as _db


@pytest.fixture
def app():
    test_app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret',
        'PROGRAM_START_DATE': '2026-06-02',
    })
    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
```

- [ ] **Step 7: Write tests/test_models.py**

```python
from models import db
from models.body import BodyMetric
from models.nutrition import MealLog
from models.workout import ExerciseSet, WorkoutLog


def test_create_body_metric(app):
    metric = BodyMetric(date='2026-06-02', weight_kg=59.0)
    db.session.add(metric)
    db.session.commit()
    fetched = BodyMetric.query.first()
    assert fetched.weight_kg == 59.0
    assert fetched.date == '2026-06-02'


def test_create_meal_log(app):
    meal = MealLog(date='2026-06-02', meal_name='Breakfast',
                   protein_g=30.0, carbs_g=60.0, fat_g=10.0, kcal=450)
    db.session.add(meal)
    db.session.commit()
    fetched = MealLog.query.first()
    assert fetched.protein_g == 30.0
    assert fetched.meal_name == 'Breakfast'


def test_create_workout_with_sets(app):
    log = WorkoutLog(date='2026-06-02', day_type='upper', completed=True)
    db.session.add(log)
    db.session.flush()
    s = ExerciseSet(workout_id=log.id, exercise_name='DB Shoulder Press',
                    weight_kg=8.0, reps=10, set_number=1)
    db.session.add(s)
    db.session.commit()
    fetched = WorkoutLog.query.first()
    assert fetched.completed is True
    assert len(fetched.sets) == 1
    assert fetched.sets[0].exercise_name == 'DB Shoulder Press'


def test_body_metric_notes_defaults_null(app):
    metric = BodyMetric(date='2026-06-02', weight_kg=60.0)
    db.session.add(metric)
    db.session.commit()
    assert BodyMetric.query.first().notes is None
```

---

### Task 3: Flask App Factory

**Files:** `routes/__init__.py`, `app.py`, `tests/test_app.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_app.py
from models.body import BodyMetric
from models.nutrition import MealLog
from models.workout import ExerciseSet, WorkoutLog


def test_app_creates_successfully(app):
    assert app is not None
    assert app.config['TESTING'] is True


def test_all_tables_queryable(app):
    assert BodyMetric.query.count() == 0
    assert MealLog.query.count() == 0
    assert WorkoutLog.query.count() == 0
    assert ExerciseSet.query.count() == 0
```

- [ ] **Step 2: Run test — confirm it fails**

```bash
pytest tests/test_app.py -v
```

Expected: `ModuleNotFoundError: No module named 'app'`

- [ ] **Step 3: Write routes/__init__.py** (empty)

```python
```

- [ ] **Step 4: Write app.py**

```python
from flask import Flask

from config import Config
from models import db


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config:
        app.config.update(config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    from routes.dashboard import dashboard_bp
    from routes.hair import hair_bp
    from routes.myths import myths_bp
    from routes.nutrition import nutrition_bp
    from routes.schedule import schedule_bp
    from routes.shopping import shopping_bp
    from routes.skin import skin_bp
    from routes.supplements import supplements_bp
    from routes.workouts import workouts_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(workouts_bp)
    app.register_blueprint(nutrition_bp)
    app.register_blueprint(supplements_bp)
    app.register_blueprint(hair_bp)
    app.register_blueprint(skin_bp)
    app.register_blueprint(shopping_bp)
    app.register_blueprint(myths_bp)

    return app
```

- [ ] **Step 5: Run test — confirm it fails (blueprint files missing)**

```bash
pytest tests/test_app.py -v
```

Expected: `ModuleNotFoundError: No module named 'routes.dashboard'`

This is expected — route files are created in Task 9. Continue.

---

### Task 4: JSON Data — Exercises & Supplements

**Files:** `data/exercises.json`, `data/supplements.json`

- [ ] **Step 1: Create data/ directory**

```bash
mkdir data
```

- [ ] **Step 2: Write data/exercises.json**

```json
{
  "phase1": [
    {
      "name": "Push-up",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Chest, triceps, anterior deltoid",
      "sets": "3",
      "reps": "10–12",
      "rest_sec": 75,
      "form_cues": "Hands shoulder-width, elbows 45° from body, lower chest to ~2 cm from floor, full lockout at top",
      "progression": "Standard → feet elevated → archer push-ups → add DB row superset"
    },
    {
      "name": "DB Goblet Squat",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Quads, glutes, core",
      "sets": "3",
      "reps": "10–12",
      "rest_sec": 90,
      "form_cues": "Hold 1 DB at chest, feet shoulder-width, knees track over toes, sit back not just down, chest up",
      "progression": "10 kg → 14 kg → 21 kg → pause at bottom 3 sec"
    },
    {
      "name": "DB Romanian Deadlift",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Hamstrings, glutes, lower back",
      "sets": "3",
      "reps": "10–12",
      "rest_sec": 90,
      "form_cues": "Hinge at hips, soft knee bend, DBs travel close to legs, feel hamstring stretch at bottom, drive hips forward at top",
      "progression": "12 kg → 16 kg → 21 kg → single-leg variant"
    },
    {
      "name": "DB Bent-over Row",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Lats, rhomboids, biceps",
      "sets": "3",
      "reps": "10–12",
      "rest_sec": 90,
      "form_cues": "Hinge 45°, DBs hang, pull elbows to hips, squeeze shoulder blades at top, controlled negative",
      "progression": "8 kg → 14 kg → 21 kg → chest-supported variant"
    },
    {
      "name": "DB Shoulder Press",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Deltoids, upper traps, triceps",
      "sets": "3",
      "reps": "10–12",
      "rest_sec": 90,
      "form_cues": "Seated or standing, DBs at ear height, press straight up, slight forward lean, no flare",
      "progression": "8 kg → 12 kg → 18 kg → Arnold press"
    },
    {
      "name": "DB Bicep Curl",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Biceps, brachialis",
      "sets": "3",
      "reps": "10–12",
      "rest_sec": 60,
      "form_cues": "Elbows pinned to sides, full ROM, 3 sec negative, no body swing",
      "progression": "8 kg → 12 kg → 16 kg → hammer curl superset"
    },
    {
      "name": "Plank",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Core — transverse abdominis, obliques",
      "sets": "3",
      "reps": "20–45 sec",
      "rest_sec": 60,
      "form_cues": "Forearms down, body flat, glutes squeezed, hips don't sag or pike, breathe normally",
      "progression": "20 sec → 45 sec → 60 sec → RKC plank"
    },
    {
      "name": "Dead Bug",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Deep core, anti-extension",
      "sets": "3",
      "reps": "10–12",
      "rest_sec": 60,
      "form_cues": "Lower back pressed into mat, extend opposite arm and leg, breathe out on extension, never lose lower back contact",
      "progression": "Bodyweight → add 2 kg DB in extended hand"
    },
    {
      "name": "DB Lateral Raise",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Medial deltoid",
      "sets": "3",
      "reps": "10–12",
      "rest_sec": 60,
      "form_cues": "Slight forward lean, raise to shoulder height, thumbs slightly down, 3 sec descent, no momentum",
      "progression": "4 kg → 8 kg → 12 kg → 4 sec up / 4 sec down tempo"
    },
    {
      "name": "Hip Thrust (mat)",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Glutes, hamstrings",
      "sets": "3",
      "reps": "10–12",
      "rest_sec": 75,
      "form_cues": "Upper back on mat edge, feet flat, drive hips up squeezing glutes at top, hold 1 sec, lower controlled",
      "progression": "Bodyweight → DB on hips → two DBs → pause variant"
    }
  ],
  "phase2_upper": [
    {
      "name": "DB Bench Press",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Chest, triceps, anterior deltoid",
      "sets": "4",
      "reps": "8–10",
      "rest_sec": 90,
      "form_cues": "Lie on mat, DBs at chest, press up and slightly in, lower with control, slight arch in lower back",
      "progression": "10 kg → 14 kg → 18 kg → pause at chest 2 sec"
    },
    {
      "name": "DB Row",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Lats, rhomboids, biceps",
      "sets": "4",
      "reps": "10",
      "rest_sec": 90,
      "form_cues": "Hinge 45°, pull elbows to hips, squeeze at top, 3 sec negative",
      "progression": "14 kg → 18 kg → 21 kg"
    },
    {
      "name": "Incline Push-up",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Lower chest, triceps",
      "sets": "3",
      "reps": "12",
      "rest_sec": 60,
      "form_cues": "Hands on elevated surface (chair height), body straight, elbows 45° from body",
      "progression": "Chair height → lower surface → deficit push-up"
    },
    {
      "name": "DB Shoulder Press",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Deltoids, upper traps, triceps",
      "sets": "3",
      "reps": "10",
      "rest_sec": 90,
      "form_cues": "DBs at ear height, press straight up, control the descent",
      "progression": "10 kg → 14 kg → 18 kg"
    },
    {
      "name": "DB Lateral Raise",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Medial deltoid",
      "sets": "3",
      "reps": "12–15",
      "rest_sec": 60,
      "form_cues": "Slight forward lean, raise to shoulder height, 3 sec descent, no momentum",
      "progression": "6 kg → 10 kg → 12 kg"
    },
    {
      "name": "DB Bicep Curl",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Biceps, brachialis",
      "sets": "3",
      "reps": "12",
      "rest_sec": 60,
      "form_cues": "Elbows pinned, full ROM, 3 sec negative",
      "progression": "10 kg → 14 kg → 16 kg"
    },
    {
      "name": "DB Tricep Overhead Extension",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Triceps (long head)",
      "sets": "3",
      "reps": "12",
      "rest_sec": 60,
      "form_cues": "Hold 1 DB with both hands overhead, elbows close to head, lower DB behind head, press back up",
      "progression": "8 kg → 12 kg → 16 kg"
    },
    {
      "name": "Face Pull (towel/band)",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Rear deltoid, external rotators, upper traps",
      "sets": "3",
      "reps": "15",
      "rest_sec": 60,
      "form_cues": "Pull to face level, elbows high and wide, external rotate at end of movement",
      "progression": "Resistance band → heavier band"
    }
  ],
  "phase2_lower": [
    {
      "name": "DB Goblet Squat",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Quads, glutes, core",
      "sets": "4",
      "reps": "10",
      "rest_sec": 90,
      "form_cues": "Hold 1 DB at chest, feet shoulder-width, knees track over toes, full depth, chest up",
      "progression": "14 kg → 18 kg → 21 kg"
    },
    {
      "name": "DB Romanian Deadlift",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Hamstrings, glutes, lower back",
      "sets": "4",
      "reps": "10",
      "rest_sec": 90,
      "form_cues": "Hinge at hips, feel hamstring stretch at bottom, drive hips forward",
      "progression": "16 kg → 18 kg → 21 kg"
    },
    {
      "name": "DB Reverse Lunge",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Quads, glutes, hamstrings",
      "sets": "3",
      "reps": "10 each leg",
      "rest_sec": 75,
      "form_cues": "Step back, lower back knee toward floor, keep front shin vertical, push through front heel to return",
      "progression": "Bodyweight → 8 kg DBs → 12 kg DBs"
    },
    {
      "name": "Hip Thrust",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Glutes, hamstrings",
      "sets": "3",
      "reps": "12",
      "rest_sec": 75,
      "form_cues": "Upper back on mat, DB on hips, drive up, squeeze glutes at top, hold 1 sec",
      "progression": "DB on hips: 12 kg → 16 kg → 21 kg"
    },
    {
      "name": "DB Calf Raise",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Gastrocnemius, soleus",
      "sets": "3",
      "reps": "15",
      "rest_sec": 60,
      "form_cues": "Stand on edge of step, full range of motion, hold at top 1 sec",
      "progression": "Bodyweight → 8 kg DBs → 14 kg DBs"
    },
    {
      "name": "Plank",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Core — transverse abdominis, obliques",
      "sets": "3",
      "reps": "45–60 sec",
      "rest_sec": 60,
      "form_cues": "Forearms down, body flat, glutes squeezed, breathe normally",
      "progression": "60 sec → RKC plank → plank with reach"
    },
    {
      "name": "Hanging Leg Raise",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Hip flexors, lower abs",
      "sets": "3",
      "reps": "10",
      "rest_sec": 60,
      "form_cues": "Hang from bar, raise legs to 90°, control the descent, don't swing",
      "progression": "Knee raises → straight leg raises → L-sit hold"
    },
    {
      "name": "Bicycle Crunches",
      "wger_id": null,
      "image_url": null,
      "muscle_group": "Obliques, rectus abdominis",
      "sets": "3",
      "reps": "20",
      "rest_sec": 60,
      "form_cues": "Hands behind head, rotate elbow to opposite knee, extend other leg, slow and controlled",
      "progression": "Slow tempo → add hold at peak contraction"
    }
  ]
}
```

- [ ] **Step 3: Write data/supplements.json**

```json
{
  "timing_table": [
    {
      "time": "With breakfast",
      "supplement": "Vitamin D3 2000 IU",
      "with_food": true,
      "reason": "Fat-soluble — needs dietary fat for ~50% better absorption"
    },
    {
      "time": "With lunch",
      "supplement": "Zinc 15–25 mg",
      "with_food": true,
      "reason": "Prevents nausea; spaced 4–5 hrs from Magnesium to avoid competition"
    },
    {
      "time": "Post-workout",
      "supplement": "Whey Protein 25–30 g",
      "with_food": false,
      "reason": "Leucine delivery during anabolic window. With water or milk."
    },
    {
      "time": "With dinner",
      "supplement": "Magnesium 500 mg",
      "with_food": true,
      "reason": "Reduces GI side effects; sleep benefit via GABA modulation"
    },
    {
      "time": "With dinner",
      "supplement": "Omega-3 2–3 g (EPA+DHA)",
      "with_food": true,
      "reason": "Fat-soluble; better absorbed with a fat-containing meal"
    },
    {
      "time": "Before bed (optional)",
      "supplement": "Quark 200 g",
      "with_food": false,
      "reason": "Slow-release casein for overnight muscle protein synthesis"
    }
  ],
  "current_products": [
    {
      "name": "Doppelherz Vitamin D3 2000 IU",
      "verdict": "Excellent",
      "verdict_color": "green",
      "dosage": "1 tablet/day with breakfast",
      "mechanism": "D3 is the active form (vs D2). Supports calcium absorption, immune function, and muscle protein synthesis.",
      "note": "Hamburg at 53°N — virtually zero Vitamin D synthesis October–April.",
      "interactions": "Take in the morning. Do not take within 2 hours of Magnesium."
    },
    {
      "name": "Abtei Magnesium 500 Plus (with B-vitamins, Biotin 150 µg, B12 20 µg)",
      "verdict": "Very Good",
      "verdict_color": "green",
      "dosage": "1 tablet with dinner",
      "mechanism": "Magnesium supports ATP synthesis, muscle contraction/relaxation, and sleep via GABA modulation. Biotin supports hair keratin production. B12 supports red blood cell formation for running stamina.",
      "note": "If loose stools occur, split dose (morning + evening).",
      "interactions": "Do not take within 2 hours of Vitamin D3. Space Zinc by 4–5 hours."
    }
  ],
  "missing_supplements": [
    {
      "name": "Omega-3 (EPA/DHA)",
      "mechanism": "Anti-inflammatory, supports muscle protein synthesis, scalp sebum quality, and skin barrier. Hamburg diet is often low in fatty fish.",
      "dose": "2–3 g EPA+DHA/day with a meal",
      "where": "dm: Doppelherz Omega-3. Rossmann: Abtei Omega-3.",
      "cost": "~€8–12/month",
      "priority": "High"
    },
    {
      "name": "Zinc 15–25 mg",
      "mechanism": "Critical for testosterone production, immune function, and hair follicle health. Zinc deficiency is a leading reversible cause of hair loss. Not in current stack.",
      "dose": "15–25 mg with food (not on empty stomach — causes nausea)",
      "where": "dm: Doppelherz Zink. Rossmann: Abtei Zink.",
      "cost": "~€5–7",
      "priority": "High"
    },
    {
      "name": "Whey Protein",
      "mechanism": "At 59 kg targeting muscle gain, 130–145 g protein/day is needed. Difficult from food alone. Leucine threshold ~2.5 g per meal triggers muscle protein synthesis.",
      "dose": "25–30 g post-workout",
      "where": "Lidl: Beavita/Powerstar. dm: ESN Whey. iHerb: ON Gold Standard.",
      "cost": "~€20–35/kg",
      "priority": "High"
    },
    {
      "name": "Creatine Monohydrate",
      "mechanism": "Most-studied ergogenic aid. Increases phosphocreatine stores, enabling more reps per set. Accelerates lean muscle gain by ~20% vs training alone. Safe at all studied doses.",
      "dose": "3–5 g/day, any time, with water",
      "where": "Amazon.de: Creapure brand.",
      "cost": "~€15–20/500g",
      "priority": "Optional, high value"
    }
  ]
}
```

---

### Task 5: JSON Data — Meals & Products

**Files:** `data/meals.json`, `data/products.json`

- [ ] **Step 1: Write data/meals.json**

```json
{
  "day_plans": [
    {
      "day_type": "training",
      "label": "Training Day",
      "targets": { "kcal": 2500, "protein_g": 140, "carbs_g": 280, "fat_g": 75 },
      "meals": [
        { "name": "Breakfast", "time": "07:30", "foods": "80g oats + 250ml milk + 3 eggs + 1 banana", "kcal": 580, "protein_g": 30 },
        { "name": "Post-workout", "time": "10:00", "foods": "Whey scoop + 200g Quark + fruit", "kcal": 400, "protein_g": 35 },
        { "name": "Lunch", "time": "13:00", "foods": "150g chicken/salmon + 150g rice + salad + olive oil", "kcal": 650, "protein_g": 45 },
        { "name": "Snack", "time": "16:00", "foods": "Hüttenkäse 150g + crackers OR nuts 30g + apple", "kcal": 300, "protein_g": 15 },
        { "name": "Dinner", "time": "18:30", "foods": "200g beef/turkey + 200g sweet potato + vegetables", "kcal": 600, "protein_g": 40 },
        { "name": "Before bed (optional)", "time": "21:30", "foods": "200g Quark + 1 tsp honey", "kcal": 220, "protein_g": 27 }
      ]
    },
    {
      "day_type": "rest",
      "label": "Rest Day",
      "note": "Slightly lower calories, same protein target. Remove one carb serving. Keep all protein sources.",
      "targets": { "kcal": 2150, "protein_g": 140, "carbs_g": 230, "fat_g": 65 },
      "meals": [
        { "name": "Breakfast", "time": "07:30", "foods": "3 eggs + 200ml milk + 50g oats", "kcal": 460, "protein_g": 28 },
        { "name": "Lunch", "time": "13:00", "foods": "150g chicken + 100g rice + salad + olive oil", "kcal": 530, "protein_g": 45 },
        { "name": "Snack", "time": "16:00", "foods": "200g Quark + fruit", "kcal": 280, "protein_g": 26 },
        { "name": "Dinner", "time": "18:30", "foods": "200g beef/turkey + vegetables + 100g sweet potato", "kcal": 480, "protein_g": 40 },
        { "name": "Before bed (optional)", "time": "21:30", "foods": "200g Quark", "kcal": 200, "protein_g": 24 }
      ]
    },
    {
      "day_type": "run",
      "label": "Run Day",
      "note": "More carbs pre-run, lighter on fat. No heavy fat in pre-run meal — delays gastric emptying and causes GI distress during running.",
      "targets": { "kcal": 2400, "protein_g": 140, "carbs_g": 270, "fat_g": 70 },
      "meals": [
        { "name": "Breakfast (pre-run)", "time": "07:30", "foods": "80g oats + 250ml milk + 1 banana + 2 eggs (no added fat)", "kcal": 520, "protein_g": 24 },
        { "name": "Post-run", "time": "09:00", "foods": "Whey scoop + 200g Quark + fruit", "kcal": 400, "protein_g": 35 },
        { "name": "Lunch", "time": "13:00", "foods": "150g chicken/tuna + 150g rice + salad + olive oil", "kcal": 600, "protein_g": 45 },
        { "name": "Snack", "time": "16:00", "foods": "Hüttenkäse 150g + crackers", "kcal": 280, "protein_g": 18 },
        { "name": "Dinner", "time": "18:30", "foods": "200g turkey + 200g sweet potato + vegetables", "kcal": 580, "protein_g": 40 },
        { "name": "Before bed (optional)", "time": "21:30", "foods": "200g Quark", "kcal": 200, "protein_g": 24 }
      ]
    }
  ],
  "food_database": [
    { "food": "Magerquark", "protein_per_100g": 12, "cost": "€0.79–1.19/500g", "where": "Überall" },
    { "food": "Hühnerbrust", "protein_per_100g": 31, "cost": "€4–6/kg", "where": "Lidl, Kaufland" },
    { "food": "Eier", "protein_per_100g": 13, "cost": "€2–3/10 Stk", "where": "Überall" },
    { "food": "Rote Linsen", "protein_per_100g": 26, "cost": "€1.50–2/500g", "where": "Lidl, Aldi" },
    { "food": "Thunfisch (Dose)", "protein_per_100g": 26, "cost": "€0.99–1.50/Dose", "where": "Überall" },
    { "food": "Hüttenkäse", "protein_per_100g": 12, "cost": "€1–1.50/250g", "where": "dm, Lidl" }
  ],
  "weekly_prep": [
    "500g Hühnenbrust in oven (25 min, 200°C) → 3–4 portions",
    "500g Vollkornreis cooked → keeps 4–5 days",
    "8 hard-boiled eggs → grab-and-go protein",
    "Big pot of Linsensuppe → 4 portions for ~€2",
    "Wash and chop vegetables"
  ]
}
```

- [ ] **Step 2: Write data/products.json**

```json
[
  {
    "category": "hair",
    "name": "Cien Nature Bio-Mandel Shampoo",
    "verdict": "Good",
    "verdict_color": "green",
    "verdict_detail": "Hydrolyzed proteins coat shaft, reduce breakage. No silicones (positive for scalp). Does nothing to address androgenic alopecia specifically.",
    "usage": "Rotate with ketoconazole shampoo on non-keto wash days",
    "where": "Lidl",
    "cost": "~€1.99"
  },
  {
    "category": "hair",
    "name": "Ketoconazole Shampoo 2% (Nizoral / Terzolin)",
    "verdict": "Evidence-backed",
    "verdict_color": "blue",
    "verdict_detail": "Two mechanisms: (1) antifungal — reduces Malassezia yeast, which drives follicle inflammation. (2) Mild anti-androgenic — weakly blocks DHT at follicle level. Studies show comparable results to 2% minoxidil in some trials.",
    "usage": "2–3×/week, leave on scalp 3–5 minutes before rinsing",
    "where": "Pharmacy / Amazon.de",
    "cost": "€15–18"
  },
  {
    "category": "hair",
    "name": "Pantene Pro-V Keratin Protect Oil",
    "verdict": "Use with caution",
    "verdict_color": "amber",
    "verdict_detail": "Primarily silicone-based (cyclopentasiloxane, dimethicone). Coats shaft for shine but does not penetrate. Silicone buildup on scalp can contribute to follicle clogging with overuse.",
    "usage": "1–2 drops on ends only. Never apply to scalp.",
    "where": "Supermarket",
    "cost": "~€5"
  },
  {
    "category": "hair",
    "name": "Silicone Scalp Massage Brush",
    "verdict": "Recommended",
    "verdict_color": "green",
    "verdict_detail": "Scalp massage increases blood flow to dermal papilla, improving nutrient delivery to follicles. A 2016 Japanese study showed 4 min daily scalp massage increased hair thickness over 6 months.",
    "usage": "During shampooing — 2–3 min circular motions. Light pressure.",
    "where": "Various",
    "cost": "€3–8"
  },
  {
    "category": "skin",
    "name": "Lacura Med Körperlotion 10% Urea",
    "verdict": "Excellent",
    "verdict_color": "green",
    "verdict_detail": "Urea at 10% is a keratolytic humectant — breaks down excess keratin buildup AND draws water into the stratum corneum. Shea butter adds an occlusive layer. Clinical standard for xerosis.",
    "usage": "Apply within 3 minutes of stepping out of shower to damp skin",
    "where": "Aldi",
    "cost": "~€3"
  },
  {
    "category": "skin",
    "name": "Lacura Med Fussbalsam Glycerin 10% Urea + Panthenol",
    "verdict": "Excellent",
    "verdict_color": "green",
    "verdict_detail": "Same urea keratolysis. Panthenol (pro-vitamin B5) converts to pantothenic acid in skin, accelerates wound healing. Glycerin holds water.",
    "usage": "Before bed with socks on — overnight occlusion doubles efficacy",
    "where": "Aldi",
    "cost": "~€2"
  },
  {
    "category": "skin",
    "name": "Lacura Med Handcreme Vitamin B3 + Urea 5%",
    "verdict": "Good",
    "verdict_color": "green",
    "verdict_detail": "Niacinamide (B3) strengthens skin barrier by upregulating ceramide synthesis. 5% Urea appropriate for thinner hand skin. Fragrance-free — lower irritation risk.",
    "usage": "After handwashing, as needed",
    "where": "Aldi",
    "cost": "~€2"
  },
  {
    "category": "skin",
    "name": "NIVEA Reichhaltige Body Milk (Hyaluron + Mandelöl)",
    "verdict": "Okay",
    "verdict_color": "amber",
    "verdict_detail": "Hyaluronic acid in body lotions is largely a marketing angle — the molecule is too large to penetrate skin topically. Functions as a surface humectant only.",
    "usage": "On less-dry days or less-affected areas",
    "where": "Supermarket / dm",
    "cost": "~€5"
  },
  {
    "category": "skin",
    "name": "Lacura Sun LSF 50 Sonnenspray",
    "verdict": "Excellent",
    "verdict_color": "green",
    "verdict_detail": "Rated 'Sehr Gut 1.5' by Stiftung Warentest. SPF mandatory year-round — UV causes skin barrier degradation through cloud cover.",
    "usage": "Body SPF. Apply generously before outdoor exposure.",
    "where": "Aldi",
    "cost": "~€3"
  },
  {
    "category": "skin",
    "name": "NIVEA Sun 50+ Citracell",
    "verdict": "Excellent",
    "verdict_color": "green",
    "verdict_detail": "Vitamin C (antioxidant synergistic with SPF) and Hyaluron. Formulated for face — no white cast.",
    "usage": "Face SPF daily — every single day, including cloudy days",
    "where": "dm / Rossmann",
    "cost": "~€8"
  }
]
```

---

### Task 6: Wger Image Fetch Script

**Files:** `scripts/fetch_wger_images.py`

- [ ] **Step 1: Create scripts/ directory**

```bash
mkdir scripts
```

- [ ] **Step 2: Write scripts/fetch_wger_images.py**

```python
#!/usr/bin/env python3
"""
One-time script: resolves Wger exercise image URLs and writes them to data/exercises.json.
Run from project root: python scripts/fetch_wger_images.py
"""
import json
import time
from pathlib import Path
from typing import Optional

import requests

EXERCISES_FILE = Path(__file__).parent.parent / 'data' / 'exercises.json'
WGER_SEARCH = 'https://wger.de/api/v2/exercise/search/'
WGER_IMAGES = 'https://wger.de/api/v2/exerciseimage/'
WGER_BASE = 'https://wger.de'


def search_exercise(name: str) -> Optional[int]:
    try:
        resp = requests.get(
            WGER_SEARCH,
            params={'term': name, 'language': 'english', 'format': 'json'},
            timeout=10,
        )
        resp.raise_for_status()
        suggestions = resp.json().get('suggestions', [])
        if suggestions:
            return suggestions[0]['data']['base_id']
    except Exception as e:
        print(f'  Search error for "{name}": {e}')
    return None


def get_image_url(base_id: int) -> Optional[str]:
    try:
        resp = requests.get(
            WGER_IMAGES,
            params={'exercise_base': base_id, 'format': 'json'},
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json().get('results', [])
        if results:
            path = results[0]['image']
            return path if path.startswith('http') else WGER_BASE + path
    except Exception as e:
        print(f'  Image error for base_id {base_id}: {e}')
    return None


def process_list(exercises: list) -> int:
    updated = 0
    for ex in exercises:
        if ex.get('image_url'):
            print(f'  Skip (cached): {ex["name"]}')
            continue
        print(f'Fetching: {ex["name"]}')
        base_id = search_exercise(ex['name'])
        if base_id:
            url = get_image_url(base_id)
            ex['wger_id'] = base_id
            ex['image_url'] = url
            print(f'  → {url or "no image found"}')
            updated += 1
        else:
            print(f'  → not found in Wger')
        time.sleep(0.5)
    return updated


def main():
    with open(EXERCISES_FILE, encoding='utf-8') as f:
        data = json.load(f)

    total = 0
    for section in ('phase1', 'phase2_upper', 'phase2_lower'):
        print(f'\n=== {section} ===')
        total += process_list(data[section])

    with open(EXERCISES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f'\nDone. Updated {total} exercises.')


if __name__ == '__main__':
    main()
```

- [ ] **Step 3: Run the script**

```bash
python scripts/fetch_wger_images.py
```

Expected: runs ~30–60 sec, prints each exercise name, updates `data/exercises.json` with `image_url` values. Bodyweight exercises (Plank, Dead Bug) may return "not found" — that's fine; the workouts template handles `null` with a placeholder.

---

### Task 7: Static Files

**Files:** `static/css/custom.css`, `static/js/theme.js`, `static/js/charts.js`, `static/js/macro_tracker.js`

- [ ] **Step 1: Create static directories**

```bash
mkdir -p static/css static/js
```

- [ ] **Step 2: Write static/css/custom.css**

```css
body {
    overflow-x: hidden;
}
```

- [ ] **Step 3: Write static/js/theme.js**

```javascript
function toggleTheme() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    updateThemeButton(isDark);
}

function updateThemeButton(isDark) {
    const icon = document.getElementById('theme-icon');
    const label = document.getElementById('theme-label');
    if (icon) icon.textContent = isDark ? '☀️' : '🌙';
    if (label) label.textContent = isDark ? 'Light Mode' : 'Dark Mode';
}

document.addEventListener('DOMContentLoaded', function () {
    updateThemeButton(document.documentElement.classList.contains('dark'));
});
```

- [ ] **Step 4: Write static/js/charts.js**

```javascript
function initWeightChart(labels, data) {
    const isDark = document.documentElement.classList.contains('dark');
    const accent = isDark ? '#3b82f6' : '#6366f1';
    const gridColor = isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.06)';
    const tickColor = '#64748b';

    new Chart(document.getElementById('weightChart').getContext('2d'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Weight (kg)',
                data: data,
                borderColor: accent,
                backgroundColor: accent + '1a',
                tension: 0.3,
                fill: true,
                pointBackgroundColor: accent,
                pointRadius: 4,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: gridColor }, ticks: { color: tickColor } },
                x: { grid: { display: false }, ticks: { color: tickColor } }
            }
        }
    });
}
```

- [ ] **Step 5: Write static/js/macro_tracker.js**

```javascript
function updateMacroBar(elementId, value, target) {
    const bar = document.getElementById(elementId);
    if (!bar) return;
    const pct = Math.min(100, Math.round((value / target) * 100));
    bar.style.width = pct + '%';
    bar.setAttribute('aria-valuenow', pct);
}
```

---

### Task 8: Base Template

**Files:** `templates/base.html`

- [ ] **Step 1: Create template directories**

```bash
mkdir -p templates/dashboard templates/schedule templates/workouts templates/nutrition templates/supplements templates/hair templates/skin templates/shopping templates/myths
```

- [ ] **Step 2: Write templates/base.html**

```html
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}Lifestyle Dashboard{% endblock %}</title>
  <script>
    (function () {
      if (localStorage.getItem('theme') === 'light')
        document.documentElement.classList.remove('dark');
    })();
  </script>
  <script>tailwind.config = { darkMode: 'class' }</script>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/custom.css') }}">
</head>
<body class="bg-slate-50 dark:bg-[#0f172a] text-slate-900 dark:text-slate-100 min-h-screen">

  <nav class="group fixed inset-y-0 left-0 z-50">
    <div class="w-14 group-hover:w-52 transition-[width] duration-200 ease-in-out h-full
                bg-indigo-50 dark:bg-[#0a0f1e] flex flex-col overflow-hidden
                border-r border-indigo-100 dark:border-slate-800 shadow-lg">

      <div class="flex items-center h-14 px-3.5 shrink-0 border-b border-indigo-100 dark:border-slate-800">
        <span class="text-indigo-600 dark:text-blue-400 font-black text-xl leading-none shrink-0">L</span>
        <span class="ml-1 font-black text-indigo-950 dark:text-slate-100 text-sm tracking-widest
                     opacity-0 group-hover:opacity-100 transition-opacity duration-150 whitespace-nowrap">IFESTYLE</span>
      </div>

      <div class="flex flex-col gap-0.5 p-2 flex-1 overflow-y-auto">
        {% set pages = [
          ('dashboard.overview', '📊', 'Overview'),
          ('schedule.index', '📅', 'Schedule'),
          ('workouts.plan', '💪', 'Workouts'),
          ('nutrition.meals', '🥗', 'Nutrition'),
          ('supplements.schedule_page', '💊', 'Supplements'),
          ('hair.routine', '💇', 'Hair'),
          ('skin.routine', '✨', 'Skin'),
          ('shopping.list_page', '🛒', 'Shopping'),
          ('myths.index', '❓', 'Myths'),
        ] %}
        {% for endpoint, icon, label in pages %}
        <a href="{{ url_for(endpoint) }}"
           class="flex items-center gap-3 px-2.5 py-2.5 rounded-lg transition-colors
                  {% if request.endpoint == endpoint %}
                    bg-indigo-500 dark:bg-blue-600 text-white
                  {% else %}
                    text-slate-500 dark:text-slate-500 hover:bg-indigo-100 dark:hover:bg-slate-800
                    hover:text-indigo-700 dark:hover:text-slate-200
                  {% endif %}">
          <span class="text-xl shrink-0 w-6 text-center leading-none">{{ icon }}</span>
          <span class="text-sm font-medium whitespace-nowrap
                       opacity-0 group-hover:opacity-100 transition-opacity duration-150">{{ label }}</span>
        </a>
        {% endfor %}
      </div>

      <div class="p-2 shrink-0 border-t border-indigo-100 dark:border-slate-800">
        <button onclick="toggleTheme()"
                class="flex items-center gap-3 px-2.5 py-2.5 rounded-lg w-full transition-colors
                       text-slate-500 dark:text-slate-500 hover:bg-indigo-100 dark:hover:bg-slate-800
                       hover:text-indigo-700 dark:hover:text-slate-200">
          <span id="theme-icon" class="text-xl shrink-0 w-6 text-center leading-none">☀️</span>
          <span class="text-sm font-medium whitespace-nowrap
                       opacity-0 group-hover:opacity-100 transition-opacity duration-150"
                id="theme-label">Light Mode</span>
        </button>
      </div>
    </div>
  </nav>

  <main class="ml-14 min-h-screen">
    <div class="max-w-5xl mx-auto px-6 py-8">
      {% block content %}{% endblock %}
    </div>
  </main>

  <script src="{{ url_for('static', filename='js/theme.js') }}"></script>
  {% block scripts %}{% endblock %}
</body>
</html>
```

---

### Task 9: Blueprint Stubs

**Files:** all 9 route files, all 9 placeholder templates, `tests/test_routes.py`

- [ ] **Step 1: Write routes/dashboard.py (stub)**

```python
from flask import Blueprint, redirect, render_template, url_for

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def overview():
    return render_template('dashboard/overview.html',
                           weight=59.0, bmi=20.4, days_since_start=0, metrics=[])


@dashboard_bp.route('/body/log', methods=['POST'])
def log_body():
    return redirect(url_for('dashboard.overview'))
```

- [ ] **Step 2: Write the 8 remaining route stubs**

`routes/schedule.py`:
```python
from flask import Blueprint, render_template

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')


@schedule_bp.route('/')
def index():
    return render_template('schedule/index.html')
```

`routes/workouts.py`:
```python
from flask import Blueprint, render_template

workouts_bp = Blueprint('workouts', __name__, url_prefix='/workouts')


@workouts_bp.route('/')
def plan():
    return render_template('workouts/plan.html')
```

`routes/nutrition.py`:
```python
from flask import Blueprint, render_template

nutrition_bp = Blueprint('nutrition', __name__, url_prefix='/nutrition')


@nutrition_bp.route('/')
def meals():
    return render_template('nutrition/meals.html')
```

`routes/supplements.py`:
```python
from flask import Blueprint, render_template

supplements_bp = Blueprint('supplements', __name__, url_prefix='/supplements')


@supplements_bp.route('/')
def schedule_page():
    return render_template('supplements/schedule.html')
```

`routes/hair.py`:
```python
from flask import Blueprint, render_template

hair_bp = Blueprint('hair', __name__, url_prefix='/hair')


@hair_bp.route('/')
def routine():
    return render_template('hair/routine.html')
```

`routes/skin.py`:
```python
from flask import Blueprint, render_template

skin_bp = Blueprint('skin', __name__, url_prefix='/skin')


@skin_bp.route('/')
def routine():
    return render_template('skin/routine.html')
```

`routes/shopping.py`:
```python
from flask import Blueprint, render_template

shopping_bp = Blueprint('shopping', __name__, url_prefix='/shopping')


@shopping_bp.route('/')
def list_page():
    return render_template('shopping/list.html')
```

`routes/myths.py`:
```python
from flask import Blueprint, render_template

myths_bp = Blueprint('myths', __name__, url_prefix='/myths')


@myths_bp.route('/')
def index():
    return render_template('myths/index.html')
```

- [ ] **Step 3: Write all 9 placeholder templates**

`templates/dashboard/overview.html`:
```html
{% extends 'base.html' %}
{% block title %}Overview — Lifestyle Dashboard{% endblock %}
{% block content %}
<div class="text-center py-24">
  <div class="text-6xl mb-4">📊</div>
  <h1 class="text-2xl font-bold mb-2">Overview</h1>
  <p class="text-slate-500 dark:text-slate-400">Coming soon</p>
</div>
{% endblock %}
```

`templates/schedule/index.html`:
```html
{% extends 'base.html' %}
{% block title %}Schedule — Lifestyle Dashboard{% endblock %}
{% block content %}
<div class="text-center py-24">
  <div class="text-6xl mb-4">📅</div>
  <h1 class="text-2xl font-bold mb-2">Weekly Schedule</h1>
  <p class="text-slate-500 dark:text-slate-400">Coming soon</p>
</div>
{% endblock %}
```

`templates/workouts/plan.html`:
```html
{% extends 'base.html' %}
{% block title %}Workouts — Lifestyle Dashboard{% endblock %}
{% block content %}
<div class="text-center py-24">
  <div class="text-6xl mb-4">💪</div>
  <h1 class="text-2xl font-bold mb-2">Workouts</h1>
  <p class="text-slate-500 dark:text-slate-400">Coming soon</p>
</div>
{% endblock %}
```

`templates/nutrition/meals.html`:
```html
{% extends 'base.html' %}
{% block title %}Nutrition — Lifestyle Dashboard{% endblock %}
{% block content %}
<div class="text-center py-24">
  <div class="text-6xl mb-4">🥗</div>
  <h1 class="text-2xl font-bold mb-2">Nutrition</h1>
  <p class="text-slate-500 dark:text-slate-400">Coming soon</p>
</div>
{% endblock %}
```

`templates/supplements/schedule.html`:
```html
{% extends 'base.html' %}
{% block title %}Supplements — Lifestyle Dashboard{% endblock %}
{% block content %}
<div class="text-center py-24">
  <div class="text-6xl mb-4">💊</div>
  <h1 class="text-2xl font-bold mb-2">Supplements</h1>
  <p class="text-slate-500 dark:text-slate-400">Coming soon</p>
</div>
{% endblock %}
```

`templates/hair/routine.html`:
```html
{% extends 'base.html' %}
{% block title %}Hair — Lifestyle Dashboard{% endblock %}
{% block content %}
<div class="text-center py-24">
  <div class="text-6xl mb-4">💇</div>
  <h1 class="text-2xl font-bold mb-2">Hair Routine</h1>
  <p class="text-slate-500 dark:text-slate-400">Coming soon</p>
</div>
{% endblock %}
```

`templates/skin/routine.html`:
```html
{% extends 'base.html' %}
{% block title %}Skin — Lifestyle Dashboard{% endblock %}
{% block content %}
<div class="text-center py-24">
  <div class="text-6xl mb-4">✨</div>
  <h1 class="text-2xl font-bold mb-2">Skincare</h1>
  <p class="text-slate-500 dark:text-slate-400">Coming soon</p>
</div>
{% endblock %}
```

`templates/shopping/list.html`:
```html
{% extends 'base.html' %}
{% block title %}Shopping — Lifestyle Dashboard{% endblock %}
{% block content %}
<div class="text-center py-24">
  <div class="text-6xl mb-4">🛒</div>
  <h1 class="text-2xl font-bold mb-2">Shopping List</h1>
  <p class="text-slate-500 dark:text-slate-400">Coming soon</p>
</div>
{% endblock %}
```

`templates/myths/index.html`:
```html
{% extends 'base.html' %}
{% block title %}Myth Check — Lifestyle Dashboard{% endblock %}
{% block content %}
<div class="text-center py-24">
  <div class="text-6xl mb-4">❓</div>
  <h1 class="text-2xl font-bold mb-2">Myth Check</h1>
  <p class="text-slate-500 dark:text-slate-400">Coming soon</p>
</div>
{% endblock %}
```

- [ ] **Step 4: Write tests/test_routes.py**

```python
def test_overview(client):
    assert client.get('/').status_code == 200


def test_schedule(client):
    assert client.get('/schedule/').status_code == 200


def test_workouts(client):
    assert client.get('/workouts/').status_code == 200


def test_nutrition(client):
    assert client.get('/nutrition/').status_code == 200


def test_supplements(client):
    assert client.get('/supplements/').status_code == 200


def test_hair(client):
    assert client.get('/hair/').status_code == 200


def test_skin(client):
    assert client.get('/skin/').status_code == 200


def test_shopping(client):
    assert client.get('/shopping/').status_code == 200


def test_myths(client):
    assert client.get('/myths/').status_code == 200
```

- [ ] **Step 5: Run all tests**

```bash
pytest tests/ -v
```

Expected: `test_models` (4), `test_app` (2), `test_routes` (9) all pass. Total: 15 tests.

---

### Task 10: Full Overview Dashboard

**Files:** `routes/dashboard.py` (overwrite), `templates/dashboard/overview.html` (overwrite), `tests/test_dashboard.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_dashboard.py
from models import db
from models.body import BodyMetric


def test_overview_default_weight(client):
    r = client.get('/')
    assert r.status_code == 200
    assert b'59' in r.data


def test_overview_default_bmi(client):
    r = client.get('/')
    assert b'20.4' in r.data


def test_overview_priority_cards(client):
    r = client.get('/')
    assert b'Nutrition' in r.data
    assert b'Resistance Training' in r.data
    assert b'Hair Fall' in r.data
    assert b'Skin Barrier' in r.data
    assert b'Running Stamina' in r.data


def test_overview_height_banner(client):
    r = client.get('/')
    assert b'Height at 24' in r.data
    assert b'Growth plates' in r.data


def test_log_body_saves_entry(client, app):
    client.post('/body/log', data={'weight_kg': '60.5'})
    with app.app_context():
        m = BodyMetric.query.first()
        assert m is not None
        assert m.weight_kg == 60.5


def test_log_body_updates_same_day(client, app):
    client.post('/body/log', data={'weight_kg': '60.0'})
    client.post('/body/log', data={'weight_kg': '61.5'})
    with app.app_context():
        assert BodyMetric.query.count() == 1
        assert BodyMetric.query.first().weight_kg == 61.5


def test_overview_shows_logged_weight(client):
    client.post('/body/log', data={'weight_kg': '62.0'})
    r = client.get('/')
    assert b'62.0' in r.data
```

- [ ] **Step 2: Run tests — confirm they fail**

```bash
pytest tests/test_dashboard.py -v
```

Expected: `test_overview_priority_cards`, `test_overview_height_banner`, and log tests fail (stub returns hardcoded values and placeholder template).

- [ ] **Step 3: Overwrite routes/dashboard.py**

```python
from datetime import date

from flask import Blueprint, current_app, redirect, render_template, request, url_for

from models import db
from models.body import BodyMetric

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def overview():
    latest = BodyMetric.query.order_by(BodyMetric.date.desc()).first()
    weight = latest.weight_kg if latest else 59.0
    bmi = round(weight / (1.70 ** 2), 1)
    start = date.fromisoformat(current_app.config['PROGRAM_START_DATE'])
    days_since_start = (date.today() - start).days
    metrics = BodyMetric.query.order_by(BodyMetric.date.asc()).all()
    return render_template(
        'dashboard/overview.html',
        weight=weight,
        bmi=bmi,
        days_since_start=days_since_start,
        metrics=metrics,
    )


@dashboard_bp.route('/body/log', methods=['POST'])
def log_body():
    try:
        weight_kg = float(request.form['weight_kg'])
    except (KeyError, ValueError):
        return redirect(url_for('dashboard.overview'))
    today = date.today().isoformat()
    existing = BodyMetric.query.filter_by(date=today).first()
    if existing:
        existing.weight_kg = weight_kg
    else:
        db.session.add(BodyMetric(date=today, weight_kg=weight_kg))
    db.session.commit()
    return redirect(url_for('dashboard.overview'))
```

- [ ] **Step 4: Overwrite templates/dashboard/overview.html**

```html
{% extends 'base.html' %}
{% block title %}Overview — Lifestyle Dashboard{% endblock %}

{% block content %}

<h1 class="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-6">Overview</h1>

<div class="grid grid-cols-3 gap-4 mb-4">
  <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-100 dark:border-slate-700 shadow-sm">
    <div class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">Weight</div>
    <div class="text-3xl font-bold text-blue-500 dark:text-blue-400">
      {{ weight }}<span class="text-base text-slate-400 ml-1">kg</span>
    </div>
    <div class="text-xs text-slate-400 mt-1">Target: 65 kg</div>
  </div>
  <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-100 dark:border-slate-700 shadow-sm">
    <div class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">BMI</div>
    <div class="text-3xl font-bold text-indigo-500 dark:text-blue-400">{{ bmi }}</div>
    <div class="text-xs text-slate-400 mt-1">Target: 22–23</div>
  </div>
  <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-100 dark:border-slate-700 shadow-sm">
    <div class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">Day</div>
    <div class="text-3xl font-bold text-emerald-500">{{ days_since_start }}</div>
    <div class="text-xs text-slate-400 mt-1">Since June 2, 2026</div>
  </div>
</div>

<form method="POST" action="{{ url_for('dashboard.log_body') }}"
      class="flex items-center gap-3 bg-white dark:bg-slate-800 rounded-xl px-5 py-4 mb-8
             border border-slate-100 dark:border-slate-700 shadow-sm">
  <label class="text-sm text-slate-600 dark:text-slate-400 whitespace-nowrap">Log today's weight:</label>
  <input type="number" name="weight_kg" step="0.1" min="30" max="200" placeholder="{{ weight }}"
         class="w-24 px-3 py-1.5 text-sm rounded-lg border border-slate-200 dark:border-slate-600
                bg-slate-50 dark:bg-slate-700 text-slate-900 dark:text-slate-100
                focus:outline-none focus:ring-2 focus:ring-indigo-500">
  <span class="text-sm text-slate-500">kg</span>
  <button type="submit"
          class="px-4 py-1.5 bg-indigo-500 dark:bg-blue-600 hover:bg-indigo-600 dark:hover:bg-blue-700
                 text-white text-sm font-medium rounded-lg transition-colors">
    Save
  </button>
</form>

<h2 class="text-lg font-bold text-slate-900 dark:text-slate-100 mb-4">Priorities</h2>
<div class="flex flex-col gap-3 mb-8">

  <a href="{{ url_for('nutrition.meals') }}"
     class="flex gap-4 bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-100 dark:border-slate-700
            shadow-sm hover:border-indigo-300 dark:hover:border-blue-700 transition-colors">
    <span class="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-100 dark:bg-blue-900 text-indigo-600 dark:text-blue-300
                 font-bold text-sm flex items-center justify-center">1</span>
    <div>
      <div class="font-semibold text-slate-900 dark:text-slate-100">Nutrition &amp; Caloric Surplus</div>
      <div class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">Foundation. At 59 kg, target 2,400–2,600 kcal/day with 130–145 g protein. Without this, training produces almost nothing.</div>
    </div>
  </a>

  <a href="{{ url_for('workouts.plan') }}"
     class="flex gap-4 bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-100 dark:border-slate-700
            shadow-sm hover:border-indigo-300 dark:hover:border-blue-700 transition-colors">
    <span class="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-100 dark:bg-emerald-900 text-emerald-600 dark:text-emerald-300
                 font-bold text-sm flex items-center justify-center">2</span>
    <div>
      <div class="font-semibold text-slate-900 dark:text-slate-100">Resistance Training — Progressive Overload</div>
      <div class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">3 days/week full-body for 8 weeks, then upper/lower split. 3–5 sets of 8–15 reps, taken close to failure.</div>
    </div>
  </a>

  <a href="{{ url_for('hair.routine') }}"
     class="flex gap-4 bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-100 dark:border-slate-700
            shadow-sm hover:border-indigo-300 dark:hover:border-blue-700 transition-colors">
    <span class="flex-shrink-0 w-8 h-8 rounded-full bg-amber-100 dark:bg-amber-900 text-amber-600 dark:text-amber-300
                 font-bold text-sm flex items-center justify-center">3</span>
    <div>
      <div class="font-semibold text-slate-900 dark:text-slate-100">Hair Fall — Act Early</div>
      <div class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">Photos show early androgenic alopecia pattern (Norwood II–III). Earlier intervention = more hair preserved. Dermatologist recommended for minoxidil/finasteride.</div>
    </div>
  </a>

  <a href="{{ url_for('skin.routine') }}"
     class="flex gap-4 bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-100 dark:border-slate-700
            shadow-sm hover:border-indigo-300 dark:hover:border-blue-700 transition-colors">
    <span class="flex-shrink-0 w-8 h-8 rounded-full bg-rose-100 dark:bg-rose-900 text-rose-600 dark:text-rose-300
                 font-bold text-sm flex items-center justify-center">4</span>
    <div>
      <div class="font-semibold text-slate-900 dark:text-slate-100">Skin Barrier Repair</div>
      <div class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">Correct products already owned (urea, glycerin, shea). Missing: dedicated face moisturizer. Apply moisturizer within 3 minutes of shower.</div>
    </div>
  </a>

  <a href="{{ url_for('schedule.index') }}"
     class="flex gap-4 bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-100 dark:border-slate-700
            shadow-sm hover:border-indigo-300 dark:hover:border-blue-700 transition-colors">
    <span class="flex-shrink-0 w-8 h-8 rounded-full bg-sky-100 dark:bg-sky-900 text-sky-600 dark:text-sky-300
                 font-bold text-sm flex items-center justify-center">5</span>
    <div>
      <div class="font-semibold text-slate-900 dark:text-slate-100">Running Stamina — Build Slowly</div>
      <div class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">2 days/week. Couch-to-5K protocol. Main risks at beginner level: shin splints, knee strain from ramping too fast.</div>
    </div>
  </a>

</div>

<div class="bg-sky-50 dark:bg-slate-800 border border-sky-200 dark:border-slate-600 rounded-xl p-6 mb-8">
  <div class="flex items-start gap-3">
    <span class="text-2xl leading-none mt-0.5">📏</span>
    <div>
      <h3 class="font-bold text-sky-800 dark:text-sky-300 mb-2">Height at 24 — Honest Answer</h3>
      <p class="text-sm text-sky-700 dark:text-slate-300 mb-3">
        Growth plates close at 16–18 in males. Height increase is not physiologically possible at 24. No supplement or exercise changes this.
      </p>
      <p class="text-sm font-semibold text-sky-800 dark:text-sky-300 mb-2">What IS possible:</p>
      <ul class="text-sm text-sky-700 dark:text-slate-300 space-y-1">
        <li>• <strong>Posture correction:</strong> anterior pelvic tilt, forward head, kyphosis can cost 2–3 cm of apparent height. Fixing this takes 8–12 weeks.</li>
        <li>• <strong>Spinal hydration:</strong> discs compress through the day. Core strength + hydration maintains disc health.</li>
        <li>• <strong>Exercises:</strong> dead hangs (60 sec × 3/day), cat-cow, hip flexor stretches, face pulls.</li>
      </ul>
    </div>
  </div>
</div>

{% if metrics %}
<h2 class="text-lg font-bold text-slate-900 dark:text-slate-100 mb-4">Weight Progress</h2>
<div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-100 dark:border-slate-700 shadow-sm mb-8">
  <canvas id="weightChart" height="80"></canvas>
</div>
{% endif %}

{% endblock %}

{% block scripts %}
{% if metrics %}
<script src="{{ url_for('static', filename='js/charts.js') }}"></script>
<script>
  initWeightChart(
    {{ metrics | map(attribute='date') | list | tojson }},
    {{ metrics | map(attribute='weight_kg') | list | tojson }}
  );
</script>
{% endif %}
{% endblock %}
```

- [ ] **Step 5: Run all tests — confirm they all pass**

```bash
pytest tests/ -v
```

Expected: all 22 tests pass (4 model + 2 app + 9 routes + 7 dashboard).

---

### Task 11: Local Run & Verification

- [ ] **Step 1: Copy .env.example to .env**

```bash
copy .env.example .env
```

- [ ] **Step 2: Start the dev server**

```bash
flask --app app:create_app run --debug
```

Expected: server starts at http://127.0.0.1:5000 with no errors.

- [ ] **Step 3: Verify all 9 nav links work**

Open http://127.0.0.1:5000 and click every sidebar icon:
- `/` — stats bar (59 kg, BMI 20.4, Day 0), 5 priority cards, height banner
- `/schedule/`, `/workouts/`, `/nutrition/`, `/supplements/`, `/hair/`, `/skin/`, `/shopping/`, `/myths/` — each shows its placeholder

- [ ] **Step 4: Test sidebar and theme toggle**

- Hover over the sidebar: labels animate in, sidebar expands to ~200px
- Click the ☀️ toggle: switches to light mode (indigo-tinted sidebar, white cards)
- Refresh: light mode persists (localStorage)
- Click 🌙: back to dark mode

- [ ] **Step 5: Test weight logging**

- Enter `60.5` in the weight form, click Save
- Page reloads: Weight shows `60.5`, BMI recalculates to `20.9`
- Submit again with `61.0`: still 1 entry in DB, weight updates to `61.0`

- [ ] **Step 6: Fetch Wger exercise images**

```bash
python scripts/fetch_wger_images.py
```

Expected: `data/exercises.json` updated with `image_url` values for most exercises. Check the file — most dumbbell exercises should have URLs.

- [ ] **Step 7: Final test run**

```bash
pytest tests/ -v
```

Expected: all 22 tests pass.
