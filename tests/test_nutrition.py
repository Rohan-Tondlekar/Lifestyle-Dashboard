from models.nutrition import MealLog


def test_nutrition_page_loads(client):
    r = client.get('/nutrition/')
    assert r.status_code == 200
    assert b'Training Day' in r.data
    assert b'Protein' in r.data


def test_nutrition_shows_food_database(client):
    r = client.get('/nutrition/')
    assert b'Magerquark' in r.data
    assert 'Hühnerbrust'.encode('utf-8') in r.data


def test_nutrition_shows_weekly_prep(client):
    r = client.get('/nutrition/')
    assert b'Sunday Batch Cook' in r.data


def test_log_meal_saves_entry(client, app):
    client.post('/nutrition/log', data={
        'meal_name': 'Breakfast',
        'protein_g': '30',
        'carbs_g': '60',
        'fat_g': '10',
        'kcal': '450',
    })
    with app.app_context():
        m = MealLog.query.first()
        assert m is not None
        assert m.meal_name == 'Breakfast'
        assert m.protein_g == 30.0
        assert m.kcal == 450


def test_macro_totals_accumulate(client, app):
    client.post('/nutrition/log', data={'meal_name': 'B', 'protein_g': '30', 'carbs_g': '60', 'fat_g': '10', 'kcal': '450'})
    client.post('/nutrition/log', data={'meal_name': 'L', 'protein_g': '45', 'carbs_g': '80', 'fat_g': '15', 'kcal': '650'})
    with app.app_context():
        assert MealLog.query.count() == 2
        total_protein = sum(m.protein_g for m in MealLog.query.all())
        assert total_protein == 75.0


def test_logged_meals_shown_on_page(client):
    client.post('/nutrition/log', data={'meal_name': 'Lunch', 'protein_g': '45', 'carbs_g': '80', 'fat_g': '15', 'kcal': '650'})
    r = client.get('/nutrition/')
    assert b"Today's Log" in r.data
    assert b'Lunch' in r.data
