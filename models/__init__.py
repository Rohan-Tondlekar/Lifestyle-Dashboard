from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models to register them with metadata
from models.user import User  # noqa: F401
from models.body import BodyMetric  # noqa: F401
from models.nutrition import MealLog  # noqa: F401
from models.workout import WorkoutLog, ExerciseSet  # noqa: F401
