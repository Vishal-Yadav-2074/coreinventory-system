from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.extensions import db
from app.models import InternalTransfer, TransferItem
from app.utils import generate_doc_no
from app.services.stock_service import decrease_stock, increase_stock

transfer_bp = Blueprint("transfer", __name__, url_prefix="/transfers")

@transfer_bp.route("/create", methods=["POST"])
@login_required
def create_transfer():
    data = request.get_json()

    transfer = InternalTransfer(
        transfer_no=generate_doc_no("TRF"),
        from_warehouse_id=data["from_warehouse_id"],
        to_warehouse_id=data["to_warehouse_id"],
        status="Draft"
    )
    db.session.add(transfer)
    db.session.flush()

    for item in data["items"]:
        db.session.add(TransferItem(
            transfer_id=transfer.id,
            product_id=item["product_id"],
            quantity=item["quantity"]
        ))

    db.session.commit()
    return jsonify({"message": "Transfer created", "transfer_no": transfer.transfer_no})


@transfer_bp.route("/validate/<int:transfer_id>", methods=["POST"])
@login_required
def validate_transfer(transfer_id):
    transfer = InternalTransfer.query.get_or_404(transfer_id)

    if transfer.status == "Done":
        return jsonify({"message": "Transfer already validated"}), 400

    try:
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
        return jsonify({"message": "Transfer validated successfully"})

    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
