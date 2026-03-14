from flask import Blueprint, jsonify
from flask_login import login_required
from app.models import StockLedger

ledger_bp = Blueprint("ledger", __name__, url_prefix="/ledger")

@ledger_bp.route("/")
@login_required
def list_ledger():
    entries = StockLedger.query.order_by(StockLedger.created_at.desc()).all()

    return jsonify([
        {
            "product": entry.product.name,
            "warehouse": entry.warehouse.name,
            "movement_type": entry.movement_type,
            "reference_no": entry.reference_no,
            "quantity_change": entry.quantity_change,
            "balance_after": entry.balance_after,
            "created_at": entry.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for entry in entries
    ])
