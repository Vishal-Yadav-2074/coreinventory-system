from app.extensions import db
from app.models import DeliveryOrder
from app.services.stock_service import decrease_stock

def validate_delivery_service(delivery_id):
    delivery = DeliveryOrder.query.get_or_404(delivery_id)

    if delivery.status == "Done":
        raise ValueError("Delivery already validated")

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
    return delivery
