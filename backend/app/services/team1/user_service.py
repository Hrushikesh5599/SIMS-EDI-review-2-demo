from psycopg2 import Error
from werkzeug.security import generate_password_hash

from app.extensions import get_db_connection


def create_user(username, email, password, role_name, creator_role):
    conn = None
    cursor = None

    try:
        # Check whether the creator is allowed to create the requested role
        allowed_roles = {
            "Owner": ["Owner", "Manager", "Employee", "Supplier"],
            "Manager": ["Employee", "Supplier"]
        }

        if creator_role not in allowed_roles:
            return None, "You do not have permission to create users"

        if role_name not in allowed_roles[creator_role]:
            return None, f"{creator_role} cannot create a {role_name} account"

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check whether username already exists
        cursor.execute(
            '''
            SELECT user_id
            FROM public."Users"
            WHERE username = %s
            ''',
            (username,)
        )

        if cursor.fetchone():
            return None, "Username already exists"

        # Check whether email already exists
        cursor.execute(
            '''
            SELECT user_id
            FROM public."Users"
            WHERE email = %s
            ''',
            (email,)
        )

        if cursor.fetchone():
            return None, "Email already exists"

        # Find the requested role
        cursor.execute(
            '''
            SELECT role_id
            FROM public."Roles"
            WHERE role_name = %s
            ''',
            (role_name,)
        )

        role = cursor.fetchone()

        if role is None:
            return None, "Invalid role"

        role_id = role[0]

        # Hash the initial password before storing it
        password_hash = generate_password_hash(password)

        # Create the user
        cursor.execute(
            '''
            INSERT INTO public."Users"
            (username, email, password_hash, role_id, status)
            VALUES (%s, %s, %s, %s, 'Active')
            RETURNING user_id, username, email, role_id, status
            ''',
            (username, email, password_hash, role_id)
        )

        new_user = cursor.fetchone()

        conn.commit()

        return {
            "user_id": new_user[0],
            "username": new_user[1],
            "email": new_user[2],
            "role_id": new_user[3],
            "status": new_user[4]
        }, None

    except Error:
        if conn:
            conn.rollback()

        return None, "Database error"

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()