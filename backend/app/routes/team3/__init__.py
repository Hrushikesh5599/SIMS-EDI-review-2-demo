from flask import Flask
from flask_jwt_extended import JWTManager

from app.config import JWT_SECRET_KEY
from app.routes.team3.reports import reports_bp
from app.routes.team3.dashboard import dashboard_bp
from app.routes.team3.notifications import notifications_bp


def create_app():
    app = Flask(__name__)

    app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
    JWTManager(app)

    app.register_blueprint(reports_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(notifications_bp)

    return app