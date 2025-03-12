from flask import Flask, render_template, jsonify, request, redirect, url_for
import sqlite3
from datetime import datetime



app = Flask(__name__)
def get_db_connection():
    try:
        conn = sqlite3.connect('store.db')
        conn.row_factory = sqlite3.Row 
        return conn
    except Exception as e:
        print(f"Error: {e}")
        return None



@app.route('/')
def index():
    try:
        conn = get_db_connection()
        if not conn:
            return "Error!"
        brands = conn.execute('SELECT DISTINCT brand_name FROM Item').fetchall()
        categories = conn.execute('SELECT * FROM ProductCategory').fetchall()
        products = conn.execute('''
            SELECT p.*, i.model, i.brand_name, pc.category_name,
                   COALESCE(SUM(si.quantity_sold), 0) as total_sold
            FROM Product p
            JOIN Item i ON p.product_id = i.item_id
            JOIN ProductCategory pc ON i.category_I_id = pc.category_id
            LEFT JOIN SaleItem si ON p.barcode_id = si.barcode_SI_id
            GROUP BY p.barcode_id
        ''').fetchall()
        conn.close()
        return render_template('index.html', categories=categories, products=products, brands=brands)
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        if conn:
            conn.close()



@app.route('/search_brand', methods=['POST'])
def search_brand():
    try:
        brand = request.form.get('brand')
        if not brand:
            return redirect(url_for('index')) #what is it?
        conn = get_db_connection()
        if not conn:
            return "Error!"
        results = conn.execute('''
            SELECT DISTINCT
                i.brand_name as Brand,
                i.model as Model,
                p.sale_price as Original_Price,
                COALESCE(ph.new_price, p.sale_price) as New_Price,
                COALESCE(ph.change_date, 'No changes') as Date,
                p.quantity as Quantity,
                s.source_name as Source,
                sup.supplier_name as Supplier,
                sup.phone_number as Phone,
                sup.address as Address
            FROM Item i
            JOIN Product p ON i.item_id = p.product_id
            LEFT JOIN PriceHistory ph ON p.barcode_id = ph.barcode_PH_id
            LEFT JOIN ProductSupplier ps ON i.item_id = ps.product_PS_id
            LEFT JOIN Supplier sup ON ps.supplier_PS_id = sup.supplier_id
            LEFT JOIN SaleItem si ON p.barcode_id = si.barcode_SI_id
            LEFT JOIN Sale s ON si.sale_SI_id = s.sale_id
            WHERE i.brand_name = ?
            GROUP BY i.model
        ''', [brand]).fetchall()
        conn.close()
        return render_template('search_results.html', results=results, brand=brand)
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        if conn:
            conn.close()



@app.route('/api/top_products')
def top_products():
    try:
        conn = get_db_connection()
        if not conn:
            return "Error!"
        products = conn.execute('''
            SELECT 
                i.brand_name as brand,
                i.model as model,
                COALESCE(SUM(si.quantity_sold), 0) as quantity
            FROM Item i
            LEFT JOIN Product p ON i.item_id = p.product_id
            LEFT JOIN SaleItem si ON p.barcode_id = si.barcode_SI_id
            GROUP BY i.brand_name, i.model
            ORDER BY quantity DESC
            LIMIT 5
        ''').fetchall()
        profit = conn.execute('''
            SELECT 
                COALESCE(SUM((si.price_sold_without_vat - p.wholesale_price) * si.quantity_sold), 0) as profit
            FROM SaleItem si
            JOIN Product p ON si.barcode_SI_id = p.barcode_id
        ''').fetchone()
        conn.close()
        return jsonify({
            'products': [dict(row) for row in products],
            'profit': profit['profit'] / 100  # Convert cents to euros if needed
        })
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        if conn:
            conn.close()



@app.route('/api/top_categories')
def top_categories():
    try:
        conn = get_db_connection()
        if not conn:
            return "Error!"
        categories = conn.execute('''
            SELECT 
                pc.category_name as category,
                COALESCE(SUM(si.quantity_sold), 0) as quantity
            FROM ProductCategory pc
            LEFT JOIN Item i ON pc.category_id = i.category_I_id
            LEFT JOIN Product p ON i.item_id = p.product_id
            LEFT JOIN SaleItem si ON p.barcode_id = si.barcode_SI_id
            GROUP BY pc.category_name
            HAVING quantity > 0
            ORDER BY quantity DESC
        ''').fetchall()
        revenue = conn.execute('''
            SELECT COALESCE(SUM(si.price_sold_without_vat * si.quantity_sold), 0) as revenue
            FROM SaleItem si
        ''').fetchone()
        conn.close()
        return jsonify({
            'categories': [dict(row) for row in categories],
            'revenue': revenue['revenue'] / 100  # Convert cents to euros if needed
        })
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        if conn:
            conn.close()



@app.route('/api/product_details')
def product_details():
    try:
        conn = get_db_connection()
        if not conn:
            return "Error!"
        products = conn.execute('''
            SELECT 
                i.brand_name as brand,
                i.model,
                pa.attribute_name,
                pa.attribute_value,
                p.wholesale_price * 100 as wholesale_price,
                p.sale_price * 100 as sale_price,
                p.quantity,
                MIN(p.quantity, COALESCE(SUM(si.quantity_sold), 0)) as quantity_sold,
                MAX(0, p.quantity - MIN(p.quantity, COALESCE(SUM(si.quantity_sold), 0))) as remaining
            FROM Item i
            JOIN Product p ON i.item_id = p.product_id
            LEFT JOIN ProductAttribute pa ON p.barcode_id = pa.barcode_PA_id
            LEFT JOIN SaleItem si ON p.barcode_id = si.barcode_SI_id
            GROUP BY i.brand_name, i.model, pa.attribute_name, pa.attribute_value, 
                     p.wholesale_price, p.sale_price, p.quantity
        ''').fetchall()
        conn.close()
        return jsonify([dict(row) for row in products])
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        if conn:
            conn.close()



@app.route('/api/category_details')
def category_details():
    try:
        conn = get_db_connection()
        if not conn:
            return "Error!"
        categories = conn.execute('''
            SELECT 
                pc.category_name as category,
                SUM(p.quantity) as quantity,
                MIN(SUM(p.quantity), COALESCE(SUM(si.quantity_sold), 0)) as quantity_sold,
                MAX(0, SUM(p.quantity) - MIN(SUM(p.quantity), COALESCE(SUM(si.quantity_sold), 0))) as remaining
            FROM ProductCategory pc
            LEFT JOIN Item i ON pc.category_id = i.category_I_id
            LEFT JOIN Product p ON i.item_id = p.product_id
            LEFT JOIN SaleItem si ON p.barcode_id = si.barcode_SI_id
            GROUP BY pc.category_name
            HAVING SUM(p.quantity) > 0 OR SUM(si.quantity_sold) > 0
        ''').fetchall()
        conn.close()
        return jsonify([dict(row) for row in categories])
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        if conn:
            conn.close()



if __name__ == '__main__':
    app.run(debug=True)
