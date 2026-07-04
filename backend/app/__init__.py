"""
Flask application factory.
Creates and configures the Flask app, registers all blueprints,
initialises the DB, and starts the APScheduler simulator.
"""

from flask import Flask
from flask_cors import CORS
from .db import db, init_db
from .realtime import socketio
from .routes.health import health_bp
from .routes.devices import devices_bp
from .routes.rooms import rooms_bp
from .routes.usage import usage_bp
from .routes.alerts import alerts_bp


def create_app():
    app = Flask(__name__)

    # Load config from environment
    import os
    from dotenv import load_dotenv
    load_dotenv()

    # Use SQLite if USE_SQLITE=true is set (no MySQL required)
    if os.getenv("USE_SQLITE", "false").lower() == "true":
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "office_iot.db")
        db_path = os.path.abspath(db_path)
        db_uri = f"sqlite:///{db_path}"
        print(f"[DB] Using SQLite: {db_path}")
    else:
        mysql_user = os.getenv("MYSQL_USER", "root")
        mysql_password = os.getenv("MYSQL_PASSWORD", "")
        mysql_host = os.getenv("MYSQL_HOST", "localhost")
        mysql_port = os.getenv("MYSQL_PORT", "3306")
        mysql_db = os.getenv("MYSQL_DB", "office_iot")
        db_uri = (
            f"mysql+pymysql://{mysql_user}:{mysql_password}"
            f"@{mysql_host}:{mysql_port}/{mysql_db}"
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

    # Extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(usage_bp)
    app.register_blueprint(alerts_bp)

    # Create tables + seed data on first run
    with app.app_context():
        init_db()

    return app
