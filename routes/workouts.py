import json
import os
from datetime import date

from flask import Blueprint, current_app, redirect, render_template, request, url_for
from flask_login import login_required

from models import db
from models.workout import ExerciseSet, WorkoutLog

workouts_bp = Blueprint('workouts', __name__, url_prefix='/workouts')


def _load_exercises():
    path = os.path.join(current_app.root_path, 'data', 'exercises.json')
    with open(path, encoding='utf-8') as f:
        return json.load(f)


@workouts_bp.route('/')
@login_required
def plan():
    exercises = _load_exercises()
    today = date.today().isoformat()
    today_sets = (ExerciseSet.query
                  .join(WorkoutLog)
                  .filter(WorkoutLog.date == today)
                  .order_by(ExerciseSet.id.asc())
                  .all())
    all_names = (
        [ex['name'] for ex in exercises['phase1']]
        + [ex['name'] for ex in exercises['phase2_upper']]
        + [ex['name'] for ex in exercises['phase2_lower']]
    )
    return render_template('workouts/plan.html',
                           exercises=exercises,
                           today_sets=today_sets,
                           all_exercise_names=sorted(set(all_names)))


@workouts_bp.route('/log', methods=['POST'])
@login_required
def log():
    today = date.today().isoformat()
    log_entry = WorkoutLog.query.filter_by(date=today).first()
    if not log_entry:
        log_entry = WorkoutLog(date=today, day_type='workout')
        db.session.add(log_entry)
        db.session.flush()
    try:
        weight_kg = float(request.form.get('weight_kg') or 0)
        reps = int(request.form.get('reps') or 0)
        set_number = int(request.form.get('set_number') or 1)
    except ValueError:
        return redirect(url_for('workouts.plan'))
    db.session.add(ExerciseSet(
        workout_id=log_entry.id,
        exercise_name=request.form.get('exercise_name', ''),
        weight_kg=weight_kg,
        reps=reps,
        set_number=set_number,
    ))
    db.session.commit()
    return redirect(url_for('workouts.plan'))
