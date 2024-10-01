# server/app/services/stock_utils.py

import sys
from app.utils.logging import LogColors  # Import LogColors for color coding


import threading
import logging

# Simulated in-memory stock ownership
stock_ownership = {}

def update_ownership(stock_symbol, action, quantity, price):
    with threading.Lock():
        if action == 'BUY':
            if stock_symbol in stock_ownership:
                stock_ownership[stock_symbol]['quantity'] += quantity
                stock_ownership[stock_symbol]['bought_price'] = price
            else:
                stock_ownership[stock_symbol] = {'quantity': quantity, 'bought_price': price}
            logging.info(f"Updated ownership for {stock_symbol}: {stock_ownership[stock_symbol]}")
            
        elif action == 'SELL':
            if stock_symbol in stock_ownership:
                stock_ownership[stock_symbol]['quantity'] -= quantity
                if stock_ownership[stock_symbol]['quantity'] <= 0:
                    del stock_ownership[stock_symbol]  # Remove when fully sold
                logging.info(f"Updated ownership after sell for {stock_symbol}: {stock_ownership.get(stock_symbol, 'not owned')}")
            else:
                logging.warning(f"Attempt to sell {stock_symbol} which is not owned.")

def check_ownership(stock_symbol):
    is_owned = stock_symbol in stock_ownership and stock_ownership[stock_symbol]['quantity'] > 0
    logging.debug(f"Checking ownership for {stock_symbol}: {'Owned' if is_owned else 'Not owned'}")
    return is_owned
