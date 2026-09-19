from psycopg2 import Error

from app.extensions import get_db_connection


def create_category(category_name, description):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''
            SELECT category_id
            FROM public."Categories"
            WHERE LOWER(category_name) = LOWER(%s)
            ''',
            (category_name,)
        )

        if cursor.fetchone():
            return None, "Category already exists"

        cursor.execute(
            '''
            INSERT INTO public."Categories"
            (category_name, description)
            VALUES (%s, %s)
            RETURNING category_id, category_name, description
            ''',
            (category_name, description)
        )

        row = cursor.fetchone()

        conn.commit()

        return {
            "category_id": row[0],
            "category_name": row[1],
            "description": row[2]
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


def get_categories(search=None):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = '''
            SELECT
                category_id,
                category_name,
                description
            FROM public."Categories"
        '''

        parameters = []

        if search:
            query += '''
                WHERE category_name ILIKE %s
            '''
            parameters.append(f"%{search}%")

        query += '''
            ORDER BY category_id
        '''

        cursor.execute(query, tuple(parameters))

        rows = cursor.fetchall()

        categories = []

        for row in rows:
            categories.append({
                "category_id": row[0],
                "category_name": row[1],
                "description": row[2]
            })

        return categories, None

    except Error:
        return None, "Database error"

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


def get_category_by_id(category_id):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''
            SELECT
                category_id,
                category_name,
                description
            FROM public."Categories"
            WHERE category_id = %s
            ''',
            (category_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None, "Category not found"

        category = {
            "category_id": row[0],
            "category_name": row[1],
            "description": row[2]
        }

        return category, None

    except Error:
        return None, "Database error"

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


def update_category(category_id, category_name, description):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''
            SELECT category_id
            FROM public."Categories"
            WHERE LOWER(category_name) = LOWER(%s)
              AND category_id != %s
            ''',
            (category_name, category_id)
        )

        if cursor.fetchone():
            return None, "Category already exists"

        cursor.execute(
            '''
            UPDATE public."Categories"
            SET
                category_name = %s,
                description = %s
            WHERE category_id = %s
            RETURNING category_id, category_name, description
            ''',
            (category_name, description, category_id)
        )

        row = cursor.fetchone()

        if row is None:
            return None, "Category not found"

        conn.commit()

        return {
            "category_id": row[0],
            "category_name": row[1],
            "description": row[2]
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


def delete_category(category_id):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''
            SELECT category_id
            FROM public."Categories"
            WHERE category_id = %s
            ''',
            (category_id,)
        )

        if cursor.fetchone() is None:
            return False, "Category not found"

        cursor.execute(
            '''
            SELECT product_id
            FROM public."Products"
            WHERE category_id = %s
            LIMIT 1
            ''',
            (category_id,)
        )

        if cursor.fetchone():
            return False, "Category cannot be deleted because products are assigned to it"

        cursor.execute(
            '''
            DELETE FROM public."Categories"
            WHERE category_id = %s
            ''',
            (category_id,)
        )

        conn.commit()

        return True, None

    except Error:
        if conn:
            conn.rollback()

        return False, "Database error"

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()