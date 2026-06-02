from flask import Blueprint, render_template

supplements_bp = Blueprint('supplements', __name__, url_prefix='/supplements')


@supplements_bp.route('/')
def schedule_page():
    return render_template('supplements/schedule.html')
