import os
from flask import Flask
from dotenv import load_dotenv
from psycopg import OperationalError

from .db import close_db


def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("FLASK_SECRET_KEY", "local-development-key-change-me"),
        DB_CONFIG={
            "host": os.getenv("DB_HOST", "127.0.0.1"),
            "port": os.getenv("DB_PORT", "5432"),
            "dbname": os.getenv("DB_NAME", "sql_injection"),
            "user": os.getenv("DB_USER", "sql_lab_app"),
            "password": os.getenv("DB_PASSWORD", ""),
        },
    )
    if test_config:
        app.config.update(test_config)

    app.teardown_appcontext(close_db)
    @app.errorhandler(OperationalError)
    def database_unavailable(_error):
        return render_database_error(), 503
    from .routes import bp
    app.register_blueprint(bp)
    return app


def render_database_error():
    from flask import render_template
    return render_template("database_error.html")

