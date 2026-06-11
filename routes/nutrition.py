import json
import os
from datetime import date

from flask import Blueprint, current_app, redirect, render_template, request, url_for
from flask_login import login_required

from models import db
from models.nutrition import MealLog

nutrition_bp = Blueprint('nutrition', __name__, url_prefix='/nutrition')


def _load_meals():
    path = os.path.join(current_app.root_path, 'data', 'meals.json')
    with open(path, encoding='utf-8') as f:
        return json.load(f)


@nutrition_bp.route('/')
@login_required
def meals():
    data = _load_meals()
    today = date.today().isoformat()
    today_logs = MealLog.query.filter_by(date=today).all()
    totals = {
        'protein_g': sum(m.protein_g for m in today_logs),
        'carbs_g': sum(m.carbs_g for m in today_logs),
        'fat_g': sum(m.fat_g for m in today_logs),
        'kcal': sum(m.kcal for m in today_logs),
    }
    return render_template('nutrition/meals.html',
                           day_plans=data['day_plans'],
                           food_database=data['food_database'],
                           weekly_prep=data['weekly_prep'],
                           today_logs=today_logs,
                           totals=totals)


@nutrition_bp.route('/log', methods=['POST'])
@login_required
def log():
    today = date.today().isoformat()
    try:
        protein_g = float(request.form.get('protein_g') or 0)
        carbs_g = float(request.form.get('carbs_g') or 0)
        fat_g = float(request.form.get('fat_g') or 0)
        kcal = int(request.form.get('kcal') or 0)
    except ValueError:
        return redirect(url_for('nutrition.meals'))
    db.session.add(MealLog(
        date=today,
        meal_name=request.form.get('meal_name', ''),
        protein_g=protein_g,
        carbs_g=carbs_g,
        fat_g=fat_g,
        kcal=kcal,
    ))
    db.session.commit()
    return redirect(url_for('nutrition.meals'))
