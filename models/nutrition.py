from models import db


class MealLog(db.Model):
    __tablename__ = 'meal_log'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    meal_name = db.Column(db.String(50))
    protein_g = db.Column(db.Float, default=0)
    carbs_g = db.Column(db.Float, default=0)
    fat_g = db.Column(db.Float, default=0)
    kcal = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)
