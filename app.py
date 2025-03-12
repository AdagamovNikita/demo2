from flask import Flask, render_template, jsonify
import sqlite3

# Create our Flask app
app = Flask(__name__)

# Simple function to get database data with error handling
def get_data_from_database(query):
    try:
        # Connect to database
        connection = sqlite3.connect('store.db')
        # This makes results accessible by column name
        connection.row_factory = sqlite3.Row
        # Create cursor
        cursor = connection.cursor()
        # Run the query
        cursor.execute(query)
        # Get all results
        results = cursor.fetchall()
        # Close connection
        connection.close()
        # Return results
        return results
    except Exception as e:
        # If anything goes wrong, print the error
        print(f"Database error: {e}")
        # Return empty list if there's an error
        return []

# Simple function to get a single value from database with error handling
def get_single_value(query, default_value=0):
    try:
        # Connect to database
        connection = sqlite3.connect('store.db')
        # This makes results accessible by column name
        connection.row_factory = sqlite3.Row
        # Create cursor
        cursor = connection.cursor()
        # Run the query
        cursor.execute(query)
        # Get just one result
        result = cursor.fetchone()
        # Close connection
        connection.close()
        # Return the result
        return result
    except Exception as e:
        # If anything goes wrong, print the error
        print(f"Database error: {e}")
        # Return a dictionary with default value if there's an error
        return {'total_profit': default_value, 'total_revenue': default_value}

# Main page
@app.route('/')
def home_page():
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Error loading home page: {e}")
        return "Sorry, there was a problem loading the page."

# Top selling products
@app.route('/api/top_products')
def top_products():
    try:
        # Query for top 5 products
        products_query = """
            SELECT 
                i.brand_name, 
                i.model, 
                SUM(IFNULL(si.quantity_sold, 0)) as total_sold
            FROM Item i
            LEFT JOIN Product p ON i.item_id = p.product_id
            LEFT JOIN SaleItem si ON p.barcode_id = si.barcode_SI_id
            GROUP BY i.brand_name, i.model
            ORDER BY total_sold DESC
            LIMIT 5
        """
        
        # Get product data
        products_data = get_data_from_database(products_query)
        
        # Convert database results to simple dictionaries
        products_list = []
        for product in products_data:
            product_dict = {
                'brand': product['brand_name'], 
                'model': product['model'], 
                'quantity': product['total_sold']
            }
            products_list.append(product_dict)
        
        # Query for total profit
        profit_query = """
            SELECT SUM(IFNULL((si.price_sold_without_vat - p.wholesale_price) * si.quantity_sold, 0)) as total_profit
            FROM SaleItem si
            JOIN Product p ON si.barcode_SI_id = p.barcode_id
        """
        
        # Get profit data
        profit_data = get_single_value(profit_query)
        total_profit = profit_data['total_profit']
        
        # Create result dictionary
        result = {
            'products': products_list, 
            'profit': total_profit
        }
        
        # Return as JSON
        return jsonify(result)
    except Exception as e:
        print(f"Error in top_products: {e}")
        return jsonify({'error': 'Could not fetch top products', 'products': [], 'profit': 0})

# Top selling categories
@app.route('/api/top_categories')
def top_categories():
    try:
        # Query for categories with sales
        categories_query = """
            SELECT 
                pc.category_name,
                SUM(IFNULL(si.quantity_sold, 0)) as total_sold
            FROM ProductCategory pc
            LEFT JOIN Item i ON pc.category_id = i.category_I_id
            LEFT JOIN Product p ON i.item_id = p.product_id
            LEFT JOIN SaleItem si ON p.barcode_id = si.barcode_SI_id
            GROUP BY pc.category_name
            HAVING total_sold > 0
            ORDER BY total_sold DESC
        """
        
        # Get category data
        categories_data = get_data_from_database(categories_query)
        
        # Convert to simple dictionaries
        categories_list = []
        for category in categories_data:
            category_dict = {
                'category': category['category_name'], 
                'quantity': category['total_sold']
            }
            categories_list.append(category_dict)
        
        # Query for total revenue
        revenue_query = """
            SELECT SUM(IFNULL(si.price_sold_without_vat * si.quantity_sold, 0)) as total_revenue
            FROM SaleItem si
        """
        
        # Get revenue data
        revenue_data = get_single_value(revenue_query)
        total_revenue = revenue_data['total_revenue']
        
        # Create result dictionary
        result = {
            'categories': categories_list, 
            'revenue': total_revenue
        }
        
        # Return as JSON
        return jsonify(result)
    except Exception as e:
        print(f"Error in top_categories: {e}")
        return jsonify({'error': 'Could not fetch top categories', 'categories': [], 'revenue': 0})

# Detailed product information
@app.route('/api/product_details')
def product_details():
    try:
        # Query for detailed product info
        products_query = """
            SELECT 
                i.brand_name,
                i.model,
                pa.attribute_name,
                pa.attribute_value,
                p.wholesale_price,
                p.sale_price,
                p.quantity,
                MIN(p.quantity, SUM(IFNULL(si.quantity_sold, 0))) as total_sold
            FROM Item i
            JOIN Product p ON i.item_id = p.product_id
            LEFT JOIN ProductAttribute pa ON p.barcode_id = pa.barcode_PA_id
            LEFT JOIN SaleItem si ON p.barcode_id = si.barcode_SI_id
            GROUP BY i.brand_name, i.model, pa.attribute_name, pa.attribute_value, p.wholesale_price, p.sale_price, p.quantity
            ORDER BY total_sold DESC
        """
        
        # Get product data
        products_data = get_data_from_database(products_query)
        
        # Convert to simple dictionaries with remaining stock calculation
        products_list = []
        for product in products_data:
            stock = product['quantity']
            sold = product['total_sold']
            remaining = stock - sold
            
            product_dict = {
                'brand': product['brand_name'],
                'model': product['model'],
                'attribute_name': product['attribute_name'],
                'attribute_value': product['attribute_value'],
                'wholesale_price': product['wholesale_price'],
                'sale_price': product['sale_price'],
                'quantity': stock,
                'quantity_sold': sold,
                'remaining': remaining
            }
            products_list.append(product_dict)
        
        # Return as JSON
        return jsonify(products_list)
    except Exception as e:
        print(f"Error in product_details: {e}")
        return jsonify([{'error': 'Could not fetch product details'}])

# Detailed category information
@app.route('/api/category_details')
def category_details():
    try:
        # Query for detailed category info
        categories_query = """
            SELECT 
                pc.category_name,
                COUNT(DISTINCT p.barcode_id) as total_products,
                SUM(IFNULL(p.quantity, 0)) as total_quantity,
                SUM(IFNULL(si.quantity_sold, 0)) as total_sold
            FROM ProductCategory pc
            LEFT JOIN Item i ON pc.category_id = i.category_I_id
            LEFT JOIN Product p ON i.item_id = p.product_id
            LEFT JOIN SaleItem si ON p.barcode_id = si.barcode_SI_id
            GROUP BY pc.category_name
            HAVING total_products > 0 OR total_sold > 0
            ORDER BY total_sold DESC
        """
        
        # Get category data
        categories_data = get_data_from_database(categories_query)
        
        # Convert to simple dictionaries with remaining stock calculation
        categories_list = []
        for category in categories_data:
            stock = category['total_quantity']
            sold = category['total_sold']
            remaining = stock - sold
            
            category_dict = {
                'category': category['category_name'],
                'quantity': stock,
                'quantity_sold': sold,
                'remaining': remaining
            }
            categories_list.append(category_dict)
        
        # Return as JSON
        return jsonify(categories_list)
    except Exception as e:
        print(f"Error in category_details: {e}")
        return jsonify([{'error': 'Could not fetch category details'}])

# Start the application
if __name__ == '__main__':
    try:
        app.run(debug=True)
    except Exception as e:
        print(f"Error starting Flask app: {e}")