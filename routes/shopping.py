from flask import Blueprint, render_template

shopping_bp = Blueprint('shopping', __name__, url_prefix='/shopping')

_ITEMS = [
    {'product': 'Nizoral 2% Shampoo', 'purpose': 'Hair loss — ketoconazole antifungal + mild DHT blocker', 'where': 'Pharmacy / Amazon.de', 'cost': '€15–18', 'priority': 'High'},
    {'product': 'Doppelherz Omega-3 Kapseln', 'purpose': 'Muscle recovery, scalp health, skin barrier', 'where': 'dm / Rossmann', 'cost': '€8–12', 'priority': 'High'},
    {'product': 'Doppelherz Zink Tabletten (15 mg)', 'purpose': 'Hair follicle health, testosterone support', 'where': 'dm / Rossmann', 'cost': '€5–7', 'priority': 'High'},
    {'product': 'Whey Protein (ESN Classic / Lidl Beavita)', 'purpose': 'Hit 130–145 g protein target', 'where': 'dm / Lidl / Amazon.de', 'cost': '€20–35/kg', 'priority': 'High'},
    {'product': 'Cetaphil Moisturizing Cream or Eucerin Urea Face 5%', 'purpose': 'Face moisturizer — missing from current routine', 'where': 'dm / Rossmann', 'cost': '€9–12', 'priority': 'Medium'},
    {'product': 'Bio Kokosöl (coconut oil)', 'purpose': 'Pre-wash hair treatment — reduces hygral fatigue', 'where': 'Lidl / Aldi / Kaufland', 'cost': '€3–4', 'priority': 'Medium'},
    {'product': 'Cien Nature Bio-Mandel Conditioner', 'purpose': 'Moisture after ketoconazole shampoo, reduce breakage', 'where': 'Lidl', 'cost': '€1.50', 'priority': 'Medium'},
    {'product': 'Regaine Männer 5% Minoxidil', 'purpose': 'Hair loss — only OTC treatment with strong clinical evidence', 'where': 'dm / Rossmann / Pharmacy', 'cost': '€25–30/month', 'priority': 'Discuss with doctor'},
    {'product': 'Creatine Monohydrate (Creapure)', 'purpose': 'Most-studied ergogenic aid — meaningful muscle gain acceleration', 'where': 'Amazon.de', 'cost': '€15–20/500g', 'priority': 'Optional'},
]


@shopping_bp.route('/')
def list_page():
    return render_template('shopping/list.html', items=_ITEMS)
