from app.extensions import db
from app.models import InternalTransfer
from app.services.stock_service import decrease_stock, increase_stock

def validate_transfer_service(transfer_id):
    transfer = InternalTransfer.query.get_or_404(transfer_id)

    if transfer.status == "Done":
        raise ValueError("Transfer already validated")

    for item in transfer.items:
        decrease_stock(
            product_id=item.product_id,
            warehouse_id=transfer.from_warehouse_id,
            qty=item.quantity,
            movement_type="TRANSFER_OUT",
            reference_no=transfer.transfer_no
        )

        increase_stock(
            product_id=item.product_id,
            warehouse_id=transfer.to_warehouse_id,
            qty=item.quantity,
            movement_type="TRANSFER_IN",
            reference_no=transfer.transfer_no
        )

    transfer.status = "Done"
    db.session.commit()
    return transfer
