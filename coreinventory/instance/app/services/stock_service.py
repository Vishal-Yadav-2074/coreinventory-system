from app.extensions import db
from app.models import Stock, StockLedger

def get_or_create_stock(product_id, warehouse_id):
    stock = Stock.query.filter_by(product_id=product_id, warehouse_id=warehouse_id).first()
    if not stock:
        stock = Stock(product_id=product_id, warehouse_id=warehouse_id, quantity=0)
        db.session.add(stock)
        db.session.flush()
    return stock

def increase_stock(product_id, warehouse_id, qty, movement_type, reference_no):
    stock = get_or_create_stock(product_id, warehouse_id)
    stock.quantity += qty

    ledger = StockLedger(
        product_id=product_id,
        warehouse_id=warehouse_id,
        movement_type=movement_type,
        reference_no=reference_no,
        quantity_change=qty,
        balance_after=stock.quantity
    )
    db.session.add(ledger)

def decrease_stock(product_id, warehouse_id, qty, movement_type, reference_no):
    stock = get_or_create_stock(product_id, warehouse_id)

    if stock.quantity < qty:
        raise ValueError("Insufficient stock")

    stock.quantity -= qty

    ledger = StockLedger(
        product_id=product_id,
        warehouse_id=warehouse_id,
        movement_type=movement_type,
        reference_no=reference_no,
        quantity_change=-qty,
        balance_after=stock.quantity
    )
    db.session.add(ledger)

def set_stock(product_id, warehouse_id, new_qty, movement_type, reference_no):
    stock = get_or_create_stock(product_id, warehouse_id)
    diff = new_qty - stock.quantity
    stock.quantity = new_qty

    ledger = StockLedger(
        product_id=product_id,
        warehouse_id=warehouse_id,
        movement_type=movement_type,
        reference_no=reference_no,
        quantity_change=diff,
        balance_after=stock.quantity
    )
    db.session.add(ledger)

    return diff
