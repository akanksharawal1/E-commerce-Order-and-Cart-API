from . import db

class Cart(db.Model):
    __tablename__ = "cart"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)  
    quantity = db.Column(db.Integer, nullable=False, default=1)

    user = db.relationship("User", backref=db.backref("cart_items", lazy=True))
    product = db.relationship("Product", backref=db.backref("cart_items", lazy=True))
