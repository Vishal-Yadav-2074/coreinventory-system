from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.extensions import db
from app.models import StockAdjustment, Stock
from app.utils import generate_doc_no
from app.services.stock_service import set_stock

adjustment_bp = Blueprint("adjustment", __name__, url_prefix="/adjustments")

@adjustment_bp.route("/create", methods=["POST"])
@login_required
def create_adjustment():
    data = request.get_json()

    product_id = data["product_id"]
    warehouse_id = data["warehouse_id"]
    counted_quantity = float(data["counted_quantity"])
    reason = data.get("reason", "")

    stock = Stock.query.filter_by(product_id=product_id, warehouse_id=warehouse_id).first()
    old_quantity = stock.quantity if stock else 0

    adjustment_no = generate_doc_no("ADJ")
    difference = counted_quantity - old_quantity

    adjustment = StockAdjustment(
        adjustment_no=adjustment_no,
        product_id=product_id,
        warehouse_id=warehouse_id,
        old_quantity=old_quantity,
        counted_quantity=counted_quantity,
        difference=difference,
        reason=reason
    )
    db.session.add(adjustment)

    set_stock(
        product_id=product_id,
        warehouse_id=warehouse_id,
        new_qty=counted_quantity,
        movement_type="ADJUSTMENT",
        reference_no=adjustment_no
    )

    db.session.commit()
    return jsonify({"message": "Stock adjusted successfully", "adjustment_no": adjustment_no})
