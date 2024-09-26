# server/app/routes/order_routes.py

import sys
from app.utils.logging import LogColors  # Import LogColors for color coding

from flask import request, jsonify, current_app as app
from app.services.stock_service import place_order
from app.routes import order_blueprint
from ib_insync import IB
import logging

# Initialize the IB instance here
ib = IB()

@order_blueprint.route('/api/order', methods=['POST'])
async def order_stock():
    app.logger.debug("Received request for /api/order")
    data = request.json

    # Validate incoming data
    required_fields = ['stockSymbol', 'exchange', 'currency', 'quantity', 'orderType', 'action', 'strategy']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        app.logger.warning(f"Missing fields: {', '.join(missing_fields)}")
        return jsonify({'status': 'error', 'message': f"Missing fields: {', '.join(missing_fields)}"}), 400

    try:
        # Connect to the IB API
        await ib.connectAsync('127.0.0.1', 7496, clientId=5)  
        
        response = await place_order(data, ib)
        
        # Handle response based on its type (dict or tuple)
        if isinstance(response, tuple):
            status_code, message = response
            return jsonify({'status': status_code, 'message': message}), status_code
        else:
            return jsonify(response), response.get('status', 200)

    except Exception as e:
        app.logger.error(f"Unexpected error during order processing: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
