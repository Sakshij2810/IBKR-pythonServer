# # server/app/services/stock_service.py

import sys
from app.utils.logging import LogColors  # Import LogColors for color coding
import logging
from ib_insync import Stock, MarketOrder, LimitOrder
from app.services.stock_utils import update_ownership
from app.services.strategies import (
    buy_to_sell_strategy,
    sell_to_buy_strategy,
    trail_buy_and_sell_strategy,
    trail_sell_and_buy_back_strategy,
)
from flask import current_app as app  # Import current_app for app context
import asyncio


async def place_order(data, ib):
    strategy = data['strategy']
    
    # Dispatch to the appropriate strategy function
    if strategy == 'buyToSell':
        return await place_order_buy_to_sell_strategy(data, ib)
    elif strategy == 'sellToBuy':
        return await place_order_sell_to_buy_strategy(data, ib)
    elif strategy == 'trailBuyAndSell':
        return await place_order_trail_buy_and_sell_strategy(data, ib)
    elif strategy == 'trailSellAndBuyBack':
        return await place_order_trail_sell_and_buy_back_strategy(data, ib)
    else:
        logging.error(f"Unknown strategy: {strategy}")
        return {'status': 'error', 'message': f'Unknown strategy: {strategy}'}, 400


async def place_order_buy_to_sell_strategy(data, ib):
    stock_symbol = data['stockSymbol']
    exchange = data['exchange']
    currency = data['currency']
    quantity = data['quantity']
    
    try:
        logging.info(f"{LogColors.YELLOW}Placing buy order for {stock_symbol}{LogColors.RESET}")
        await buy_to_sell_strategy(stock_symbol, exchange, currency, quantity, ib)
        return {'status': 'success', 'message': f'Buy to sell order placed for {stock_symbol}'}, 200
    except Exception as e:
        logging.error(f"Error in buy to sell strategy for {stock_symbol}: {e}")
        return {'status': 'error', 'message': str(e)}, 500


async def place_order_sell_to_buy_strategy(data, ib):
    stock_symbol = data['stockSymbol']
    exchange = data['exchange']
    currency = data['currency']
    quantity = data['quantity']
    
    try:
        logging.info(f"{LogColors.YELLOW}Placing sell order for {stock_symbol}{LogColors.RESET}")
        await sell_to_buy_strategy(stock_symbol, exchange, currency, quantity, ib)
        return {'status': 'success', 'message': f'Sell to buy order placed for {stock_symbol}'}, 200
    except Exception as e:
        logging.error(f"Error in sell to buy strategy for {stock_symbol}: {e}")
        return {'status': 'error', 'message': str(e)}, 500


async def place_order_trail_buy_and_sell_strategy(data, ib):
    stock_symbol = data['stockSymbol']
    exchange = data['exchange']
    currency = data['currency']
    quantity = data['quantity']
    trail_percentage = data.get('trailPercentage', 0.1)
    
    try:
        logging.info(f"{LogColors.YELLOW}Placing trailing buy and sell order for {stock_symbol}{LogColors.RESET}")
        await trail_buy_and_sell_strategy(stock_symbol, exchange, currency, quantity, ib, trail_percentage)
        return {'status': 'success', 'message': f'Trail buy and sell order placed for {stock_symbol}'}, 200
    except Exception as e:
        logging.error(f"Error in trail buy and sell strategy for {stock_symbol}: {e}")
        return {'status': 'error', 'message': str(e)}, 500


async def place_order_trail_sell_and_buy_back_strategy(data, ib):
    stock_symbol = data['stockSymbol']
    exchange = data['exchange']
    currency = data['currency']
    quantity = data['quantity']
    trail_percentage = data.get('trailPercentage', 0.1)
    
    try:
        logging.info(f"{LogColors.YELLOW}Placing trailing sell and buy back order for {stock_symbol}{LogColors.RESET}")
        await trail_sell_and_buy_back_strategy(stock_symbol, exchange, currency, quantity, ib, trail_percentage)
        return {'status': 'success', 'message': f'Trail sell and buy back order placed for {stock_symbol}'}, 200
    except Exception as e:
        logging.error(f"Error in trail sell and buy back strategy for {stock_symbol}: {e}")
        return {'status': 'error', 'message': str(e)}, 500
