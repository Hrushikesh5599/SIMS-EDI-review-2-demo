from flask import Flask
from app.routes.team3.reports import reports_bp


def create_app():
    app = Flask(__name__)

    app.register_blueprint(reports_bp)

    return app