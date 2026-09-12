from flask import Blueprint, jsonify
from app.extensions import get_db_connection

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@reports_bp.route("/", methods=["GET"])
def get_reports():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT report_id, report_name, report_type, generated_by, generated_on
        FROM "Reports"
        ORDER BY report_id DESC
    ''')

    rows = cursor.fetchall()

    reports = []

    for row in rows:
        reports.append({
            "report_id": row[0],
            "report_name": row[1],
            "report_type": row[2],
            "generated_by": row[3],
            "generated_on": row[4]
        })

    cursor.close()
    conn.close()

    return jsonify(reports)