from flask import Blueprint, render_template

nutrition_bp = Blueprint('nutrition', __name__, url_prefix='/nutrition')


@nutrition_bp.route('/')
def meals():
    return render_template('nutrition/meals.html')
