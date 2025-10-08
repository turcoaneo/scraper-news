import os

from flasgger import Swagger
from flask import Flask


def create_app():
    app = Flask(__name__)

    # Get absolute path to project root
    base_dir = os.path.dirname(os.path.abspath(__file__))
    swagger_path = os.path.join(base_dir, "config", "swagger.json")

    Swagger(app, template_file=swagger_path)

    from app.routes.cluster import cluster_bp
    app.register_blueprint(cluster_bp)

    return app
