from flask import Blueprint, render_template

hair_bp = Blueprint('hair', __name__, url_prefix='/hair')


@hair_bp.route('/')
def routine():
    return render_template('hair/routine.html')
