from flask import Blueprint, jsonify, request
from flask_login import login_required
from sqlalchemy import func
from app.models import Product, Stock, Receipt, DeliveryOrder, InternalTransfer

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@dashboard_bp.route("/")
@login_required
def dashboard():
    total_products_in_stock = func.coalesce(func.sum(Stock.quantity), 0)
    total_stock = Stock.query.with_entities(total_products_in_stock).scalar()

    low_stock_items = (
        Stock.query.join(Product, Stock.product_id == Product.id)
        .filter(Stock.quantity <= Product.reorder_level, Stock.quantity > 0)
        .count()
    )

    out_of_stock_items = Stock.query.filter(Stock.quantity <= 0).count()

    pending_receipts = Receipt.query.filter(Receipt.status.in_(["Draft", "Waiting", "Ready"])).count()
    pending_deliveries = DeliveryOrder.query.filter(DeliveryOrder.status.in_(["Draft", "Waiting", "Ready"])).count()
    scheduled_transfers = InternalTransfer.query.filter(InternalTransfer.status.in_(["Draft", "Waiting", "Ready"])).count()

    return jsonify({
        "total_products_in_stock": total_stock,
        "low_stock_items": low_stock_items,
        "out_of_stock_items": out_of_stock_items,
        "pending_receipts": pending_receipts,
        "pending_deliveries": pending_deliveries,
        "scheduled_transfers": scheduled_transfers
    })
