import json
import os

from flask import Blueprint, current_app, render_template

hair_bp = Blueprint('hair', __name__, url_prefix='/hair')

_ROUTINE = [
    {'step': 1, 'action': 'Pre-wash oil treatment', 'frequency': '1–2×/week', 'product': 'Coconut oil (Lidl/Aldi, ~€3) on mid-lengths. Leave 1–2 hrs. Not scalp.'},
    {'step': 2, 'action': 'Dry scalp massage', 'frequency': 'Every wash', 'product': 'Silicone brush — 2 min before water'},
    {'step': 3, 'action': 'Ketoconazole shampoo', 'frequency': '2–3×/week', 'product': 'Nizoral 2% or Terzolin — leave 5 min'},
    {'step': 4, 'action': 'Wet scalp massage', 'frequency': 'During shampoo', 'product': 'Silicone brush — 2 min'},
    {'step': 5, 'action': 'Moisturizing shampoo (rotate)', 'frequency': 'Remaining wash days', 'product': 'Cien Nature Bio-Mandel'},
    {'step': 6, 'action': 'Conditioner', 'frequency': 'Every wash', 'product': 'Mid-lengths to ends only, 2 min, rinse well'},
    {'step': 7, 'action': 'Leave-in oil (optional)', 'frequency': 'Styling days', 'product': 'Pantene Keratin Oil — 1–2 drops on ends'},
    {'step': 8, 'action': 'Towel dry', 'frequency': 'Every wash', 'product': 'Pat, don\'t rub. Microfiber towel reduces breakage.'},
]


@hair_bp.route('/')
def routine():
    path = os.path.join(current_app.root_path, 'data', 'products.json')
    with open(path, encoding='utf-8') as f:
        all_products = json.load(f)
    hair_products = [p for p in all_products if p['category'] == 'hair']
    return render_template('hair/routine.html',
                           products=hair_products,
                           routine=_ROUTINE)
