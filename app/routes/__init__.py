# server/app/routes/__init__.py


from flask import Blueprint

# Create a blueprint for your routes
order_blueprint = Blueprint('orders', __name__)

from .order_routes import *  # Ensure all routes are imported


