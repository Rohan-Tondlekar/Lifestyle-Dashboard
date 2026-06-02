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
