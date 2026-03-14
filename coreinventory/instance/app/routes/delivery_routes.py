from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.extensions import db
from app.models import DeliveryOrder, DeliveryItem
from app.utils import generate_doc_no
from app.services.stock_service import decrease_stock

delivery_bp = Blueprint("delivery", __name__, url_prefix="/deliveries")

@delivery_bp.route("/create", methods=["POST"])
@login_required
def create_delivery():
    data = request.get_json()

    delivery = DeliveryOrder(
        delivery_no=generate_doc_no("DEL"),
        customer_name=data["customer_name"],
        warehouse_id=data["warehouse_id"],
        status="Draft"
    )
    db.session.add(delivery)
    db.session.flush()

    for item in data["items"]:
        db.session.add(DeliveryItem(
            delivery_id=delivery.id,
            product_id=item["product_id"],
            quantity=item["quantity"]
        ))

    db.session.commit()
    return jsonify({"message": "Delivery created", "delivery_no": delivery.delivery_no})


@delivery_bp.route("/validate/<int:delivery_id>", methods=["POST"])
@login_required
def validate_delivery(delivery_id):
    delivery = DeliveryOrder.query.get_or_404(delivery_id)

    if delivery.status == "Done":
        return jsonify({"message": "Delivery already validated"}), 400

    try:
        for item in delivery.items:
            decrease_stock(
                product_id=item.product_id,
                warehouse_id=delivery.warehouse_id,
                qty=item.quantity,
                movement_type="DELIVERY",
                reference_no=delivery.delivery_no
            )
        delivery.status = "Done"
        db.session.commit()
        return jsonify({"message": "Delivery validated. Stock decreased."})

    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
