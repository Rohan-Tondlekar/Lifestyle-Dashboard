from models.body import BodyMetric


def test_overview_default_weight(client):
    r = client.get('/')
    assert r.status_code == 200
    assert b'59' in r.data


def test_overview_default_bmi(client):
    r = client.get('/')
    assert b'20.4' in r.data


def test_overview_priority_cards(client):
    r = client.get('/')
    assert b'Nutrition' in r.data
    assert b'Resistance Training' in r.data
    assert b'Hair Fall' in r.data
    assert b'Skin Barrier' in r.data
    assert b'Running Stamina' in r.data


def test_overview_height_banner(client):
    r = client.get('/')
    assert b'Height at 24' in r.data
    assert b'Growth plates' in r.data


def test_log_body_saves_entry(client, app):
    client.post('/body/log', data={'weight_kg': '60.5'})
    with app.app_context():
        m = BodyMetric.query.first()
        assert m is not None
        assert m.weight_kg == 60.5


def test_log_body_updates_same_day(client, app):
    client.post('/body/log', data={'weight_kg': '60.0'})
    client.post('/body/log', data={'weight_kg': '61.5'})
    with app.app_context():
        assert BodyMetric.query.count() == 1
        assert BodyMetric.query.first().weight_kg == 61.5


def test_overview_shows_logged_weight(client):
    client.post('/body/log', data={'weight_kg': '62.0'})
    r = client.get('/')
    assert b'62.0' in r.data
