from app.extensions import db
from app.models import Receipt
from app.services.stock_service import increase_stock

def validate_receipt_service(receipt_id):
    receipt = Receipt.query.get_or_404(receipt_id)

    if receipt.status == "Done":
        raise ValueError("Receipt already validated")

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
    return receipt
