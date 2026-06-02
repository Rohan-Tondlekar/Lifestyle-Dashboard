from models import db


class BodyMetric(db.Model):
    __tablename__ = 'body_metric'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    weight_kg = db.Column(db.Float)
    notes = db.Column(db.Text)
