from flask import Flask
from config import Config
from app.extensions import db, login_manager, migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "auth.login"

    from app.routes.auth_routes import auth_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.product_routes import product_bp
    from app.routes.warehouse_routes import warehouse_bp
    from app.routes.receipt_routes import receipt_bp
    from app.routes.delivery_routes import delivery_bp
    from app.routes.transfer_routes import transfer_bp
    from app.routes.adjustment_routes import adjustment_bp
    from app.routes.ledger_routes import ledger_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(warehouse_bp)
    app.register_blueprint(receipt_bp)
    app.register_blueprint(delivery_bp)
    app.register_blueprint(transfer_bp)
    app.register_blueprint(adjustment_bp)
    app.register_blueprint(ledger_bp)

    return app
