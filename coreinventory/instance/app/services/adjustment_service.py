from app.extensions import db
from app.models import Stock, StockAdjustment
from app.services.stock_service import set_stock
from app.utils import generate_doc_no

def create_adjustment_service(product_id, warehouse_id, counted_quantity, reason=""):
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
    return adjustment
