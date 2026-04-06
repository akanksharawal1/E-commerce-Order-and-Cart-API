from flask import Flask, request, jsonify
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db
from models.user import User
from models.product import Product
from models.cart import Cart
from models.order import Order
import jwt
from functools import wraps
from datetime import datetime, timedelta

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)

    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            if "Authorization" in request.headers:
                token = request.headers["Authorization"].split(" ")[1]
            if not token:
                return jsonify({"error": "Token is missing"}), 401
            try:
                data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
                current_user = db.session.get(User, data["user_id"])
            except:
                return jsonify({"error": "Token is invalid"}), 401
            return f(current_user, *args, **kwargs)
        return decorated

    def admin_required(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            if not getattr(current_user, "is_admin", False):
                return jsonify({"error": "Admin access required"}), 403
            return f(current_user, *args, **kwargs)
        return decorated

    @app.route("/")
    def home():
        return "Ecommerce API is running with DB ready"

    @app.route("/register", methods=["POST"])
    def register_user():
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        is_admin = data.get("is_admin", False)

        if not all([name, email, password]):
            return jsonify({"error": "Name, email and password are required"}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already exists"}), 400

        new_user = User(name=name, email=email, password_hash=generate_password_hash(password))
        new_user.is_admin = is_admin
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": f"User {name} registered successfully"}), 201

    @app.route("/login", methods=["POST"])
    def login_user():
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        if not all([email, password]):
            return jsonify({"error": "Email and password are required"}), 400
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid email or password"}), 401
        token = jwt.encode(
            {"user_id": user.id, "exp": datetime.utcnow() + timedelta(hours=1)},
            app.config["SECRET_KEY"],
            algorithm="HS256"
        )
        return jsonify({"message": f"Welcome back, {user.name}!", "token": token}), 200

    @app.route("/products", methods=["POST"])
    @token_required
    @admin_required
    def add_product(current_user):
        data = request.get_json()
        if not data or "name" not in data or "price" not in data or "stock" not in data:
            return jsonify({"error": "Name, price, and stock are required"}), 400
        new_product = Product(name=data["name"], price=data["price"], stock=data["stock"])
        db.session.add(new_product)
        db.session.commit()
        return jsonify({"message": f"Product {data['name']} added", "id": new_product.id}), 201

    @app.route("/products", methods=["GET"])
    def get_products():
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        paginated = Product.query.paginate(page, per_page, False)
        return jsonify([{"id": p.id, "name": p.name, "price": float(p.price), "stock": p.stock} for p in paginated.items])

    @app.route("/cart", methods=["POST"])
    @token_required
    def add_to_cart(current_user):
        data = request.get_json()
        if not data or "product_id" not in data or "quantity" not in data:
            return jsonify({"error": "product_id and quantity are required"}), 400
        product = db.session.get(Product, data["product_id"])
        if not product:
            return jsonify({"error": "Product not found"}), 404
        if product.stock < data["quantity"]:
            return jsonify({"error": "Not enough stock"}), 400
        existing_item = Cart.query.filter_by(user_id=current_user.id, product_id=product.id).first()
        if existing_item:
            existing_item.quantity += data["quantity"]
        else:
            new_item = Cart(user_id=current_user.id, product_id=product.id, quantity=data["quantity"])
            db.session.add(new_item)
        db.session.commit()
        return jsonify({"message": "Item added to cart"}), 201

    @app.route("/cart", methods=["GET"])
    @token_required
    def get_cart(current_user):
        items = Cart.query.filter_by(user_id=current_user.id).all()
        response = []
        for item in items:
            product = db.session.get(Product, item.product_id)
            response.append({
                "product": product.name,
                "quantity": item.quantity,
                "price_per_item": float(product.price),
                "total": float(product.price) * item.quantity
            })
        return jsonify(response), 200

    @app.route("/orders", methods=["POST"])
    @token_required
    def create_order(current_user):
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        if not cart_items:
            return jsonify({"error": "Cart is empty"}), 400
        for item in cart_items:
            order = Order(user_id=current_user.id, product_id=item.product_id, quantity=item.quantity)
            db.session.add(order)
            product = db.session.get(Product, item.product_id)
            product.stock -= item.quantity
            db.session.delete(item)
        db.session.commit()
        return jsonify({"message": f"Order placed successfully for user {current_user.name}"}), 201

    @app.route("/orders", methods=["GET"])
    @token_required
    def get_orders(current_user):
        orders = Order.query.filter_by(user_id=current_user.id).all()
        response = []
        for order in orders:
            product = db.session.get(Product, order.product_id)
            response.append({
                "order_id": order.id,
                "product": product.name,
                "quantity": order.quantity,
                "price_per_item": float(product.price),
                "total": float(product.price) * order.quantity
            })
        return jsonify(response), 200

    @app.route("/orders/<int:order_id>", methods=["DELETE"])
    @token_required
    def delete_order(current_user, order_id):
        order = db.session.get(Order, order_id)
        if not order or order.user_id != current_user.id:
            return jsonify({"error": "Order not found or access denied"}), 404
        db.session.delete(order)
        db.session.commit()
        return jsonify({"message": f"Order {order_id} deleted successfully"}), 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
