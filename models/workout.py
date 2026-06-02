from models import db


class WorkoutLog(db.Model):
    __tablename__ = 'workout_log'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    day_type = db.Column(db.String(20))
    completed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    sets = db.relationship('ExerciseSet', backref='workout', lazy=True,
                           cascade='all, delete-orphan')


class ExerciseSet(db.Model):
    __tablename__ = 'exercise_set'
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout_log.id'), nullable=False)
    exercise_name = db.Column(db.String(100), nullable=False)
    weight_kg = db.Column(db.Float)
    reps = db.Column(db.Integer)
    set_number = db.Column(db.Integer)
