from models.workout import ExerciseSet, WorkoutLog


def test_workouts_page_loads(client):
    r = client.get('/workouts/')
    assert r.status_code == 200
    assert b'Phase 1' in r.data
    assert b'Push-up' in r.data


def test_workouts_shows_phase2(client):
    r = client.get('/workouts/')
    assert b'Phase 2' in r.data
    assert b'Upper Day' in r.data


def test_log_set_saves_entry(client, app):
    client.post('/workouts/log', data={
        'exercise_name': 'DB Shoulder Press',
        'weight_kg': '8.0',
        'reps': '10',
        'set_number': '1',
    })
    with app.app_context():
        s = ExerciseSet.query.first()
        assert s is not None
        assert s.exercise_name == 'DB Shoulder Press'
        assert s.weight_kg == 8.0
        assert s.reps == 10


def test_log_set_creates_workout_log(client, app):
    client.post('/workouts/log', data={
        'exercise_name': 'Plank',
        'weight_kg': '0',
        'reps': '30',
        'set_number': '1',
    })
    with app.app_context():
        assert WorkoutLog.query.count() == 1


def test_multiple_sets_share_one_log(client, app):
    for i in range(1, 4):
        client.post('/workouts/log', data={
            'exercise_name': 'DB Bicep Curl',
            'weight_kg': '8',
            'reps': '12',
            'set_number': str(i),
        })
    with app.app_context():
        assert WorkoutLog.query.count() == 1
        assert ExerciseSet.query.count() == 3


def test_today_sets_shown_on_page(client):
    client.post('/workouts/log', data={
        'exercise_name': 'DB Goblet Squat',
        'weight_kg': '10',
        'reps': '12',
        'set_number': '1',
    })
    r = client.get('/workouts/')
    assert b"Today's Sets" in r.data
    assert b'DB Goblet Squat' in r.data
