from flask import Flask

from config import Config
from models import db


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config:
        app.config.update(config)

    db.init_app(app)

    from models import body, nutrition, workout  # noqa: F401 — registers tables with metadata

    with app.app_context():
        db.create_all()

    from routes.dashboard import dashboard_bp
    from routes.hair import hair_bp
    from routes.myths import myths_bp
    from routes.nutrition import nutrition_bp
    from routes.schedule import schedule_bp
    from routes.shopping import shopping_bp
    from routes.skin import skin_bp
    from routes.supplements import supplements_bp
    from routes.workouts import workouts_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(workouts_bp)
    app.register_blueprint(nutrition_bp)
    app.register_blueprint(supplements_bp)
    app.register_blueprint(hair_bp)
    app.register_blueprint(skin_bp)
    app.register_blueprint(shopping_bp)
    app.register_blueprint(myths_bp)

    return app
