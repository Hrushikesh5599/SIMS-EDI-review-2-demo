from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.extensions import get_db_connection


def verify_active_user():
    conn = None
    cursor = None

    try:
        user_id = get_jwt_identity()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''
            SELECT status
            FROM public."Users"
            WHERE user_id = %s
            ''',
            (user_id,)
        )

        user = cursor.fetchone()

        if user is None:
            return False, "User account not found"

        if user[0] != "Active":
            return False, "User account is inactive"

        return True, None

    except Exception:
        return False, "Database error"

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


def role_required(*allowed_roles):
    def decorator(function):
        @wraps(function)
        @jwt_required()
        def wrapper(*args, **kwargs):

            active, error = verify_active_user()

            if not active:
                if error == "Database error":
                    return jsonify({
                        "error": error
                    }), 500

                return jsonify({
                    "error": error
                }), 403

            claims = get_jwt()
            user_role = claims.get("role")

            if user_role not in allowed_roles:
                return jsonify({
                    "error": "Access denied",
                    "message": "You do not have permission to perform this action"
                }), 403

            return function(*args, **kwargs)

        return wrapper

    return decorator