from flask import Blueprint, render_template

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')

_WEEK = [
    {'day': 'Monday',    'type': 'Upper body lift', 'focus': 'Chest + Back',        'badge': 'upper'},
    {'day': 'Tuesday',   'type': 'Run + active rest', 'focus': 'Week 1–8 running program', 'badge': 'run'},
    {'day': 'Wednesday', 'type': 'Lower body + core', 'focus': 'Legs + Abs',         'badge': 'lower'},
    {'day': 'Thursday',  'type': 'Full rest',        'focus': 'Walk if desired',     'badge': 'rest'},
    {'day': 'Friday',    'type': 'Upper body lift',  'focus': 'Shoulders + Arms',    'badge': 'upper'},
    {'day': 'Saturday',  'type': 'Run + stretch',    'focus': 'Week 1–8 running program', 'badge': 'run'},
    {'day': 'Sunday',    'type': 'Rest / meal prep', 'focus': 'Prep for the week',   'badge': 'rest'},
]

_TIMELINE = [
    ('07:00', 'Wake. 400 ml water. Vitamin D3 with breakfast (fat-soluble).'),
    ('07:15', 'AM skincare: lukewarm face wash → face moisturizer on damp skin → SPF 50.'),
    ('07:30', 'Breakfast: 3 eggs + 80g oats + 1 banana + 200ml milk. ~600 kcal, ~30g protein.'),
    ('09:00', 'Workout (45–60 min). 500 ml water during session.'),
    ('10:00', 'Post-workout: Quark 200g + fruit, or chicken + rice. Within 60 min of training.'),
    ('13:00', 'Lunch: 150g protein + 150g rice/pasta + salad + olive oil. ~650 kcal.'),
    ('18:00', 'Dinner: 200g protein + vegetables + complex carb. Take Magnesium 500 mg with dinner.'),
    ('20:00', 'Hair routine on wash days (scalp massage → shampoo → condition).'),
    ('21:30', 'PM skincare + Lacura Med 10% Urea on body within 3 min of shower. Fussbalsam on feet with socks.'),
    ('22:00', 'Optional: 200g Quark before bed (casein for overnight muscle repair).'),
]

_RUNNING = [
    {'weeks': '1–2', 'structure': '1 min jog / 2 min walk × 8 rounds', 'run_time': '~8 min running', 'rpe': '4–5/10'},
    {'weeks': '3–4', 'structure': '2 min jog / 1 min walk × 8 rounds', 'run_time': '~16 min running', 'rpe': '5/10'},
    {'weeks': '5–6', 'structure': '5 min jog / 1 min walk × 4 rounds', 'run_time': '~20 min running', 'rpe': '5–6/10'},
    {'weeks': '7',   'structure': '10 min jog / 1 min walk × 2',        'run_time': '~20 min',         'rpe': '6/10'},
    {'weeks': '8',   'structure': '20 min continuous jog (slow pace)',   'run_time': '20 min',          'rpe': '6/10'},
]


@schedule_bp.route('/')
def index():
    return render_template('schedule/index.html',
                           week=_WEEK,
                           timeline=_TIMELINE,
                           running=_RUNNING)
