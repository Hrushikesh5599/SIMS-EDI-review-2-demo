from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.team1.auth_service import login_user, change_password

auth_bp = Blueprint(
    "team1_auth",
    __name__,
    url_prefix="/api/auth"
)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({
            "error": "Username and password are required"
        }), 400

    result, error = login_user(username, password)

    if error:
        if error == "User account is inactive":
            return jsonify({
                "error": error
            }), 403

        return jsonify({
            "error": error
        }), 401

    return jsonify(result), 200

@auth_bp.route("/change-password", methods=["PUT"])
@jwt_required()
def change_user_password():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not current_password or not new_password:
        return jsonify({
            "error": "Current password and new password are required"
        }), 400

    if len(new_password) < 8:
        return jsonify({
            "error": "New password must be at least 8 characters long"
        }), 400

    user_id = get_jwt_identity()

    success, error = change_password(
        user_id,
        current_password,
        new_password
    )

    if error:
        if error == "Database error":
            return jsonify({
                "error": error
            }), 500

        if error == "User not found":
            return jsonify({
                "error": error
            }), 404

        return jsonify({
            "error": error
        }), 400

    return jsonify({
        "message": "Password changed successfully"
    }), 200