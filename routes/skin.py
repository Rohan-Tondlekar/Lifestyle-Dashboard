import json
import os

from flask import Blueprint, current_app, render_template
from flask_login import login_required

skin_bp = Blueprint('skin', __name__, url_prefix='/skin')

_AM_PM = [
    {'step': 'Cleanse', 'am': 'Rinse with lukewarm water only (no soap AM)', 'pm': 'Gentle cleanser or water', 'why': 'Morning: protective overnight oils should not be stripped. Evening: remove sweat/SPF.'},
    {'step': 'Moisturize', 'am': 'Face cream (Cetaphil or Eucerin 5%) on slightly damp skin', 'pm': 'Same — slightly thicker application', 'why': 'Damp skin assists humectant binding.'},
    {'step': 'SPF', 'am': 'NIVEA Sun 50+ on face — every single day', 'pm': '—', 'why': 'UV is the #1 skin barrier degrader, year-round.'},
    {'step': 'Body', 'am': 'Lacura Med 10% Urea within 3 min of shower', 'pm': 'Same — focus elbows, knees, shins', 'why': '3-minute window before transepidermal water loss normalises'},
    {'step': 'Feet', 'am': '—', 'pm': 'Lacura Fussbalsam + cotton socks', 'why': 'Overnight occlusion dramatically improves urea penetration'},
]


@skin_bp.route('/')
@login_required
def routine():
    path = os.path.join(current_app.root_path, 'data', 'products.json')
    with open(path, encoding='utf-8') as f:
        all_products = json.load(f)
    skin_products = [p for p in all_products if p['category'] == 'skin']
    return render_template('skin/routine.html',
                           products=skin_products,
                           am_pm=_AM_PM)
