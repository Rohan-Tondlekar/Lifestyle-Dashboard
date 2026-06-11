from flask import Flask
from flask_login import LoginManager

from config import Config
from models import db, User


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config:
        app.config.update(config)

    db.init_app(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Redirect to login page if not authenticated
    login_manager.login_message = 'Please log in to access this page.'

    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID from database."""
        return User.query.get(int(user_id))

    from models import body, nutrition, workout  # noqa: F401 — registers tables with metadata

    with app.app_context():
        db.create_all()

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.hair import hair_bp
    from routes.myths import myths_bp
    from routes.nutrition import nutrition_bp
    from routes.schedule import schedule_bp
    from routes.shopping import shopping_bp
    from routes.skin import skin_bp
    from routes.supplements import supplements_bp
    from routes.workouts import workouts_bp

    # Register auth blueprint FIRST (before protected routes)
    app.register_blueprint(auth_bp)

    # Register all other blueprints (will be protected by @login_required)
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
