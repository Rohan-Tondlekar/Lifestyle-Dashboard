from flask import Blueprint, render_template

skin_bp = Blueprint('skin', __name__, url_prefix='/skin')


@skin_bp.route('/')
def routine():
    return render_template('skin/routine.html')
