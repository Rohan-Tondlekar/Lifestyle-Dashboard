import json
import os

from flask import Blueprint, current_app, render_template

supplements_bp = Blueprint('supplements', __name__, url_prefix='/supplements')


def _load():
    path = os.path.join(current_app.root_path, 'data', 'supplements.json')
    with open(path, encoding='utf-8') as f:
        return json.load(f)


@supplements_bp.route('/')
def schedule_page():
    data = _load()
    return render_template('supplements/schedule.html',
                           timing_table=data['timing_table'],
                           current_products=data['current_products'],
                           missing_supplements=data['missing_supplements'])
