from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.extensions import db
from app.models import Product, Category

product_bp = Blueprint("product", __name__, url_prefix="/products")

@product_bp.route("/", methods=["GET"])
@login_required
def list_products():
    products = Product.query.all()
    data = []
    for p in products:
        data.append({
            "id": p.id,
            "name": p.name,
            "sku": p.sku,
            "category": p.category.name if p.category else None,
            "unit_of_measure": p.unit_of_measure,
            "reorder_level": p.reorder_level
        })
    return jsonify(data)

@product_bp.route("/create", methods=["POST"])
@login_required
def create_product():
    data = request.get_json()

    category = None
    if data.get("category"):
        category = Category.query.filter_by(name=data["category"]).first()
        if not category:
            category = Category(name=data["category"])
            db.session.add(category)
            db.session.flush()

    product = Product(
        name=data["name"],
        sku=data["sku"],
        category_id=category.id if category else None,
        unit_of_measure=data["unit_of_measure"],
        reorder_level=data.get("reorder_level", 0)
    )
    db.session.add(product)
    db.session.commit()

    return jsonify({"message": "Product created successfully"})
