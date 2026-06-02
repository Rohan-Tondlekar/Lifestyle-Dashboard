# Personal Lifestyle Dashboard

A science-backed personal health and fitness web application built in Python (Flask), covering fitness, nutrition, hair health, and skincare — tailored for a 24-year-old male in Hamburg, Germany targeting lean muscle gain.

---

## Project Description

This dashboard consolidates a complete lifestyle coaching plan into a single web application. It tracks workouts, macros, supplement timing, hair care routines, and skincare protocols. All recommendations are evidence-based, with mechanisms explained. The app is designed to be run locally and stores progress data in a SQLite database.

**User profile this was built for:**
- Age: 24 | Height: 170 cm | Weight: 59 kg → Target: ~65 kg (lean muscle)
- Current BMI: 20.4 → Target BMI: 22–23
- Fitness baseline: complete beginner (0 workouts/week)
- Running baseline: none
- Goals: muscle hypertrophy, running stamina, reduce hair fall, manage dry skin
- Equipment: adjustable dumbbells up to 21 kg, yoga mat
- Location: Hamburg, Germany (affects supplement needs — low UV October–April, German store availability)

---

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Backend | Python 3.11+ / Flask | Lightweight, easy to extend, good for local apps |
| Database | SQLite via SQLAlchemy | Zero setup, file-based, perfect for personal use |
| Frontend | Jinja2 templates + vanilla JS | No build step, fast iteration |
| Styling | Tailwind CSS (CDN) | Utility-first, responsive out of the box |
| Charts | Chart.js (CDN) | Lightweight, good-looking progress charts |
| Exercise images | Wger REST API or Exercisedb | Free, no API key required for Wger |

---

## Project Structure

```
lifestyle-dashboard/
│
├── app.py                    # Flask app factory, route registration
├── config.py                 # Config: DB path, secret key, constants
├── requirements.txt
├── README.md
│
├── models/
│   ├── __init__.py
│   ├── workout.py            # WorkoutLog, ExerciseSet models
│   ├── nutrition.py          # MealLog, FoodItem models
│   ├── body.py               # BodyMetric (weight, measurements)
│   └── routine.py            # HairLog, SkinLog
│
├── routes/
│   ├── __init__.py
│   ├── dashboard.py          # Overview, summary stats
│   ├── workouts.py           # Workout plans, logging
│   ├── nutrition.py          # Meal plans, macro tracker
│   ├── supplements.py        # Supplement schedule
│   ├── hair.py               # Hair routine tracker
│   └── skin.py               # Skin routine tracker
│
├── static/
│   ├── css/
│   │   └── custom.css
│   ├── js/
│   │   ├── macro_tracker.js
│   │   ├── workout_logger.js
│   │   └── charts.js
│   └── images/
│       └── exercises/        # Downloaded or fetched exercise images
│
├── templates/
│   ├── base.html             # Navbar, sidebar, layout wrapper
│   ├── dashboard/
│   │   └── overview.html
│   ├── workouts/
│   │   ├── plan.html
│   │   └── log.html
│   ├── nutrition/
│   │   ├── meals.html
│   │   └── tracker.html
│   ├── supplements/
│   │   └── schedule.html
│   ├── hair/
│   │   └── routine.html
│   └── skin/
│       └── routine.html
│
└── data/
    ├── exercises.json        # Exercise library with sets/reps/progressions
    ├── foods.json            # Food database with macros
    └── products.json         # Hair + skin products with ingredient analysis
```

---

## Setup Instructions

### 1. Clone / create the project

```bash
mkdir lifestyle-dashboard
cd lifestyle-dashboard
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install flask flask-sqlalchemy requests
pip freeze > requirements.txt
```

### 2. Initialize the database

```bash
flask shell
>>> from app import db
>>> db.create_all()
>>> exit()
```

### 3. Run locally

```bash
flask run --debug
# Open http://127.0.0.1:5000
```

### 4. (Optional) Fetch exercise images from Wger API

```bash
python scripts/fetch_exercises.py
# Saves images to static/images/exercises/
```

---

## Build Guidelines

### General principles

- Every page should work without JavaScript for core content — JS only enhances (charts, live macro updates, toggles).
- Use Flask blueprints for each section (workouts, nutrition, etc.) — keeps routes organized as the app grows.
- Store all static coaching content (exercise descriptions, meal plans, product analysis) in JSON files under `data/` — this makes it easy to edit without touching Python.
- The SQLite database is for user-generated data only: workout logs, macro logs, body weight entries, routine completion.
- All dates stored as UTC ISO strings. Display in local time using JS `Intl.DateTimeFormat`.

### Database schema guidelines

```python
# models/workout.py
class WorkoutLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String, nullable=False)      # ISO date string
    day_type = db.Column(db.String)                  # "upper", "lower", "run", "rest"
    completed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    sets = db.relationship('ExerciseSet', backref='workout', lazy=True)

class ExerciseSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout_log.id'))
    exercise_name = db.Column(db.String, nullable=False)
    weight_kg = db.Column(db.Float)
    reps = db.Column(db.Integer)
    set_number = db.Column(db.Integer)

# models/nutrition.py
class MealLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String, nullable=False)
    meal_name = db.Column(db.String)                 # "breakfast", "lunch", etc.
    protein_g = db.Column(db.Float, default=0)
    carbs_g = db.Column(db.Float, default=0)
    fat_g = db.Column(db.Float, default=0)
    kcal = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)

# models/body.py
class BodyMetric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String, nullable=False)
    weight_kg = db.Column(db.Float)
    notes = db.Column(db.Text)
```

### API routes to implement

| Method | Route | Purpose |
|---|---|---|
| GET | `/` | Overview dashboard |
| GET | `/workouts` | View weekly workout plan |
| POST | `/workouts/log` | Log a completed workout |
| GET | `/workouts/history` | View past workout logs + Chart.js progress chart |
| GET | `/nutrition` | View meal plans (training / rest / run day) |
| POST | `/nutrition/log` | Log a meal/macro entry |
| GET | `/nutrition/tracker` | Live macro tracker for today |
| GET | `/supplements` | Supplement schedule with timing table |
| GET | `/hair` | Hair routine + product analysis |
| GET | `/skin` | Skin routine + product verdicts |
| POST | `/body/log` | Log weight entry |
| GET | `/body/progress` | Body weight chart over time |

---

## Dashboard Contents

### Overview page

**Stats bar (top of page):**
- Current weight (from latest BodyMetric entry)
- Current BMI (calculated: weight / 1.70²)
- Target: 65 kg / BMI 22–23
- Days since program start

**Priority order (render as numbered cards):**

1. **Nutrition & caloric surplus** — Foundation. At 59 kg, target 2,400–2,600 kcal/day with 130–145 g protein. Without this, training produces almost nothing.
2. **Resistance training — progressive overload** — 3 days/week full-body for 8 weeks, then upper/lower split. 3–5 sets of 8–15 reps, taken close to failure.
3. **Hair fall — act early** — Photos show early androgenic alopecia pattern (Norwood II–III). Frontal recession at temples + crown thinning. Earlier intervention = more hair preserved. Ketoconazole shampoo + zinc + scalp massage are supportive. Dermatologist recommended for minoxidil/finasteride discussion.
4. **Skin barrier repair** — Correct products already owned (urea, glycerin, shea). Missing: dedicated face moisturizer. Apply moisturizer within 3 minutes of shower.
5. **Running stamina — build slowly** — 2 days/week. Couch-to-5K protocol. Main risks at beginner level: shin splints, knee strain from ramping too fast.

**Height increase — honest answer (display as info banner):**
Growth plates close at 16–18 in males. Height increase is not physiologically possible at 24. No supplement or exercise changes this. What IS possible:
- Posture correction: anterior pelvic tilt, forward head, kyphosis can cost 2–3 cm of apparent height. Fixing this is real and takes 8–12 weeks.
- Spinal hydration: discs compress through the day. Core strength + hydration maintains disc health.
- Exercises: dead hangs (60 sec × 3/day), cat-cow, hip flexor stretches, face pulls.

---

### Weekly Schedule page

**7-day layout (render as card grid):**

| Day | Type | Focus |
|---|---|---|
| Monday | Upper body lift | Chest + Back |
| Tuesday | Run + active rest | Week 1–8 running program |
| Wednesday | Lower body + core | Legs + Abs |
| Thursday | Full rest | Walk if desired |
| Friday | Upper body lift | Shoulders + Arms |
| Saturday | Run + stretch | Week 1–8 running program |
| Sunday | Rest / meal prep | Prep for the week |

**Daily schedule template (training day):**

| Time | Activity |
|---|---|
| 07:00 | Wake. 400 ml water. Vitamin D3 with breakfast (fat-soluble). |
| 07:15 | AM skincare: lukewarm face wash → face moisturizer on damp skin → SPF 50. |
| 07:30 | Breakfast: 3 eggs + 80g oats + 1 banana + 200ml milk. ~600 kcal, ~30g protein. |
| 09:00 | Workout (45–60 min). 500 ml water during session. |
| 10:00 | Post-workout: Quark 200g + fruit, or chicken + rice. Within 60 min of training. |
| 13:00 | Lunch: 150g protein + 150g rice/pasta + salad + olive oil. ~650 kcal. |
| 18:00 | Dinner: 200g protein + vegetables + complex carb. Take Magnesium 500 mg with dinner. |
| 20:00 | Hair routine on wash days (scalp massage → shampoo → condition). |
| 21:30 | PM skincare + Lacura Med 10% Urea on body within 3 min of shower. Fussbalsam on feet with socks. |
| 22:00 | Optional: 200g Quark before bed (casein for overnight muscle repair). |

**Running program (8-week beginner protocol):**

| Week | Session structure | Total run time | RPE |
|---|---|---|---|
| 1–2 | 1 min jog / 2 min walk × 8 rounds | ~8 min running | 4–5/10 |
| 3–4 | 2 min jog / 1 min walk × 8 rounds | ~16 min running | 5/10 |
| 5–6 | 5 min jog / 1 min walk × 4 rounds | ~20 min running | 5–6/10 |
| 7 | 10 min jog / 1 min walk × 2 | ~20 min | 6/10 |
| 8 | 20 min continuous jog (slow pace) | 20 min | 6/10 |

Run 2×/week (Tue + Sat). Always warm up 5 min brisk walk before, cool down 5 min after. If joints hurt, repeat previous week — do not push through joint pain.

---

### Workouts page

#### Phase 1: Full-body (weeks 1–8) — 3×/week

All exercises: 3 sets × 10–12 reps. Rest 60–90 sec between sets. Progressive overload = add 1 rep per session until you hit 12, then increase weight or difficulty.

| Exercise | Muscle group | Form cues | Progression |
|---|---|---|---|
| Push-ups | Chest, triceps, anterior deltoid | Hands shoulder-width, elbows 45° from body, lower chest to ~2 cm from floor, full lockout at top | Standard → feet elevated → archer push-ups → add DB row superset |
| DB Goblet squat | Quads, glutes, core | Hold 1 DB at chest, feet shoulder-width, knees track over toes, sit back not just down, chest up | 10 kg → 14 kg → 21 kg → pause at bottom 3 sec |
| DB Romanian deadlift | Hamstrings, glutes, lower back | Hinge at hips, soft knee bend, DBs travel close to legs, feel hamstring stretch at bottom, drive hips forward at top | 12 kg → 16 kg → 21 kg → single-leg variant |
| DB Bent-over row | Lats, rhomboids, biceps | Hinge 45°, DBs hang, pull elbows to hips, squeeze shoulder blades at top, controlled negative | 8 kg → 14 kg → 21 kg → chest-supported variant |
| DB Shoulder press | Deltoids, upper traps, triceps | Seated or standing, DBs at ear height, press straight up, slight forward lean, no flare | 8 kg → 12 kg → 18 kg → Arnold press |
| DB Bicep curl | Biceps, brachialis | Elbows pinned to sides, full ROM, 3 sec negative, no body swing | 8 kg → 12 kg → 16 kg → hammer curl superset |
| Plank | Core — transverse abdominis, obliques | Forearms down, body flat, glutes squeezed, hips don't sag or pike, breathe normally | 20 sec → 45 sec → 60 sec → RKC plank |
| Dead bug | Deep core, anti-extension | Lower back pressed into mat, extend opposite arm and leg, breathe out on extension, never lose lower back contact | Bodyweight → add 2 kg DB in extended hand |
| DB Lateral raise | Medial deltoid | Slight forward lean, raise to shoulder height, thumbs slightly down, 3 sec descent, no momentum | 4 kg → 8 kg → 12 kg → 4 sec up / 4 sec down tempo |
| Hip thrust (mat) | Glutes, hamstrings | Upper back on mat edge, feet flat, drive hips up squeezing glutes at top, hold 1 sec, lower controlled | Bodyweight → DB on hips → two DBs → pause variant |

**Exercise image guidance for developers:** Fetch images from the [Wger REST API](https://wger.de/api/v2/) — free, no auth required for basic use. Endpoint: `GET https://wger.de/api/v2/exercise/?format=json&language=2&category=X`. Map exercise names to Wger exercise IDs and store in `data/exercises.json`.

#### Phase 2: Upper/Lower split (weeks 9+)

**Upper day (Monday + Friday):**
- DB Bench press (chest): 4×8–10
- DB Row (back): 4×10
- Incline push-ups (chest): 3×12
- DB Shoulder press: 3×10
- DB Lateral raise: 3×12–15
- DB Bicep curl: 3×12
- DB Tricep overhead extension: 3×12
- Face pulls (band/towel): 3×15

**Lower day (Wednesday):**
- DB Goblet squat: 4×10
- DB Romanian deadlift: 4×10
- DB Reverse lunge: 3×10 each leg
- Hip thrust: 3×12
- DB Calf raise: 3×15
- Plank: 3×45–60 sec
- Hanging leg raise: 3×10
- Bicycle crunches: 3×20

---

### Supplements page

**Current supplements (from user photos):**

**Doppelherz Vitamin D3 2000 IU (50 µg)**
- Verdict: Excellent. Hamburg is at 53°N — virtually zero Vitamin D synthesis October–April.
- Mechanism: D3 is the active form (vs D2). Supports calcium absorption, immune function, muscle protein synthesis.
- Dosage: 1 tablet/day with breakfast. Fat-soluble — absorption increases ~50% with dietary fat.
- Interactions: Take in the morning, not with magnesium (competition for absorption channels).

**Abtei Magnesium 500 Plus (with all B-vitamins, Biotin 150 µg, Folate 600 µg, B12 20 µg)**
- Verdict: Very good stack. Magnesium supports ATP synthesis, muscle contraction/relaxation, sleep via GABA modulation.
- Biotin (150 µg) supports hair keratin production — relevant for hair loss concern.
- B12 supports red blood cell formation critical for running stamina.
- Dosage: 1 tablet with dinner. If loose stools occur, split dose (morning + evening).
- Interactions: Do not take within 2 hours of Vitamin D3. Zinc and magnesium compete — space by 4–5 hours.

**Missing supplements — critical gaps:**

| Supplement | Mechanism | Dose | Where to buy |
|---|---|---|---|
| Omega-3 (EPA/DHA) | Anti-inflammatory, supports muscle protein synthesis, scalp sebum quality, skin barrier. Hamburg diet often low in fatty fish. | 2–3 g EPA+DHA/day with a meal | dm: Doppelherz Omega-3. Rossmann: Abtei Omega-3. ~€8–12/month |
| Zinc 15–25 mg | Critical for testosterone production, immune function, and hair follicle health. Zinc deficiency is a leading reversible cause of hair loss. Not in current stack. | 15–25 mg with food (not empty stomach — nausea) | dm: Doppelherz Zink. Rossmann: Abtei Zink. ~€5–7 |
| Whey Protein | At 59 kg targeting muscle gain, 130–145 g protein/day is needed. Difficult from food alone. Leucine threshold ~2.5 g per meal triggers muscle protein synthesis. | 25–30 g post-workout | Lidl: Beavita/Powerstar. dm: ESN Whey. iHerb: ON Gold Standard |
| Creatine Monohydrate (optional) | Most-studied ergogenic aid. Increases phosphocreatine stores. Enables more reps per set. Accelerates lean muscle gain by ~20% compared to training alone. Safe at all studied doses. | 3–5 g/day, any time, with water | Amazon.de: Creapure brand. ~€15–20/500g |

**Daily supplement timing table:**

| Time | Supplement | With food? | Reason |
|---|---|---|---|
| With breakfast | Vitamin D3 2000 IU | With fat-containing food | Fat-soluble — needs dietary fat |
| With lunch | Zinc 15–25 mg | With food | Prevents nausea; spaced from Mg |
| Post-workout | Whey protein 25–30 g | With water or milk | Leucine delivery during anabolic window |
| With dinner | Magnesium 500 mg | With food | Reduces GI side effects; sleep benefit |
| With dinner | Omega-3 2–3 g | With food | Fat-soluble |
| Before bed (optional) | Quark 200 g | As-is | Slow casein for overnight muscle repair |

---

### Meal Planning page

**Daily macro targets (muscle gain at 59 kg):**
- Calories: 2,500 kcal/day (surplus of ~300–400 kcal above TDEE)
- Protein: 140 g/day (2.2–2.4 g/kg bodyweight)
- Carbohydrates: 280 g/day
- Fat: 75 g/day

**Training day meal plan (~2,500 kcal):**

| Meal | Time | Key foods | Kcal | Protein |
|---|---|---|---|---|
| Breakfast | 07:30 | 80g oats + 250ml milk + 3 eggs + 1 banana | ~580 | ~30g |
| Post-workout | 10:00 | Whey scoop + 200g Quark + fruit | ~400 | ~35g |
| Lunch | 13:00 | 150g chicken/salmon + 150g rice + salad + olive oil | ~650 | ~45g |
| Snack | 16:00 | Hüttenkäse 150g + crackers OR nuts 30g + apple | ~300 | ~15g |
| Dinner | 18:30 | 200g beef/turkey + 200g sweet potato + vegetables | ~600 | ~40g |
| Before bed (optional) | 21:30 | 200g Quark + 1 tsp honey | ~220 | ~27g |

**Rest day meal plan (~2,100–2,200 kcal):** Slightly lower calories, same protein target. Remove one carb serving. Keep all protein sources.

**Run day meal plan (~2,400 kcal):** More carbs pre-run, lighter on fat. No heavy fat in pre-run meal — delays gastric emptying, causes GI distress during running.

**Best protein sources — Germany price/quality ranking:**

| Food | Protein/100g | Cost | Where |
|---|---|---|---|
| Magerquark | 12g | €0.79–1.19/500g | Überall |
| Hühnerbrust | 31g | €4–6/kg | Lidl, Kaufland |
| Eier | 13g | €2–3/10 Stk | Überall |
| Rote Linsen | 26g (dry) | €1.50–2/500g | Lidl, Aldi |
| Thunfisch (Dose) | 26g | €0.99–1.50/Dose | Überall |
| Hüttenkäse | 12g | €1–1.50/250g | dm, Lidl |

**Weekly meal prep (Sunday batch cook):**
- 500g Hühnenbrust in oven (25 min, 200°C) → 3–4 portions
- 500g Vollkornreis cooked → keeps 4–5 days
- 8 hard-boiled eggs → grab-and-go protein
- Big pot of Linsensuppe → 4 portions for ~€2
- Wash and chop vegetables

---

### Hair page

**Hair assessment (based on user photos):**
Visible frontal recession along the hairline, temple thinning, and crown area thinning — consistent with early androgenic alopecia (AGA), likely Norwood Scale II–III. This is hormone-driven (DHT), not purely nutritional. Early intervention is critical.

**Shampoo analysis — Cien Nature Bio-Mandel (current product, from Lidl):**
- Ingredients: Lauryl Glucoside + Sodium Coco-Sulfate (surfactants, milder than SLS), Argania Spinosa Kernel Oil (argan), Prunus Amygdalus Dulcis Oil (almond), Hydrolyzed Wheat/Corn/Soy Protein, Aloe vera.
- Verdict: Good for hair quality — hydrolyzed proteins coat shaft, reduce breakage. No silicones (positive for scalp). Does nothing to address androgenic alopecia specifically.
- Use as: general quality shampoo, rotated with ketoconazole shampoo.

**Ketoconazole shampoo — is the Instagram recommendation valid?**
Yes, partially evidence-backed. Two mechanisms: (1) Antifungal — reduces Malassezia yeast on scalp, which drives seborrheic dermatitis and worsens follicle inflammation. (2) Mild anti-androgenic — weakly blocks DHT at follicle level. Studies show 2% ketoconazole 2–4×/week produced comparable results to 2% minoxidil in some trials. Not a standalone cure for AGA, but a legitimate supportive tool.
- Product: Nizoral 2% Shampoo (pharmacy/Amazon.de, ~€15–18) or Terzolin 2% (dm/Rossmann pharmacy section).
- Use: 2–3×/week, leave on scalp 3–5 minutes before rinsing.

**Baby shampoo — does fewer chemicals = better for hair loss?**
No. Baby shampoos are very mild (designed for infant scalps) but contain no active ingredients targeting hair loss. No DHT blockers, no antifungals, no follicle stimulants. Using baby shampoo instead of ketoconazole shampoo is a step backwards for this pattern.

**Pantene Pro-V Keratin Protect Oil (current product, from photo):**
- Primarily silicone-based (cyclopentasiloxane, dimethicone). Coats shaft for shine and smoothness.
- Does not penetrate the hair shaft like true oils (coconut, argan).
- Silicone buildup on scalp can contribute to follicle clogging with overuse.
- Use: 1–2 drops on ends only. Never apply to scalp.

**Scalp massage brush (silicone, from photo):**
Good tool. Scalp massage increases blood flow to the dermal papilla, improving nutrient delivery to actively growing follicles. A 2016 Japanese study showed 4 min daily scalp massage increased hair thickness over 6 months. Use during shampooing — 2–3 min circular motions. Light pressure.

**Complete hair routine:**

| Step | Action | Frequency | Product |
|---|---|---|---|
| 1 | Pre-wash oil treatment | 1–2×/week | Coconut oil (Lidl/Aldi, ~€3) on mid-lengths. Leave 1–2 hrs. Not scalp. |
| 2 | Dry scalp massage | Every wash | Silicone brush — 2 min before water |
| 3 | Ketoconazole shampoo | 2–3×/week | Nizoral 2% or Terzolin — leave 5 min |
| 4 | Wet scalp massage | During shampoo | Silicone brush — 2 min |
| 5 | Moisturizing shampoo (rotate) | Remaining wash days | Cien Nature Bio-Mandel |
| 6 | Conditioner | Every wash | Mid-lengths to ends only, 2 min, rinse well |
| 7 | Leave-in oil (optional) | Styling days | Pantene Keratin Oil — 1–2 drops on ends |
| 8 | Towel dry | Every wash | Pat, don't rub. Microfiber towel reduces breakage. |

**Medical note (display as warning card):** The pattern observed (temple recession + crown thinning at 24) is characteristic of androgenic alopecia. Ketoconazole + zinc + scalp massage are supportive. The two evidence-based medical treatments are Minoxidil (topical, OTC in Germany — "Regaine Männer" at dm/Rossmann) and Finasteride (oral, prescription only). A dermatologist (Hautarzt) can confirm diagnosis and guide treatment.

---

### Skincare page

**Product verdicts (from user photos):**

**Lacura Med Körperlotion Intensiv 10% Urea (Aldi):**
- Verdict: Excellent for dry body skin.
- Mechanism: Urea at 10% is a keratolytic humectant — breaks down excess keratin buildup AND draws water into the stratum corneum. Shea butter adds an occlusive layer. This is the clinical standard for xerosis.
- Usage: Apply within 3 minutes of stepping out of shower to damp skin. Morning and evening if very dry.

**Lacura Med Fussbalsam Glycerin 10% Urea + Panthenol (Aldi):**
- Verdict: Great for feet.
- Mechanism: Same urea keratolysis. Panthenol (pro-vitamin B5) converts to pantothenic acid in skin, accelerates wound healing. Glycerin holds water.
- Usage: Before bed with socks on — overnight occlusion doubles efficacy.

**Lacura Med Handcreme Vitamin B3 + Urea 5% (Aldi):**
- Verdict: Good hand cream.
- Mechanism: Niacinamide (B3) at effective concentrations strengthens the skin barrier by upregulating ceramide synthesis. 5% Urea appropriate for thinner hand skin. Fragrance-free — lower irritation risk.

**NIVEA Reichhaltige Body Milk (Hyaluron + Mandelöl):**
- Verdict: Okay but weaker than Lacura Med for dry skin.
- Hyaluronic acid in body lotions is largely a marketing angle — the molecule is too large to penetrate skin topically. Functions as a surface humectant only.
- Use on less-dry days or less-affected areas.

**Lacura Sun LSF 50 Sonnenspray (Aldi) + NIVEA Sun 50+ Citracell:**
- Verdict: Both good. Lacura rated "Sehr Gut 1.5" by Stiftung Warentest (independent German consumer testing) — strong endorsement.
- NIVEA Sun has Vitamin C (antioxidant synergistic with SPF) and Hyaluron.
- Use NIVEA Sun on face (formulated for face, no white cast); Lacura Sun for body.
- SPF mandatory year-round. UV causes skin barrier degradation and premature aging through cloud cover.

**What's missing — face moisturizer:**
No dedicated face moisturizer in current routine. Lacura Med 10% Urea may be too strong for facial skin (can cause mild tingling on thinner facial epidermis).

Recommended (dm/Rossmann):
- Cetaphil Moisturizing Cream — fragrance-free, ceramide + glycerin base, dermatologist standard for dry/sensitive skin. ~€12.
- Eucerin Urea Repair Face Cream 5% — same urea science, face-appropriate concentration. ~€9.
- Budget option: Lacura Med Handcreme (5% urea, fragrance-free) applied to face — not elegant, but works.

**AM/PM skincare routine:**

| Step | AM | PM | Why |
|---|---|---|---|
| Cleanse | Rinse with lukewarm water only (no soap AM) | Gentle cleanser or water | Morning: protective overnight oils should not be stripped. Evening: remove sweat/SPF. |
| Moisturize | Face cream (Cetaphil or Eucerin 5%) on slightly damp skin | Same — slightly thicker application | Damp skin assists humectant binding. |
| SPF | NIVEA Sun 50+ on face — every single day | — | UV is the #1 skin barrier degrader, year-round. |
| Body | Lacura Med 10% Urea within 3 min of shower | Same — focus elbows, knees, shins | 3-minute window before transepidermal water loss normalizes |
| Feet | — | Lacura Fussbalsam + cotton socks | Overnight occlusion dramatically improves urea penetration |

---

### Shopping List page

**Priority purchases (dm / Rossmann / Pharmacy / Amazon.de):**

| Product | Purpose | Where | Cost | Priority |
|---|---|---|---|---|
| Nizoral 2% Shampoo | Hair loss — ketoconazole antifungal + mild DHT blocker | Pharmacy / Amazon.de | €15–18 | High |
| Doppelherz Omega-3 Kapseln | Muscle recovery, scalp health, skin barrier | dm / Rossmann | €8–12 | High |
| Doppelherz Zink Tabletten (15 mg) | Hair follicle health, testosterone support | dm / Rossmann | €5–7 | High |
| Whey Protein (ESN Classic / Lidl Beavita) | Hit 130–145 g protein target | dm / Lidl / Amazon.de | €20–35/kg | High |
| Cetaphil Moisturizing Cream or Eucerin Urea Face 5% | Face moisturizer — missing from current routine | dm / Rossmann | €9–12 | Medium |
| Bio Kokosöl (coconut oil) | Pre-wash hair treatment — reduces hygral fatigue | Lidl / Aldi / Kaufland | €3–4 | Medium |
| Cien Nature Bio-Mandel Conditioner | Moisture after ketoconazole shampoo, reduce breakage | Lidl | €1.50 | Medium |
| Regaine Männer 5% Minoxidil | Hair loss — only OTC treatment with strong clinical evidence | dm / Rossmann / Pharmacy | €25–30/month | Discuss with doctor |
| Creatine Monohydrate (Creapure) | Most-studied ergogenic aid — meaningful muscle gain acceleration | Amazon.de | €15–20/500g | Optional, high value |

---

### Myth Check page

**Claim: Olive oil + lemon juice after meals improves gut health**
Verdict: Partially misrepresented science.

**Olive oil — what the evidence actually says:**
- Extra virgin olive oil contains oleocanthal (natural COX inhibitor) and polyphenols that may support beneficial gut bacteria (Bifidobacteria, Lactobacilli).
- Mediterranean diet research (robust) shows high olive oil intake correlates with reduced colorectal cancer risk and better microbiome diversity.
- However: these benefits come from dietary incorporation over months/years — not a specific post-meal shot. No evidence that taking olive oil as a shot provides distinct benefits vs. cooking with it.
- Large amounts of oil post-meal can trigger nausea and diarrhea.

**Lemon juice — what the evidence actually says:**
- Contains citric acid and small amounts of Vitamin C. No significant evidence it improves gut health as a post-meal ritual.
- The "acidic juice improves digestion" claim is mechanistically backwards — stomach acid is pH 1.5–3.5. Lemon juice (pH ~2–3) does not meaningfully change gastric pH.
- Repeated exposure to citric acid erodes tooth enamel — documented and significant.
- May mildly slow gastric emptying (small blood glucose effect) but effect size is tiny.

**Verdict:** Skip the ritual. Cook with extra virgin olive oil — that's where the real benefit is. The Instagram framing conflates correlation in dietary patterns with causation from a specific ritual.

**What actually improves gut health (evidence-backed):**
- 30+ different plant foods per week (microbiome diversity — the Tim Spector / Zoe research)
- Fermented foods: Naturjoghurt, Kefir, Sauerkraut (every German supermarket)
- Dietary fiber: 25–38 g/day (whole grains, legumes, vegetables)
- Adequate hydration: 2–2.5 L/day
- Omega-3 fatty acids

---

## Feature Roadmap (build order)

### Phase 1 — Core (build first)
- [ ] Flask app with blueprints scaffold
- [ ] SQLite database with all models
- [ ] Overview dashboard with static content
- [ ] Workout plan page (read from `data/exercises.json`)
- [ ] Supplement schedule page (static, read from `data/supplements.json`)

### Phase 2 — Interactive
- [ ] Workout logging (POST form → database → confirmation)
- [ ] Macro tracker (live JS updating progress bars, POST to database)
- [ ] Body weight logging + Chart.js progress chart
- [ ] Exercise images fetched from Wger API

### Phase 3 — Polish
- [ ] Weekly calendar view with workout history
- [ ] Streak tracking (consecutive days logged)
- [ ] Export data as CSV
- [ ] Mobile-responsive layout
- [ ] Print-friendly shopping list

---

## Prompt for Claude Code

Use this prompt when starting the project in VS Code with Claude Code:

```
Build a personal lifestyle dashboard web app using Python Flask.

Project structure: use blueprints for routes (dashboard, workouts, nutrition, 
supplements, hair, skin). Use SQLAlchemy with SQLite for storing workout logs, 
meal logs, and body weight entries.

Frontend: Jinja2 templates + Tailwind CSS (CDN) + Chart.js (CDN) for progress charts.

Pages to build:
1. Overview — stats bar (BMI, weight, days since start), priority cards, 
   height myth info banner
2. Weekly schedule — 7-day card grid, daily timeline, running program table
3. Workouts — exercise cards with images from Wger API, sets/reps logger, 
   phase 1 and phase 2 plans
4. Supplements — timing table, current product verdicts, missing supplements
5. Meal planning — meal plans for training/rest/run days, macro tracker with 
   live JS progress bars, food database table, weekly prep checklist
6. Hair — product analysis cards, full routine table, medical warning banner
7. Skin — product verdict cards, AM/PM routine table
8. Shopping list — priority table with badges
9. Myth check — claim/verdict/evidence cards

Database models needed: WorkoutLog, ExerciseSet, MealLog, BodyMetric.

Store all static coaching content (exercises, meals, products) in JSON files 
under data/ so content is editable without touching Python.

Start with the Flask app factory, SQLAlchemy setup, and the overview dashboard 
page. Then we'll build each section one by one.
```

---

## Notes for Development

- Keep all coaching content in `data/*.json` — this is the "source of truth" for what gets displayed. Python routes just read and pass to templates.
- The database is only for user-generated data: what you logged, what you ate, your weight over time.
- All product recommendations are specific to German availability (dm, Rossmann, Lidl, Aldi, Kaufland, Amazon.de). Keep this context in the data files.
- Exercise progressions are tied to dumbbells up to 21 kg maximum — the progression tables reflect this ceiling.
- Running program assumes complete beginner baseline — do not skip weeks.
- All supplement interactions are documented in `data/supplements.json` — surface these as warnings in the UI wherever relevant.
