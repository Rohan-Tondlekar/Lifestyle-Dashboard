from models.body import BodyMetric
from models.nutrition import MealLog
from models.workout import ExerciseSet, WorkoutLog


def test_app_creates_successfully(app):
    assert app is not None
    assert app.config['TESTING'] is True


def test_all_tables_queryable(app):
    assert BodyMetric.query.count() == 0
    assert MealLog.query.count() == 0
    assert WorkoutLog.query.count() == 0
    assert ExerciseSet.query.count() == 0
