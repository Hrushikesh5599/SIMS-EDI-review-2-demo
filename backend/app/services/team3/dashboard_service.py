from app.extensions import get_db_connection


def get_employee_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Total number of products
        cursor.execute('SELECT COUNT(*) FROM "Products"')
        total_products = cursor.fetchone()[0]

        # Total available stock
        cursor.execute('SELECT COALESCE(SUM(quantity_available), 0) FROM "Inventory"')
        total_stock = cursor.fetchone()[0]

        # Stock in
        cursor.execute('''
            SELECT COALESCE(SUM(quantity), 0)
            FROM "StockTransactions"
            WHERE transaction_type = 'STOCK_IN'
        ''')
        stock_in = cursor.fetchone()[0]

        # Stock out
        cursor.execute('''
            SELECT COALESCE(SUM(quantity), 0)
            FROM "StockTransactions"
            WHERE transaction_type = 'STOCK_OUT'
        ''')
        stock_out = cursor.fetchone()[0]

        # Low-stock products
        cursor.execute('''
            SELECT
                p.product_id,
                p.product_name,
                i.quantity_available
            FROM "Products" p
            JOIN "Inventory" i
                ON p.product_id = i.product_id
            WHERE i.quantity_available <= 10
            ORDER BY i.quantity_available ASC
        ''')
        low_stock_rows = cursor.fetchall()

        low_stock_products = []

        for row in low_stock_rows:
            low_stock_products.append({
                "product_id": row[0],
                "product_name": row[1],
                "quantity_available": row[2]
            })

        return {
            "total_products": total_products,
            "total_stock": total_stock,
            "stock_in": stock_in,
            "stock_out": stock_out,
            "low_stock_products": low_stock_products
        }

    finally:
        cursor.close()
        conn.close()

def get_supplier_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Total purchase orders
        cursor.execute('SELECT COUNT(*) FROM "PurchaseOrders"')
        total_purchase_orders = cursor.fetchone()[0]

        # Received orders
        cursor.execute('''
            SELECT COUNT(*)
            FROM "PurchaseOrders"
            WHERE status = 'Received'
        ''')
        received_orders = cursor.fetchone()[0]

        # Completed orders
        cursor.execute('''
            SELECT COUNT(*)
            FROM "PurchaseOrders"
            WHERE status = 'Completed'
        ''')
        completed_orders = cursor.fetchone()[0]

        # Total purchase amount
        cursor.execute('''
            SELECT COALESCE(SUM(total_amount), 0)
            FROM "PurchaseOrders"
        ''')
        total_purchase_amount = cursor.fetchone()[0]

        # Total quotations
        cursor.execute('SELECT COUNT(*) FROM "SupplierQuotations"')
        total_quotations = cursor.fetchone()[0]

        # Pending quotations
        cursor.execute('''
            SELECT COUNT(*)
            FROM "SupplierQuotations"
            WHERE status = 'Pending'
        ''')
        pending_quotations = cursor.fetchone()[0]

        # Approved quotations
        cursor.execute('''
            SELECT COUNT(*)
            FROM "SupplierQuotations"
            WHERE status = 'Approved'
        ''')
        approved_quotations = cursor.fetchone()[0]

        return {
            "total_purchase_orders": total_purchase_orders,
            "received_orders": received_orders,
            "completed_orders": completed_orders,
            "total_purchase_amount": float(total_purchase_amount),
            "total_quotations": total_quotations,
            "pending_quotations": pending_quotations,
            "approved_quotations": approved_quotations
        }

    finally:
        cursor.close()
        conn.close()