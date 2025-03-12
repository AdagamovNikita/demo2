from flask import Flask, render_template, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('store.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/top_products')
def top_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get top selling products with correct grouping and totals
    cursor.execute('''
        SELECT 
            i.brand_name, 
            i.model, 
            COALESCE(SUM(si.quantity_sold), 0) as total_sold
        FROM Item i
        LEFT JOIN Product p ON i.item_id = p.product_id
        LEFT JOIN SaleItem si ON p.barcode_id = si.barcode_SI_id
        GROUP BY i.brand_name, i.model
        ORDER BY total_sold DESC
        LIMIT 5
    ''')
    
    products = cursor.fetchall()
    result = [{'brand': row['brand_name'], 'model': row['model'], 'quantity': row['total_sold']} for row in products]
    
    # Calculate total profit with correct joins
    cursor.execute('''
        SELECT COALESCE(SUM((si.price_sold_without_vat - p.wholesale_price) * si.quantity_sold), 0) as total_profit
        FROM SaleItem si
        JOIN Product p ON si.barcode_SI_id = p.barcode_id
    ''')
    profit = cursor.fetchone()['total_profit']
    
    conn.close()
    return jsonify({'products': result, 'profit': profit})

@app.route('/api/top_categories')
def top_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get top selling categories with correct grouping and totals
    cursor.execute('''
        SELECT 
            pc.category_name, 
            COALESCE(SUM(si.quantity_sold), 0) as total_sold
        FROM ProductCategory pc
        LEFT JOIN Item i ON pc.category_id = i.category_I_id
        LEFT JOIN Product p ON i.item_id = p.product_id
        LEFT JOIN SaleItem si ON p.barcode_id = si.barcode_SI_id
        GROUP BY pc.category_name
        ORDER BY total_sold DESC
    ''')
    
    categories = cursor.fetchall()
    result = [{'category': row['category_name'], 'quantity': row['total_sold']} for row in categories]
    
    # Calculate total revenue with correct calculation
    cursor.execute('''
        SELECT COALESCE(SUM(si.price_sold_without_vat * si.quantity_sold), 0) as total_revenue
        FROM SaleItem si
    ''')
    revenue = cursor.fetchone()['total_revenue']
    
    conn.close()
    return jsonify({'categories': result, 'revenue': revenue})

@app.route('/api/product_details')
def product_details():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            i.brand_name,
            i.model,
            pa.attribute_name,
            pa.attribute_value,
            p.wholesale_price,
            p.sale_price,
            p.quantity,
            MIN(p.quantity, COALESCE(SUM(si.quantity_sold), 0)) as total_sold
        FROM Item i
        JOIN Product p ON i.item_id = p.product_id
        LEFT JOIN ProductAttribute pa ON p.barcode_id = pa.barcode_PA_id
        LEFT JOIN SaleItem si ON p.barcode_id = si.barcode_SI_id
        GROUP BY i.brand_name, i.model, pa.attribute_name, pa.attribute_value, p.wholesale_price, p.sale_price, p.quantity
        ORDER BY total_sold DESC
    ''')
    
    products = cursor.fetchall()
    result = [{
        'brand': row['brand_name'],
        'model': row['model'],
        'attribute_name': row['attribute_name'],
        'attribute_value': row['attribute_value'],
        'wholesale_price': row['wholesale_price'],
        'sale_price': row['sale_price'],
        'quantity': row['quantity'],
        'quantity_sold': row['total_sold'],
        'remaining': row['quantity'] - row['total_sold']
    } for row in products]
    
    conn.close()
    return jsonify(result)

@app.route('/api/category_details')
def category_details():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            pc.category_name,
            COUNT(DISTINCT p.barcode_id) as total_products,
            SUM(p.quantity) as total_quantity,
            MIN(SUM(p.quantity), COALESCE(SUM(si.quantity_sold), 0)) as total_sold
        FROM ProductCategory pc
        LEFT JOIN Item i ON pc.category_id = i.category_I_id
        LEFT JOIN Product p ON i.item_id = p.product_id
        LEFT JOIN SaleItem si ON p.barcode_id = si.barcode_SI_id
        GROUP BY pc.category_name
        ORDER BY total_sold DESC
    ''')
    
    categories = cursor.fetchall()
    result = [{
        'category': row['category_name'],
        'quantity': row['total_quantity'] or 0,
        'quantity_sold': row['total_sold'],
        'remaining': (row['total_quantity'] or 0) - row['total_sold']
    } for row in categories]
    
    conn.close()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True) 