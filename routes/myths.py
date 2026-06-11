from flask import Blueprint, render_template
from flask_login import login_required

myths_bp = Blueprint('myths', __name__, url_prefix='/myths')

_MYTHS = [
    {
        'claim': 'Olive oil + lemon juice after meals improves gut health',
        'verdict': 'Partially misrepresented',
        'verdict_color': 'amber',
        'sections': [
            {
                'heading': 'Olive oil — what the evidence actually says',
                'body': 'Extra virgin olive oil contains oleocanthal (natural COX inhibitor) and polyphenols that may support beneficial gut bacteria (Bifidobacteria, Lactobacilli). Mediterranean diet research (robust) shows high olive oil intake correlates with reduced colorectal cancer risk and better microbiome diversity. However: these benefits come from dietary incorporation over months/years — not a specific post-meal shot. No evidence that taking olive oil as a shot provides distinct benefits vs. cooking with it. Large amounts of oil post-meal can trigger nausea and diarrhoea.',
            },
            {
                'heading': 'Lemon juice — what the evidence actually says',
                'body': 'Contains citric acid and small amounts of Vitamin C. No significant evidence it improves gut health as a post-meal ritual. The "acidic juice improves digestion" claim is mechanistically backwards — stomach acid is pH 1.5–3.5. Lemon juice (pH ~2–3) does not meaningfully change gastric pH. Repeated exposure to citric acid erodes tooth enamel. May mildly slow gastric emptying but the effect size is tiny.',
            },
        ],
        'verdict_text': 'Skip the ritual. Cook with extra virgin olive oil — that\'s where the real benefit is. The framing conflates correlation in dietary patterns with causation from a specific ritual.',
        'evidence': [
            'Cook with extra virgin olive oil — 2+ tbsp/day in food',
            '30+ different plant foods per week (microbiome diversity)',
            'Fermented foods: Naturjoghurt, Kefir, Sauerkraut',
            'Dietary fibre: 25–38 g/day (whole grains, legumes, vegetables)',
            'Adequate hydration: 2–2.5 L/day',
        ],
    },
]


@myths_bp.route('/')
@login_required
def index():
    return render_template('myths/index.html', myths=_MYTHS)
