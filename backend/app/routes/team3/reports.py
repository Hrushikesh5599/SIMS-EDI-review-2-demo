from flask import Blueprint, jsonify

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@reports_bp.route("/", methods=["GET"])
def get_reports():
    return jsonify({
        "message": "Reports API is working"
    })