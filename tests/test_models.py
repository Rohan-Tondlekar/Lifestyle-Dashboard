from models import db
from models.body import BodyMetric
from models.nutrition import MealLog
from models.workout import ExerciseSet, WorkoutLog


def test_create_body_metric(app):
    metric = BodyMetric(date='2026-06-02', weight_kg=59.0)
    db.session.add(metric)
    db.session.commit()
    fetched = BodyMetric.query.first()
    assert fetched.weight_kg == 59.0
    assert fetched.date == '2026-06-02'


def test_create_meal_log(app):
    meal = MealLog(date='2026-06-02', meal_name='Breakfast',
                   protein_g=30.0, carbs_g=60.0, fat_g=10.0, kcal=450)
    db.session.add(meal)
    db.session.commit()
    fetched = MealLog.query.first()
    assert fetched.protein_g == 30.0
    assert fetched.meal_name == 'Breakfast'


def test_create_workout_with_sets(app):
    log = WorkoutLog(date='2026-06-02', day_type='upper', completed=True)
    db.session.add(log)
    db.session.flush()
    s = ExerciseSet(workout_id=log.id, exercise_name='DB Shoulder Press',
                    weight_kg=8.0, reps=10, set_number=1)
    db.session.add(s)
    db.session.commit()
    fetched = WorkoutLog.query.first()
    assert fetched.completed is True
    assert len(fetched.sets) == 1
    assert fetched.sets[0].exercise_name == 'DB Shoulder Press'


def test_body_metric_notes_defaults_null(app):
    metric = BodyMetric(date='2026-06-02', weight_kg=60.0)
    db.session.add(metric)
    db.session.commit()
    assert BodyMetric.query.first().notes is None
