# server/app/services/stock_service.py

import sys
from app.utils.logging import LogColors  # Import LogColors for color coding

# import logging
# from ib_insync import Stock, MarketOrder, LimitOrder
# from app.services.stock_utils import update_ownership, check_ownership
# from app.services.strategies import buy_to_sell_strategy, sell_to_buy_strategy

# async def place_order(data, ib):
#     stock_symbol = data['stockSymbol']
#     exchange = data['exchange']
#     currency = data['currency']
#     quantity = data['quantity']
#     order_type = data['orderType']
#     action = data['action']
#     strategy = data['strategy']

#     try:
#         # Check ownership before SELL
#         if action == 'SELL' and  check_ownership(stock_symbol):
#             logging.error(f"Cannot sell {stock_symbol}, no prior buy order detected.")
#             return {'status': 'error', 'message': 'You cannot sell a stock you do not own.'}, 400

#         # Ensure that stocks aren't bought again if already owned
#         if action == 'BUY' and check_ownership(stock_symbol):
#             logging.error(f"{stock_symbol} already owned, cannot buy again in this strategy.")
#             return {'status': 'error', 'message': f'{stock_symbol} is already owned. Cannot place buy order.'}, 400

#         # Process strategy based on action
#         if action == 'BUY':
#             if strategy == 'buyToSell':
#                 logging.info(f"Placing buy order for {stock_symbol}")
#                 await buy_to_sell_strategy(stock_symbol, exchange, currency, quantity, ib)
#             else:
#                 logging.error("Invalid strategy provided for buy action.")
#                 return {'status': 'error', 'message': 'Invalid strategy provided.'}, 400
#         elif action == 'SELL':
#             if strategy == 'sellToBuy':
#                 logging.info(f"Placing sell order for {stock_symbol}")
#                 await sell_to_buy_strategy(stock_symbol, exchange, currency, quantity, ib)
#             else:
#                 logging.error("Invalid strategy provided for sell action.")
#                 return {'status': 'error', 'message': 'Invalid strategy provided.'}, 400
#         else:
#             logging.error("Invalid action provided.")
#             return {'status': 'error', 'message': 'Invalid action provided.'}, 400

#         return {'status': 'success', 'message': f'Strategy {strategy} initiated for {action}.'}, 200
#     except Exception as e:
#         logging.error(f"Error in place_order for {stock_symbol}: {e}", exc_info=True)
#         return {'status': 'error', 'message': 'Internal error processing order'}, 500

import logging
from ib_insync import Stock, MarketOrder, LimitOrder
from app.services.stock_utils import update_ownership, check_ownership
from app.services.strategies import buy_to_sell_strategy
from flask import current_app as app  # Import current_app for app context
import asyncio

# Buy to Sell Strategy
async def place_order(data, ib):
    stock_symbol = data['stockSymbol']
    exchange = data['exchange']
    currency = data['currency']
    quantity = data['quantity']
    order_type = data['orderType']
    action = data['action']
    strategy = data['strategy']

    try:
        # Check ownership before SELL
        if action == 'SELL' and check_ownership(stock_symbol):
            logging.error(f"Cannot sell {stock_symbol}, no prior buy order detected.")
            return {'status': 'error', 'message': 'You cannot sell a stock you do not own.'}, 400

        # Ensure that stocks aren't bought again if already owned
        if action == 'BUY' and check_ownership(stock_symbol):
            logging.error(f"{stock_symbol} already owned, cannot buy again in this strategy.")
            return {'status': 'error', 'message': f'{stock_symbol} is already owned. Cannot place buy order.'}, 400

        # Process strategy based on action
        if action == 'BUY':
            if strategy == 'buyToSell':
                logging.info(f"Placing buy order for {stock_symbol}")
                await buy_to_sell_strategy(stock_symbol, exchange, currency, quantity, ib)
            else:
                logging.error(f"Unknown strategy: {strategy}")
                return {'status': 'error', 'message': 'Unknown strategy.'}, 400

    except Exception as e:
        logging.error(f"Error in place_order for {stock_symbol}: {e}")
        return {'status': 'error', 'message': str(e)}, 500
