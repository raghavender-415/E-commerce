# E-commerce Flask Application

A full-featured e-commerce web application built with Flask, featuring user authentication, product catalog, shopping cart, and order management.

## 🚀 Features

- **User Authentication**: Register, login, and logout functionality
- **Product Catalog**: Browse products by category with search and filtering
- **Shopping Cart**: Add/remove items, update quantities
- **Order Management**: Place orders and view order history
- **Responsive Design**: Modern, mobile-friendly UI
- **Database**: SQLite with SQLAlchemy ORM

## 🛠️ Technologies Used

- **Backend**: Python Flask
- **Database**: SQLite with Flask-SQLAlchemy
- **Authentication**: Flask-Login
- **Frontend**: HTML5, CSS3, Jinja2 templates
- **Styling**: Custom CSS with Google Fonts

## 📋 Prerequisites

- Python 3.8 or higher
- Git

## 🔧 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/raghavender-415/E-commerce.git
   cd E-commerce
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install flask flask-sqlalchemy flask-login werkzeug
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Open in browser:**
   Navigate to `http://127.0.0.1:5000`

## 📁 Project Structure

```
E-commerce/
├── app.py                 # Main Flask application
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── products.html     # Product listing
│   ├── product_detail.html # Product details
│   ├── cart.html         # Shopping cart
│   ├── checkout.html     # Checkout page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── account.html      # User account
│   └── orders.html       # Order history
├── static/
│   └── css/
│       └── style.css     # CSS stylesheets
├── instance/
│   └── shop.db          # SQLite database
└── README.md            # This file
```

## 🎯 Usage

### For Customers:
1. **Browse Products**: Visit the home page to see featured products
2. **Search & Filter**: Use the search bar and category filters
3. **Add to Cart**: Click "Add to Cart" on product pages
4. **Checkout**: Review cart and place orders (requires login)
5. **Account Management**: View order history and account details

### Sample Data:
The application comes pre-seeded with sample products across categories:
- Electronics (Headphones, Smart Watch, Bluetooth Speaker, Laptop Stand)
- Clothing (Merino Sweater, Slim Chinos, Running Shoes)
- Books (Clean Code, Deep Work)
- Home & Garden (Ceramic Plant Pot, Scented Candles)

## 🔐 Authentication

- **Registration**: Create new accounts with username, email, and password
- **Login**: Secure login with email/password
- **Session Management**: Persistent sessions with "Remember Me" option
- **Protected Routes**: Certain pages require authentication

## 🛒 Shopping Cart Features

- **Add Items**: Add products to cart with quantity selection
- **Update Quantities**: Modify item quantities in cart
- **Remove Items**: Remove items from cart
- **Persistent Cart**: Cart contents saved in session
- **Cart Summary**: Real-time cart count and total in navigation

## 📊 Database Schema

### Users Table:
- id, username, email, password, created_at

### Categories Table:
- id, name

### Products Table:
- id, name, description, price, stock, image_url, category_id, created_at, featured

### Orders Table:
- id, user_id, items (JSON), total, status, created_at

## 🚀 Deployment

For production deployment, consider:
- Using a production WSGI server (Gunicorn, uWSGI)
- Setting up environment variables for secrets
- Using a production database (PostgreSQL, MySQL)
- Enabling HTTPS
- Setting `app.config['SECRET_KEY']` to a secure random value

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 📞 Contact

For questions or support, please open an issue on GitHub.

---

**Happy Shopping! 🛍️**