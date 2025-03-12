// Function to format currency
function formatCurrency(value) {
    return value ? value.toFixed(2) : '0.00';
}

// Function to load and display top products
async function loadTopProducts() {
    try {
        const response = await fetch('/api/top_products');
        const data = await response.json();
        
        const tbody = document.querySelector('#products-table tbody');
        tbody.innerHTML = '';
        
        data.products.forEach(product => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${product.brand || 'N/A'}</td>
                <td>${product.model || 'N/A'}</td>
                <td>${product.quantity || 0}</td>
            `;
            tbody.appendChild(row);
        });
        
        document.getElementById('profit').textContent = formatCurrency(data.profit);
    } catch (error) {
        console.error('Error loading top products:', error);
    }
}

// Function to load and display top categories
async function loadTopCategories() {
    try {
        const response = await fetch('/api/top_categories');
        const data = await response.json();
        
        const tbody = document.querySelector('#categories-table tbody');
        tbody.innerHTML = '';
        
        data.categories.forEach(category => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${category.category || 'N/A'}</td>
                <td>${category.quantity || 0}</td>
            `;
            tbody.appendChild(row);
        });
        
        document.getElementById('revenue').textContent = formatCurrency(data.revenue);
    } catch (error) {
        console.error('Error loading top categories:', error);
    }
}

// Function to load and display product details
async function loadProductDetails() {
    try {
        const response = await fetch('/api/product_details');
        const products = await response.json();
        
        const tbody = document.querySelector('#product-details-table tbody');
        tbody.innerHTML = '';
        
        products.forEach(product => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${product.brand || 'N/A'}</td>
                <td>${product.model || 'N/A'}</td>
                <td>${product.attribute_name || '-'}</td>
                <td>${product.attribute_value || '-'}</td>
                <td>${formatCurrency(product.wholesale_price)}€</td>
                <td>${formatCurrency(product.sale_price)}€</td>
                <td>${product.quantity || 0}</td>
                <td>${product.quantity_sold || 0}</td>
                <td>${product.remaining || 0}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading product details:', error);
    }
}

// Function to load and display category details
async function loadCategoryDetails() {
    try {
        const response = await fetch('/api/category_details');
        const categories = await response.json();
        
        const tbody = document.querySelector('#category-details-table tbody');
        tbody.innerHTML = '';
        
        categories.forEach(category => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${category.category || 'N/A'}</td>
                <td>${category.quantity || 0}</td>
                <td>${category.quantity_sold || 0}</td>
                <td>${category.remaining || 0}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading category details:', error);
    }
}

// Modal functionality
const productModal = document.getElementById('product-modal');
const categoryModal = document.getElementById('category-modal');
const closeButtons = document.getElementsByClassName('close');

// Add click event to products table
document.getElementById('products-table').addEventListener('click', () => {
    productModal.style.display = 'block';
    loadProductDetails();
});

// Add click event to categories table
document.getElementById('categories-table').addEventListener('click', () => {
    categoryModal.style.display = 'block';
    loadCategoryDetails();
});

// Close modal when clicking the close button
Array.from(closeButtons).forEach(button => {
    button.addEventListener('click', () => {
        productModal.style.display = 'none';
        categoryModal.style.display = 'none';
    });
});

// Close modal when clicking outside
window.addEventListener('click', (event) => {
    if (event.target === productModal) {
        productModal.style.display = 'none';
    }
    if (event.target === categoryModal) {
        categoryModal.style.display = 'none';
    }
});

// Load initial data
loadTopProducts();
loadTopCategories(); 