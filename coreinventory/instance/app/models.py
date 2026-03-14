from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager

# ---------------- USER ----------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="Inventory Manager")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------- CATEGORY ----------------
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)


# ---------------- WAREHOUSE ----------------
class Warehouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    location = db.Column(db.String(255), nullable=True)


# ---------------- PRODUCT ----------------
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    sku = db.Column(db.String(80), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)
    unit_of_measure = db.Column(db.String(50), nullable=False)
    reorder_level = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category = db.relationship("Category", backref="products")


# ---------------- STOCK PER LOCATION ----------------
class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouse.id"), nullable=False)
    quantity = db.Column(db.Float, default=0)

    product = db.relationship("Product", backref="stock_records")
    warehouse = db.relationship("Warehouse", backref="stock_records")

    __table_args__ = (
        db.UniqueConstraint("product_id", "warehouse_id", name="unique_product_warehouse"),
    )


# ---------------- RECEIPT ----------------
class Receipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receipt_no = db.Column(db.String(50), unique=True, nullable=False)
    supplier_name = db.Column(db.String(120), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouse.id"), nullable=False)
    status = db.Column(db.String(30), default="Draft")   # Draft, Waiting, Ready, Done, Canceled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    warehouse = db.relationship("Warehouse", backref="receipts")


class ReceiptItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey("receipt.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False)

    receipt = db.relationship("Receipt", backref="items")
    product = db.relationship("Product")


# ---------------- DELIVERY ----------------
class DeliveryOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    delivery_no = db.Column(db.String(50), unique=True, nullable=False)
    customer_name = db.Column(db.String(120), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouse.id"), nullable=False)
    status = db.Column(db.String(30), default="Draft")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    warehouse = db.relationship("Warehouse", backref="deliveries")


class DeliveryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    delivery_id = db.Column(db.Integer, db.ForeignKey("delivery_order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False)

    delivery = db.relationship("DeliveryOrder", backref="items")
    product = db.relationship("Product")


# ---------------- TRANSFER ----------------
class InternalTransfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transfer_no = db.Column(db.String(50), unique=True, nullable=False)
    from_warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouse.id"), nullable=False)
    to_warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouse.id"), nullable=False)
    status = db.Column(db.String(30), default="Draft")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    from_warehouse = db.relationship("Warehouse", foreign_keys=[from_warehouse_id])
    to_warehouse = db.relationship("Warehouse", foreign_keys=[to_warehouse_id])


class TransferItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transfer_id = db.Column(db.Integer, db.ForeignKey("internal_transfer.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False)

    transfer = db.relationship("InternalTransfer", backref="items")
    product = db.relationship("Product")


# ---------------- ADJUSTMENT ----------------
class StockAdjustment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    adjustment_no = db.Column(db.String(50), unique=True, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouse.id"), nullable=False)
    old_quantity = db.Column(db.Float, nullable=False)
    counted_quantity = db.Column(db.Float, nullable=False)
    difference = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product")
    warehouse = db.relationship("Warehouse")


# ---------------- LEDGER ----------------
class StockLedger(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouse.id"), nullable=False)
    movement_type = db.Column(db.String(50), nullable=False)  
    # RECEIPT / DELIVERY / TRANSFER_OUT / TRANSFER_IN / ADJUSTMENT

    reference_no = db.Column(db.String(50), nullable=False)
    quantity_change = db.Column(db.Float, nullable=False)
    balance_after = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product")
    warehouse = db.relationship("Warehouse")
