from psycopg2 import Error
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token

from app.extensions import get_db_connection


def login_user(username, password):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''
            SELECT
                u.user_id,
                u.username,
                u.email,
                u.password_hash,
                u.status,
                r.role_name
            FROM public."Users" u
            JOIN public."Roles" r
                ON u.role_id = r.role_id
            WHERE u.username = %s
            ''',
            (username,)
        )

        user = cursor.fetchone()

        if user is None:
            return None, "Invalid username or password"

        user_id = user[0]
        db_username = user[1]
        email = user[2]
        password_hash = user[3]
        status = user[4]
        role_name = user[5]

        if status != "Active":
            return None, "User account is inactive"

        if not check_password_hash(password_hash, password):
            return None, "Invalid username or password"

        access_token = create_access_token(
            identity=str(user_id),
            additional_claims={
                "username": db_username,
                "role": role_name
            }
        )

        return {
            "access_token": access_token,
            "user": {
                "user_id": user_id,
                "username": db_username,
                "email": email,
                "role": role_name
            }
        }, None

    except Error:
        return None, "Database error"

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()