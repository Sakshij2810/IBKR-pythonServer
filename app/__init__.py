# server/app/__init__.py

import sys
from app.utils.logging import LogColors  # Import LogColors for color coding

from flask import Flask, request
from flask_cors import CORS
import logging
from app.config import Config  # Import the Config class
from app.routes import order_blueprint  # Import the order blueprint
from app.utils.logging import setup_logging  # Import the custom logging setup

def create_app():
    app = Flask(__name__)

    # Load the configuration
    app.config.from_object(Config)  # Load the config

    CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "https://ibkr-client.vercel.app"]}})

    # Set up custom logging
    setup_logging()

    # Log app startup
    app.logger.info("Flask app is starting...")

    @app.before_request
    def log_request_info():
        app.logger.info(f"Request received from {request.remote_addr} at {request.url}")

    # Add a test route
    @app.route('/test', methods=['GET'])
    def test():
        app.logger.info("Test successful!")  # Log the test success message
        return "Test successful!"

    # Register the order blueprint
    app.register_blueprint(order_blueprint)

    return app
