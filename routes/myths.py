from flask import Blueprint, render_template

myths_bp = Blueprint('myths', __name__, url_prefix='/myths')


@myths_bp.route('/')
def index():
    return render_template('myths/index.html')
