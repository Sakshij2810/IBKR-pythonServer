#  server/app/services/startegies.py

# import sys
# from app.utils.logging import LogColors  # Import LogColors for color coding




# import logging
# from ib_insync import Stock, MarketOrder, LimitOrder
# from app.services.stock_utils import update_ownership
# from flask import current_app as app  # Import current_app for app context
# import asyncio

# # Helper function to qualify contracts
# async def qualify_contract(contract, ib):
#     await ib.qualifyContractsAsync(contract)

# Buy to Sell Strategy
# async def buy_to_sell_strategy(stock_symbol, exchange, currency, quantity, ib, buy_price=None, sell_percentage=0.0005):
#     contract = Stock(stock_symbol, exchange, currency)

#     with app.app_context():
#         try:
#             logging.info(f"Qualifying contract for {stock_symbol} on {exchange} with currency {currency}")
#             await qualify_contract(contract, ib)  # Use await to qualify contracts
#             logging.info(f"Contract for {stock_symbol} qualified successfully")
#         except Exception as e:
#             logging.error(f"{stock_symbol}: Failed to qualify contract: {e}")
#             return

#         try:
#             if buy_price is None:
#                 buy_order = MarketOrder('BUY', quantity)
#                 logging.info(f"Placing market buy order for {quantity} shares of {stock_symbol}")
#             else:
#                 buy_order = LimitOrder('BUY', quantity, buy_price)
#                 logging.info(f"Placing limit buy order for {quantity} shares of {stock_symbol} at {buy_price}")

#             buy_trade = ib.placeOrder(contract, buy_order)
#             logging.info(f"Buy order for {stock_symbol} placed. Waiting for it to be filled...")
#         except Exception as e:
#             logging.error(f"{stock_symbol}: Failed to place buy order: {e}")
#             return

#         while not buy_trade.isDone():
#             await asyncio.sleep(1)

#         if buy_trade.orderStatus.status == 'Filled':
#             executed_price = buy_trade.orderStatus.avgFillPrice
#             logging.info(f"{LogColors.YELLOW}Buy order filled for {quantity} shares of {stock_symbol} at {executed_price}{LogColors.RESET}")

#             # Calculate the sell price based on the executed buy price
#             sell_price = executed_price * (1 + sell_percentage)
#             logging.info(f"Placing sell order for {stock_symbol} at {sell_price} (15% higher than buy price)")

#             update_ownership(stock_symbol, 'BUY', quantity, executed_price)

#             try:
#                 sell_order = LimitOrder('SELL', quantity, sell_price)
#                 sell_trade = ib.placeOrder(contract, sell_order)
#                 logging.info(f"{LogColors.YELLOW}Sell order placed for {stock_symbol} at {sell_price}. Waiting for it to be filled...{LogColors.RESET}")
#             except Exception as e:
#                 logging.error(f"{stock_symbol}: Failed to place sell order: {e}")
#                 return

#             while not sell_trade.isDone():
#                 await asyncio.sleep(1)

#             if sell_trade.orderStatus.status == 'Filled':
#                 logging.info(f"{LogColors.YELLOW}Sell order filled for {quantity} shares of {stock_symbol} at {sell_price}{LogColors.RESET}")
#                 update_ownership(stock_symbol, 'SELL', quantity, sell_price)
#             else:
#                 logging.error(f"{stock_symbol}: Sell order was not filled.")
#         else:
#             logging.error(f"{stock_symbol}: Buy order was not filled.")


import sys
from app.utils.logging import LogColors  # Import LogColors for color coding

import logging
from ib_insync import Stock, MarketOrder, LimitOrder
from app.services.stock_utils import update_ownership
from flask import current_app as app  # Import current_app for app context
import asyncio

# Helper function to qualify contracts
async def qualify_contract(contract, ib):
    await ib.qualifyContractsAsync(contract)

# Buy to Sell Strategy
async def buy_to_sell_strategy(stock_symbol, exchange, currency, quantity, ib, buy_price=None, sell_percentage=0.0005):
    contract = Stock(stock_symbol, exchange, currency)

    with app.app_context():
        try:
            logging.info(f"Qualifying contract for {stock_symbol} on {exchange} with currency {currency}")
            await qualify_contract(contract, ib)
            logging.info(f"Contract for {stock_symbol} qualified successfully")
        except Exception as e:
            logging.error(f"{stock_symbol}: Failed to qualify contract: {e}")
            return

        try:
            if buy_price is None:
                buy_order = MarketOrder('BUY', quantity)
                logging.info(f"Placing market buy order for {quantity} shares of {stock_symbol}")
            else:
                buy_order = LimitOrder('BUY', quantity, buy_price)
                logging.info(f"Placing limit buy order for {quantity} shares of {stock_symbol} at {buy_price}")

            buy_trade = ib.placeOrder(contract, buy_order)
            logging.info(f"Buy order for {stock_symbol} placed. Waiting for the buy order to be filled...")

            # Wait for the buy order to be filled
            while not buy_trade.isDone():
                await asyncio.sleep(1)

            if buy_trade.orderStatus.status == 'Filled':
                executed_price = buy_trade.orderStatus.avgFillPrice
                logging.info(f"{LogColors.YELLOW}Buy order filled for {quantity} shares of {stock_symbol} at {executed_price}{LogColors.RESET}")
                update_ownership(stock_symbol, 'BUY', quantity, executed_price)
            else:
                logging.error(f"{stock_symbol}: Buy order was not filled. Exiting strategy.")
                return
        except Exception as e:
            logging.error(f"{stock_symbol}: Failed to place buy order: {e}")
            return

        # Calculate the sell price based on the filled buy price
        sell_price = executed_price * (1 + sell_percentage)
        logging.info(f"Sell price calculated: {sell_price}")

        # Start a 1-minute countdown before placing the sell order
        logging.info(f"Waiting 1 minute before placing sell order for {stock_symbol}...")
        for i in range(6):
            logging.info(f"{60 - i * 10} seconds remaining...")
            await asyncio.sleep(10)

        logging.info("1 minute wait completed, placing sell order now.")

        try:
            # Place sell order after waiting 1 minute
            sell_order = LimitOrder('SELL', quantity, sell_price)
            sell_trade = ib.placeOrder(contract, sell_order)
            logging.info(f"Sell order placed for {stock_symbol} at {sell_price}.")
        except Exception as e:
            logging.error(f"{stock_symbol}: Failed to place sell order: {e}")
            return

        while not sell_trade.isDone():
            await asyncio.sleep(1)

        if sell_trade.orderStatus.status == 'Filled':
            logging.info(f"{LogColors.YELLOW}Sell order filled for {quantity} shares of {stock_symbol} at {sell_price}{LogColors.RESET}")
            update_ownership(stock_symbol, 'SELL', quantity, sell_price)
        else:
            logging.error(f"{stock_symbol}: Sell order was not filled.")



# Sell to Buy Strategy
async def sell_to_buy_strategy(stock_symbol, exchange, currency, quantity, ib, sell_price=None, buy_percentage=0.15):
    contract = Stock(stock_symbol, exchange, currency)

    with app.app_context():
        try:
            await qualify_contract(contract, ib)  # Use await to qualify contracts
        except Exception as e:
            logging.error(f"Failed to qualify contract for {stock_symbol}: {e}")
            return

        try:
            sell_order = MarketOrder('SELL', quantity) if sell_price is None else LimitOrder('SELL', quantity, sell_price)
            sell_trade = ib.placeOrder(contract, sell_order)

            while not sell_trade.isDone():
                ib.sleep(1)

            if sell_trade.orderStatus.status == 'Filled':
                executed_price = sell_trade.orderStatus.avgFillPrice
                buy_price = executed_price * (1 - buy_percentage)
                logging.info(f"Sell order filled at {executed_price}. Placing buy order at {buy_price}")

                buy_order = LimitOrder('BUY', quantity, buy_price)
                buy_trade = ib.placeOrder(contract, buy_order)

                while not buy_trade.isDone():
                    ib.sleep(1)

                if buy_trade.orderStatus.status == 'Filled':
                    logging.info(f"Buy order filled at {buy_price}")
                else:
                    logging.error("Buy order was not filled.")
            else:
                logging.error("Sell order was not filled.")
        except Exception as e:
            logging.error(f"Error during sell to buy strategy for {stock_symbol}: {e}")


# Trail Buy and Sell Strategy
async def trail_buy_and_sell_strategy(stock_symbol, exchange, currency, quantity, ib, trail_percentage=0.10):
    contract = Stock(stock_symbol, exchange, currency)

    with app.app_context():
        try:
            await qualify_contract(contract, ib)  # Use await to qualify contracts
        except Exception as e:
            logging.error(f"Failed to qualify contract for {stock_symbol}: {e}")
            return

        buy_order = MarketOrder('BUY', quantity)
        buy_trade = ib.placeOrder(contract, buy_order)

        while not buy_trade.isDone():
            ib.sleep(1)

        if buy_trade.orderStatus.status == 'Filled':
            executed_price = buy_trade.orderStatus.avgFillPrice
            highest_price = executed_price
            trailing_sell_price = highest_price * (1 + trail_percentage)
            logging.info(f"Buy order filled at {executed_price}. Initial trailing sell price set at {trailing_sell_price}")

            while True:
                ib.sleep(5)
                ticker = ib.reqMktData(contract, '', False, False)
                ib.sleep(1)
                current_price = ticker.last
                ib.cancelMktData(ticker)

                if current_price is None:
                    continue

                logging.debug(f"Current price: {current_price}, Highest price: {highest_price}")

                if current_price > highest_price:
                    highest_price = current_price
                    trailing_sell_price = highest_price * (1 + trail_percentage)
                    logging.info(f"New highest price detected: {highest_price}. Adjusted trailing sell price to {trailing_sell_price}")

                if current_price <= trailing_sell_price:
                    logging.info(f"Current price {current_price} reached trailing sell price. Placing sell order at {trailing_sell_price}")
                    sell_order = MarketOrder('SELL', quantity)
                    ib.placeOrder(contract, sell_order)
                    break
        else:
            logging.error(f"Buy order for {stock_symbol} was not filled.")


# Trail Sell and Buy Back Strategy
async def trail_sell_and_buy_back_strategy(stock_symbol, exchange, currency, quantity, ib, trail_percentage=0.10):
    contract = Stock(stock_symbol, exchange, currency)

    with app.app_context():
        try:
            await qualify_contract(contract, ib)  # Use await to qualify contracts
        except Exception as e:
            logging.error(f"Failed to qualify contract for {stock_symbol}: {e}")
            return

        sell_order = MarketOrder('SELL', quantity)
        sell_trade = ib.placeOrder(contract, sell_order)

        while not sell_trade.isDone():
            ib.sleep(1)

        if sell_trade.orderStatus.status == 'Filled':
            executed_price = sell_trade.orderStatus.avgFillPrice
            lowest_price = executed_price
            trailing_buy_price = lowest_price * (1 - trail_percentage)
            logging.info(f"Sell order filled at {executed_price}. Initial trailing buy price set at {trailing_buy_price}")

            while True:
                ib.sleep(5)
                ticker = ib.reqMktData(contract, '', False, False)
                ib.sleep(1)
                current_price = ticker.last
                ib.cancelMktData(ticker)

                if current_price is None:
                    continue

                logging.debug(f"Current price: {current_price}, Lowest price: {lowest_price}")

                if current_price < lowest_price:
                    lowest_price = current_price
                    trailing_buy_price = lowest_price * (1 - trail_percentage)
                    logging.info(f"New lowest price detected: {lowest_price}. Adjusted trailing buy price to {trailing_buy_price}")

                if current_price >= trailing_buy_price:
                    logging.info(f"Current price {current_price} reached trailing buy price. Placing buy order at {trailing_buy_price}")
                    buy_order = MarketOrder('BUY', quantity)
                    ib.placeOrder(contract, buy_order)
                    break
        else:
            logging.error(f"Sell order for {stock_symbol} was not filled.")
