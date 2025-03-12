# Store Dashboard

A simple interactive dashboard that displays store sales data using Python+Flask for the backend, HTML+CSS+JS for the frontend, and SQLite3 for the database.

## Features

- Display top selling products with brand, model, and quantity sold
- Display top selling categories with category name and quantity sold
- Show total profit from all sales
- Show total revenue from all sales
- Interactive tables that open detailed views when clicked
- Detailed product view showing additional information like attributes, prices, and stock levels
- Detailed category view showing total products, quantities, and sales

## Technologies Used

- Backend: Python 3.x with Flask
- Frontend: HTML5, CSS3, JavaScript
- Database: SQLite3

## Setup Instructions

1. Clone the repository:
```bash
git clone <your-repository-url>
cd store-dashboard
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
python setup_db.py
```

5. Run the application:
```bash
python app.py
```

6. Open your web browser and navigate to `http://localhost:5000`

## Project Structure

- `app.py` - Main Flask application with routes and database queries
- `setup_db.py` - Database creation and sample data population
- `templates/` - HTML templates
  - `index.html` - Main dashboard template
- `static/` - Static files
  - `style.css` - CSS styles
  - `script.js` - JavaScript for interactivity

## Database Schema

The database consists of multiple tables:
- ProductCategory
- Item
- Product
- ProductAttribute
- PriceHistory
- Sale
- SaleItem
- Supplier
- ProductSupplier
- PromoCode

## Notes

- All prices in the database are stored in cents to avoid floating-point arithmetic
- The dashboard automatically updates when the page is loaded
- Clicking on tables opens modal windows with detailed information 