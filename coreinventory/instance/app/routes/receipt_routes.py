from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.extensions import db
from app.models import Receipt, ReceiptItem
from app.utils import generate_doc_no
from app.services.stock_service import increase_stock

receipt_bp = Blueprint("receipt", __name__, url_prefix="/receipts")

@receipt_bp.route("/create", methods=["POST"])
@login_required
def create_receipt():
    data = request.get_json()

    receipt = Receipt(
        receipt_no=generate_doc_no("REC"),
        supplier_name=data["supplier_name"],
        warehouse_id=data["warehouse_id"],
        status="Draft"
    )
    db.session.add(receipt)
    db.session.flush()

    for item in data["items"]:
        receipt_item = ReceiptItem(
            receipt_id=receipt.id,
            product_id=item["product_id"],
            quantity=item["quantity"]
        )
        db.session.add(receipt_item)

    db.session.commit()
    return jsonify({"message": "Receipt created", "receipt_no": receipt.receipt_no})


@receipt_bp.route("/validate/<int:receipt_id>", methods=["POST"])
@login_required
def validate_receipt(receipt_id):
    receipt = Receipt.query.get_or_404(receipt_id)

    if receipt.status == "Done":
        return jsonify({"message": "Receipt already validated"}), 400

    for item in receipt.items:
        increase_stock(
            product_id=item.product_id,
            warehouse_id=receipt.warehouse_id,
            qty=item.quantity,
            movement_type="RECEIPT",
            reference_no=receipt.receipt_no
        )

    receipt.status = "Done"
    db.session.commit()

    return jsonify({"message": "Receipt validated. Stock increased."})
