from flask import Blueprint, jsonify, request
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

@reports_bp.route("/status", methods=["GET"])
def get_inventory_status():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT status, progress, message, updated_at
            FROM "SystemStatus"
            WHERE module_name = 'Inventory'
        ''')

        row = cursor.fetchone()

        if row is None:
            return jsonify({
                "error": "Inventory status not found"
            }), 404

        return jsonify({
            "status": row[0],
            "progress": row[1],
            "message": row[2],
            "updated_at": row[3]
        }), 200

    finally:
        cursor.close()
        conn.close()

@reports_bp.route("/generate", methods=["POST"])
def generate_report():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check whether inventory is ready
        cursor.execute('''
            SELECT status, progress, message
            FROM "SystemStatus"
            WHERE module_name = 'Inventory'
        ''')

        status_row = cursor.fetchone()

        if status_row is None:
            return jsonify({
                "error": "Inventory status not found"
            }), 404

        inventory_status = status_row[0]
        progress = status_row[1]
        message = status_row[2]

        # Lock report generation while inventory is loading
        if inventory_status != "READY":
            return jsonify({
                "error": "Report generation locked",
                "status": inventory_status,
                "progress": progress,
                "message": message
            }), 423

        # Get report details
        data = request.get_json(silent=True) or {}

        report_name = data.get("report_name")
        report_type = data.get("report_type")
        generated_by = data.get("generated_by")

        if not report_name or not report_type or not generated_by:
            return jsonify({
                "error": "report_name, report_type and generated_by are required"
            }), 400

        report_data = []

        if report_type == "Inventory":
            cursor.execute('''
                SELECT
                    p.product_id,
                    p.product_name,
                    p.sku,
                    i.quantity_available,
                    p.reorder_level,
                    p.status,
                    i.last_updated
                FROM public."Products" p
                JOIN public."Inventory" i
                    ON p.product_id = i.product_id
                ORDER BY p.product_id
            ''')

            inventory_rows = cursor.fetchall()

            for inventory_row in inventory_rows:
                quantity_available = inventory_row[3]
                reorder_level = inventory_row[4]

                report_data.append({
                    "product_id": inventory_row[0],
                    "product_name": inventory_row[1],
                    "sku": inventory_row[2],
                    "quantity_available": quantity_available,
                    "reorder_level": reorder_level,
                    "status": inventory_row[5],
                    "stock_status": "LOW STOCK" if quantity_available <= reorder_level else "IN STOCK",
                    "last_updated": inventory_row[6]
                })

        # Create report record
        cursor.execute('''
            INSERT INTO "Reports"
            (
                report_name,
                report_type,
                generated_by
            )
            VALUES (%s, %s, %s)
            RETURNING report_id, report_name, report_type, generated_by, generated_on
        ''', (
            report_name,
            report_type,
            generated_by
        ))

        row = cursor.fetchone()

        conn.commit()

        return jsonify({
            "message": "Report generated successfully",
            "report": {
                "report_id": row[0],
                "report_name": row[1],
                "report_type": row[2],
                "generated_by": row[3],
                "generated_on": row[4]
            },
            "data": report_data
        }), 201

    finally:
        cursor.close()
        conn.close()
