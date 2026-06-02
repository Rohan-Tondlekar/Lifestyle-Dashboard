from flask import Blueprint, render_template

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')


@schedule_bp.route('/')
def index():
    return render_template('schedule/index.html')
