import sqlite3
from datetime import datetime, timedelta
import random

def create_database():
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ProductCategory (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Item (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        model TEXT NOT NULL,
        category_I_id INTEGER,
        brand_name TEXT NOT NULL,
        FOREIGN KEY (category_I_id) REFERENCES ProductCategory(category_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Product (
        product_id INTEGER,
        barcode_id TEXT PRIMARY KEY,
        quantity INTEGER NOT NULL,
        wholesale_price INTEGER NOT NULL,
        sale_price INTEGER NOT NULL,
        FOREIGN KEY (product_id) REFERENCES Item(item_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ProductAttribute (
        barcode_PA_id TEXT,
        attribute_id INTEGER,
        attribute_name TEXT NOT NULL,
        attribute_value TEXT NOT NULL,
        PRIMARY KEY (barcode_PA_id, attribute_id),
        FOREIGN KEY (barcode_PA_id) REFERENCES Product(barcode_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS PriceHistory (
        barcode_PH_id TEXT,
        price_id INTEGER PRIMARY KEY AUTOINCREMENT,
        old_price INTEGER NOT NULL,
        new_price INTEGER NOT NULL,
        change_date DATETIME NOT NULL,
        FOREIGN KEY (barcode_PH_id) REFERENCES Product(barcode_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS PromoCode (
        code_id TEXT PRIMARY KEY,
        discount_percentage INTEGER NOT NULL,
        valid_from DATE NOT NULL,
        valid_to DATE NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Sale (
        sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_date DATETIME NOT NULL,
        source_name TEXT NOT NULL,
        code_S_id TEXT,
        tax_rate INTEGER NOT NULL,
        total_price_without_vat INTEGER NOT NULL,
        vat_paid INTEGER NOT NULL,
        total_price_with_vat INTEGER NOT NULL,
        FOREIGN KEY (code_S_id) REFERENCES PromoCode(code_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS SaleItem (
        sale_SI_id INTEGER,
        sale_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        barcode_SI_id TEXT NOT NULL,
        quantity_sold INTEGER NOT NULL,
        price_sold_without_vat INTEGER NOT NULL,
        FOREIGN KEY (sale_SI_id) REFERENCES Sale(sale_id),
        FOREIGN KEY (barcode_SI_id) REFERENCES Product(barcode_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Supplier (
        supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_name TEXT NOT NULL,
        phone_number TEXT,
        address TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ProductSupplier (
        product_PS_id INTEGER,
        supplier_PS_id INTEGER,
        PRIMARY KEY (product_PS_id, supplier_PS_id),
        FOREIGN KEY (product_PS_id) REFERENCES Item(item_id),
        FOREIGN KEY (supplier_PS_id) REFERENCES Supplier(supplier_id)
    )
    ''')
    
    # Insert sample data
    # Categories
    categories = [
        ('Smartphones',),
        ('Laptops',),
        ('Tablets',),
        ('Accessories',)
    ]
    cursor.executemany('INSERT INTO ProductCategory (category_name) VALUES (?)', categories)
    
    # Items
    items = [
        ('iPhone 13', 1, 'Apple'),
        ('iPhone 13 Pro', 1, 'Apple'),
        ('Galaxy S21', 1, 'Samsung'),
        ('Galaxy S21 Ultra', 1, 'Samsung'),
        ('MacBook Pro 14"', 2, 'Apple'),
        ('MacBook Air M1', 2, 'Apple'),
        ('Galaxy Book Pro', 2, 'Samsung'),
        ('iPad Pro 12.9"', 3, 'Apple'),
        ('Galaxy Tab S7', 3, 'Samsung'),
        ('AirPods Pro', 4, 'Apple'),
        ('Galaxy Watch 4', 4, 'Samsung'),
        ('Apple Watch Series 7', 4, 'Apple')
    ]
    cursor.executemany('INSERT INTO Item (model, category_I_id, brand_name) VALUES (?, ?, ?)', items)
    
    # Products
    products = [
        (1, 'IP13-128-BLK', 50, 80000, 99900),
        (1, 'IP13-256-BLK', 30, 90000, 109900),
        (2, 'IP13P-128-GRY', 25, 100000, 119900),
        (2, 'IP13P-256-GRY', 20, 110000, 129900),
        (3, 'GS21-128-BLK', 40, 70000, 89900),
        (3, 'GS21-256-BLK', 35, 80000, 99900),
        (4, 'GS21U-256-BLK', 15, 100000, 119900),
        (5, 'MBP14-512-SP', 20, 150000, 199900),
        (6, 'MBA-M1-256-GRY', 30, 100000, 129900),
        (7, 'GBP-512-BLK', 25, 120000, 149900),
        (8, 'IPP-256-WHT', 15, 80000, 99900),
        (9, 'GTS7-256-BLK', 20, 60000, 79900),
        (10, 'APP-WHT', 100, 20000, 24900),
        (11, 'GWS4-44-BLK', 40, 15000, 19900),
        (12, 'AWS7-41-BLK', 35, 30000, 39900)
    ]
    cursor.executemany('INSERT INTO Product (product_id, barcode_id, quantity, wholesale_price, sale_price) VALUES (?, ?, ?, ?, ?)', products)
    
    # Product Attributes
    attributes = [
        ('IP13-128-BLK', 1, 'Color', 'Black'),
        ('IP13-256-BLK', 1, 'Color', 'Black'),
        ('IP13P-128-GRY', 1, 'Color', 'Graphite'),
        ('IP13P-256-GRY', 1, 'Color', 'Graphite'),
        ('GS21-128-BLK', 1, 'Color', 'Black'),
        ('GS21-256-BLK', 1, 'Color', 'Black'),
        ('GS21U-256-BLK', 1, 'Color', 'Black'),
        ('MBP14-512-SP', 1, 'Color', 'Space Gray'),
        ('MBA-M1-256-GRY', 1, 'Color', 'Gray'),
        ('GBP-512-BLK', 1, 'Color', 'Black'),
        ('IPP-256-WHT', 1, 'Color', 'White'),
        ('GTS7-256-BLK', 1, 'Color', 'Black'),
        ('APP-WHT', 1, 'Color', 'White'),
        ('GWS4-44-BLK', 1, 'Color', 'Black'),
        ('AWS7-41-BLK', 1, 'Color', 'Black')
    ]
    cursor.executemany('INSERT INTO ProductAttribute (barcode_PA_id, attribute_id, attribute_name, attribute_value) VALUES (?, ?, ?, ?)', attributes)
    
    # Suppliers
    suppliers = [
        ('Apple Inc.', '+1-800-275-8777', '1 Apple Park Way, Cupertino, CA 95014'),
        ('Samsung Electronics', '+82-2-2053-3000', '129 Samsung-ro, Yeongtong-gu, Suwon-si, Gyeonggi-do, South Korea')
    ]
    cursor.executemany('INSERT INTO Supplier (supplier_name, phone_number, address) VALUES (?, ?, ?)', suppliers)
    
    # Product-Supplier relationships
    product_suppliers = [
        (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (8, 1), (10, 1), (12, 1),
        (3, 2), (4, 2), (7, 2), (9, 2), (11, 2), (13, 2), (14, 2)
    ]
    cursor.executemany('INSERT INTO ProductSupplier (product_PS_id, supplier_PS_id) VALUES (?, ?)', product_suppliers)
    
    # Promo Codes
    promo_codes = [
        ('SUMMER2023', 1000, '2023-06-01', '2023-08-31'),
        ('BACK2SCHOOL', 1500, '2023-08-01', '2023-09-30')
    ]
    cursor.executemany('INSERT INTO PromoCode (code_id, discount_percentage, valid_from, valid_to) VALUES (?, ?, ?, ?)', promo_codes)
    
    # Generate sales data using simple inserts
    sales_data = [
        # Format: (sale_date, items_list)
        ('2023-07-01 10:00:00', [
            ('IP13-128-BLK', 1),
            ('MBP14-512-SP', 1),
            ('IPP-256-WHT', 1),
            ('APP-WHT', 2)
        ]),
        ('2023-07-01 14:30:00', [
            ('GS21-128-BLK', 1),
            ('MBA-M1-256-GRY', 1),
            ('GTS7-256-BLK', 1),
            ('GWS4-44-BLK', 2)
        ]),
        ('2023-07-02 11:15:00', [
            ('IP13-256-BLK', 1),
            ('GBP-512-BLK', 1),
            ('IPP-256-WHT', 1),
            ('AWS7-41-BLK', 2)
        ]),
        # Add more sales as needed following the same pattern
    ]

    # Get all product prices and store them in a dictionary for easy lookup
    cursor.execute("SELECT barcode_id, sale_price FROM Product")
    all_prices = {}  # Create an empty dictionary

    # Fill the dictionary with barcode as key and price as value
    for row in cursor.fetchall():
        barcode = row[0]
        price = row[1]
        all_prices[barcode] = price

    # Process each sale in the sales_data
    for sale_date, items in sales_data:
        # Calculate the sale totals
        # Start with zero for the subtotal
        subtotal = 0
        
        # Add up the price of each item
        for barcode, quantity in items:
            item_price = all_prices[barcode]
            item_total = item_price * quantity
            subtotal = subtotal + item_total
        
        # Calculate tax (20% VAT)
        tax_amount = int(subtotal * 0.2)
        
        # Calculate total with tax
        total_with_tax = subtotal + tax_amount
        
        # Insert the sale record
        cursor.execute('''
        INSERT INTO Sale (sale_date, source_name, tax_rate, total_price_without_vat, 
                         vat_paid, total_price_with_vat)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (sale_date, 'Store', 20, subtotal, tax_amount, total_with_tax))
        
        # Get the sale_id for the items
        sale_id = cursor.lastrowid
        
        # Insert each item in the sale
        for barcode, quantity in items:
            cursor.execute('''
            INSERT INTO SaleItem (sale_SI_id, barcode_SI_id, quantity_sold, price_sold_without_vat)
            VALUES (?, ?, ?, ?)
            ''', (sale_id, barcode, quantity, all_prices[barcode]))
            
            # Update the product quantity
            cursor.execute('''
            UPDATE Product 
            SET quantity = quantity - ? 
            WHERE barcode_id = ?
            ''', (quantity, barcode))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()
    print("Database created and populated with sample data.")