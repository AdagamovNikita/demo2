import sqlite3

def test_database():
    try:
        # Connect to database
        conn = sqlite3.connect('store.db')
        cursor = conn.cursor()
        
        # Test queries
        print("Checking database contents:")
        
        # Check ProductCategory
        cursor.execute("SELECT COUNT(*) FROM ProductCategory")
        print(f"Number of categories: {cursor.fetchone()[0]}")
        
        # Check Item
        cursor.execute("SELECT COUNT(*) FROM Item")
        print(f"Number of items: {cursor.fetchone()[0]}")
        
        # Check Product
        cursor.execute("SELECT COUNT(*) FROM Product")
        print(f"Number of products: {cursor.fetchone()[0]}")
        
        # Check SaleItem
        cursor.execute("SELECT COUNT(*) FROM SaleItem")
        print(f"Number of sale items: {cursor.fetchone()[0]}")
        
        # Test top products query
        print("\nTesting top products query:")
        cursor.execute('''
            SELECT i.brand_name, i.model, COALESCE(SUM(si.quantity_sold), 0) as total_sold
            FROM Item i
            LEFT JOIN Product p ON i.item_id = p.product_id
            LEFT JOIN SaleItem si ON p.barcode_id = si.barcode_SI_id
            GROUP BY i.brand_name, i.model
            ORDER BY total_sold DESC
            LIMIT 5
        ''')
        for row in cursor.fetchall():
            print(f"Brand: {row[0]}, Model: {row[1]}, Sold: {row[2]}")
            
        conn.close()
        print("\nDatabase check completed successfully!")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_database() 