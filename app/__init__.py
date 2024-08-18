from flask import Flask, jsonify
from .routes import main_bp

def create_app():
    app = Flask(__name__)
    app.config['DATABASE'] = 'file_index.db'

    with app.app_context():
        from .models import init_db
        init_db()

    app.register_blueprint(main_bp)

    return app
