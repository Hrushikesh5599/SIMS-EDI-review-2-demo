from flask import Blueprint, jsonify

from app.services.team3.dashboard_service import (
    get_employee_dashboard,
    get_supplier_dashboard
)
from app.middleware.team1_auth import role_required


dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/api/dashboard"
)


@dashboard_bp.route("/employee", methods=["GET"])
@role_required("Employee")
def employee_dashboard():
    dashboard_data = get_employee_dashboard()

    return jsonify(dashboard_data), 200


@dashboard_bp.route("/supplier", methods=["GET"])
@role_required("Supplier")
def supplier_dashboard():
    dashboard_data = get_supplier_dashboard()

    return jsonify(dashboard_data), 200