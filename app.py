from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


# ─── Models ────────────────────────────────────────────────────────────────────

class User(UserMixin, db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80),  unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders     = db.relationship('Order', backref='user', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Category(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(50), nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)


class Product(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price       = db.Column(db.Float, nullable=False)
    stock       = db.Column(db.Integer, default=0)
    image_url   = db.Column(db.String(300), default='')
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    featured    = db.Column(db.Boolean, default=False)


class Order(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items      = db.Column(db.Text, nullable=False)   # JSON
    total      = db.Column(db.Float, nullable=False)
    status     = db.Column(db.String(30), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─── Cart helpers ───────────────────────────────────────────────────────────────

def get_cart():
    return session.get('cart', {})

def save_cart(cart):
    session['cart'] = cart
    session.modified = True

def cart_count():
    return sum(item['qty'] for item in get_cart().values())

def cart_total():
    return sum(item['price'] * item['qty'] for item in get_cart().values())

app.jinja_env.globals.update(cart_count=cart_count, cart_total=cart_total)


# ─── Routes: Auth ──────────────────────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username'].strip()
        email    = request.form['email'].strip().lower()
        password = request.form['password']
        confirm  = request.form['confirm']

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'error')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('register'))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Welcome, {username}!', 'success')
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email    = request.form['email'].strip().lower()
        password = request.form['password']
        user     = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=request.form.get('remember'))
            flash(f'Welcome back, {user.username}!', 'success')
            nxt = request.args.get('next')
            return redirect(nxt or url_for('index'))
        flash('Invalid email or password.', 'error')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))


# ─── Routes: Shop ──────────────────────────────────────────────────────────────

@app.route('/')
def index():
    featured   = Product.query.filter_by(featured=True).limit(6).all()
    categories = Category.query.all()
    return render_template('index.html', featured=featured, categories=categories)


@app.route('/products')
def products():
    q          = request.args.get('q', '')
    cat_id     = request.args.get('category', type=int)
    sort       = request.args.get('sort', 'newest')
    categories = Category.query.all()

    query = Product.query
    if q:
        query = query.filter(Product.name.ilike(f'%{q}%'))
    if cat_id:
        query = query.filter_by(category_id=cat_id)

    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort == 'name':
        query = query.order_by(Product.name.asc())
    else:
        query = query.order_by(Product.created_at.desc())

    prods = query.all()
    return render_template('products.html', products=prods,
                           categories=categories, q=q,
                           selected_cat=cat_id, sort=sort)


@app.route('/product/<int:pid>')
def product_detail(pid):
    product  = Product.query.get_or_404(pid)
    related  = Product.query.filter_by(category_id=product.category_id)\
                            .filter(Product.id != pid).limit(4).all()
    return render_template('product_detail.html', product=product, related=related)


# ─── Routes: Cart ──────────────────────────────────────────────────────────────

@app.route('/cart')
def cart():
    cart  = get_cart()
    items = []
    for pid, data in cart.items():
        product = Product.query.get(int(pid))
        if product:
            items.append({'product': product, **data})
    return render_template('cart.html', items=items)


@app.route('/cart/add/<int:pid>', methods=['POST'])
def add_to_cart(pid):
    product = Product.query.get_or_404(pid)
    qty     = int(request.form.get('qty', 1))
    cart    = get_cart()
    key     = str(pid)

    if key in cart:
        cart[key]['qty'] = min(cart[key]['qty'] + qty, product.stock)
    else:
        cart[key] = {'name': product.name, 'price': product.price,
                     'qty': min(qty, product.stock), 'image': product.image_url}
    save_cart(cart)
    flash(f'"{product.name}" added to cart.', 'success')
    return redirect(request.referrer or url_for('products'))


@app.route('/cart/update/<int:pid>', methods=['POST'])
def update_cart(pid):
    qty  = int(request.form.get('qty', 1))
    cart = get_cart()
    key  = str(pid)
    if key in cart:
        if qty <= 0:
            del cart[key]
        else:
            product      = Product.query.get(pid)
            cart[key]['qty'] = min(qty, product.stock) if product else qty
    save_cart(cart)
    return redirect(url_for('cart'))


@app.route('/cart/remove/<int:pid>')
def remove_from_cart(pid):
    cart = get_cart()
    cart.pop(str(pid), None)
    save_cart(cart)
    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart'))


@app.route('/cart/count')
def cart_count_api():
    return jsonify({'count': cart_count(), 'total': round(cart_total(), 2)})


# ─── Routes: Checkout & Orders ─────────────────────────────────────────────────

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = get_cart()
    if not cart:
        flash('Your cart is empty.', 'info')
        return redirect(url_for('cart'))

    if request.method == 'POST':
        order = Order(
            user_id = current_user.id,
            items   = json.dumps(cart),
            total   = cart_total(),
            status  = 'confirmed'
        )
        db.session.add(order)
        db.session.commit()
        save_cart({})
        flash(f'Order #{order.id} placed successfully!', 'success')
        return redirect(url_for('orders'))

    items = []
    for pid, data in cart.items():
        product = Product.query.get(int(pid))
        if product:
            items.append({'product': product, **data})
    return render_template('checkout.html', items=items)


@app.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=current_user.id)\
                             .order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=user_orders)


@app.route('/account')
@login_required
def account():
    order_count = Order.query.filter_by(user_id=current_user.id).count()
    return render_template('account.html', order_count=order_count)


# ─── Seed ──────────────────────────────────────────────────────────────────────

def seed_db():
    if Category.query.first():
        return

    cats = {}
    for name in ['Electronics', 'Clothing', 'Books', 'Home & Garden']:
        c = Category(name=name)
        db.session.add(c)
        db.session.flush()
        cats[name] = c.id

    products = [
        # Electronics
        ('Wireless Headphones', 'Premium noise-cancelling over-ear headphones with 40h battery life and studio-quality sound.', 149.99, 25, 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600', 'Electronics', True),
        ('Smart Watch Pro', 'Feature-packed smartwatch with health monitoring, GPS, and 7-day battery.', 299.99, 15, 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600', 'Electronics', True),
        ('Bluetooth Speaker', 'Waterproof portable speaker with 360° sound and 24h playtime.', 79.99, 40, 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=600', 'Electronics', False),
        ('Laptop Stand', 'Adjustable aluminium laptop stand for ergonomic desk setup.', 49.99, 60, 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600', 'Electronics', False),
        # Clothing
        ('Merino Wool Sweater', 'Luxuriously soft 100% merino wool crewneck in classic colours.', 89.99, 30, 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=600', 'Clothing', True),
        ('Slim-Fit Chinos', 'Versatile stretch chinos that go from office to weekend effortlessly.', 59.99, 50, 'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=600', 'Clothing', False),
        ('Running Shoes', 'Lightweight responsive trainers engineered for speed and comfort.', 119.99, 20, 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600', 'Clothing', True),
        # Books
        ('The Art of Clean Code', 'A practical guide to writing beautiful, maintainable software.', 34.99, 100, 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600', 'Books', False),
        ('Deep Work', 'Rules for focused success in a distracted world by Cal Newport.', 18.99, 80, 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=600', 'Books', False),
        # Home
        ('Ceramic Plant Pot Set', 'Set of 3 minimalist matte ceramic pots with bamboo trays.', 42.99, 35, 'https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=600', 'Home & Garden', True),
        ('Scented Candle Collection', 'Hand-poured soy wax candles in 4 calming fragrances.', 28.99, 55, 'https://images.unsplash.com/photo-1602523961358-f9f03dd557db?w=600', 'Home & Garden', False),
    ]

    for name, desc, price, stock, img, cat, featured in products:
        p = Product(name=name, description=desc, price=price, stock=stock,
                    image_url=img, category_id=cats[cat], featured=featured)
        db.session.add(p)

    db.session.commit()
    print("✓ Database seeded.")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_db()
    app.run(debug=True)