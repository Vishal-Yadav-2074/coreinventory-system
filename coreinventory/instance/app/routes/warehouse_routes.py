from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.extensions import db
from app.models import Warehouse

warehouse_bp = Blueprint("warehouse", __name__, url_prefix="/warehouses")

@warehouse_bp.route("/", methods=["GET"])
@login_required
def list_warehouses():
    warehouses = Warehouse.query.all()
    return jsonify([
        {
            "id": w.id,
            "name": w.name,
            "code": w.code,
            "location": w.location
        }
        for w in warehouses
    ])

@warehouse_bp.route("/create", methods=["POST"])
@login_required
def create_warehouse():
    data = request.get_json()

    warehouse = Warehouse(
        name=data["name"],
        code=data["code"],
        location=data.get("location")
    )
    db.session.add(warehouse)
    db.session.commit()

    return jsonify({"message": "Warehouse created successfully"})
