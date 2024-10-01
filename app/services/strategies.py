#server/app/services/strategies.py

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
async def buy_to_sell_strategy(stock_symbol, exchange, currency, quantity, ib, buy_price=None, sell_percentage=0.15):
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
                buy_price = round(buy_price, 2)  # Round buy price to 2 decimal places
                buy_order = LimitOrder('BUY', quantity, buy_price)
                logging.info(f"Placing limit buy order for {quantity} shares of {stock_symbol} at {buy_price}")

            buy_trade = ib.placeOrder(contract, buy_order)
            logging.info(f"{LogColors.YELLOW}Buy order for {stock_symbol} placed. Waiting for the buy order to be filled...{LogColors.RESET}")

            # Wait for the buy order to be filled
            while not buy_trade.isDone():
                await asyncio.sleep(1)

            if buy_trade.orderStatus.status == 'Filled':
                executed_price = round(buy_trade.orderStatus.avgFillPrice, 2)  # Round executed price to 2 decimal places
                logging.info(f"{LogColors.YELLOW}Buy order filled for {quantity} shares of {stock_symbol} at {executed_price}{LogColors.RESET}")
                update_ownership(stock_symbol, 'BUY', quantity, executed_price)
            else:
                logging.error(f"{stock_symbol}: Buy order was not filled. Exiting strategy.")
                return
        except Exception as e:
            logging.error(f"{stock_symbol}: Failed to place buy order: {e}")
            return

        # Calculate the sell price based on the filled buy price
        sell_price = round(executed_price * (1 + sell_percentage), 2)  # Round sell price to 2 decimal places
        logging.info(f"{LogColors.YELLOW}Sell price calculated: {sell_price}{LogColors.RESET}")

        # Start a 1-minute countdown before placing the sell order
        logging.info(f"{LogColors.YELLOW}Waiting 1 minute before placing sell order for {stock_symbol}...{LogColors.RESET}")
        for i in range(6):
            logging.info(f"{60 - i * 10} seconds remaining...")
            await asyncio.sleep(10)

        logging.info(f"{LogColors.YELLOW}1 minute wait completed, placing sell order now.{LogColors.RESET}")

        try:
            # Place sell order after waiting 1 minute
            sell_order = LimitOrder('SELL', quantity, sell_price)
            sell_trade = ib.placeOrder(contract, sell_order)
            logging.info(f"{LogColors.YELLOW}Sell order placed for {stock_symbol} at {sell_price}.{LogColors.RESET}")
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
            if sell_price is None:
                sell_order = MarketOrder('SELL', quantity)
            else:
                sell_price = round(sell_price, 2)  # Round sell price to 2 decimal places
                sell_order = LimitOrder('SELL', quantity, sell_price)

            logging.info(f"Placing sell order for {stock_symbol}")
            sell_trade = ib.placeOrder(contract, sell_order)

            while not sell_trade.isDone():
                await asyncio.sleep(1)

            if sell_trade.orderStatus.status == 'Filled':
                executed_price = round(sell_trade.orderStatus.avgFillPrice, 2)  # Round executed price to 2 decimal places
                buy_price = round(executed_price * (1 - buy_percentage), 2)  # Round buy price to 2 decimal places
                logging.info(f"{LogColors.YELLOW}Sell order filled at {executed_price}. Buy order will be placed at {buy_price} after 1 minute.{LogColors.RESET}")

                # Start a 1-minute countdown before placing the buy order
                logging.info(f"{LogColors.YELLOW}Waiting 1 minute before placing buy order for {stock_symbol}...{LogColors.RESET}")
                for i in range(6):
                    logging.info(f"{60 - i * 10} seconds remaining...")
                    await asyncio.sleep(10)

                logging.info(f"{LogColors.YELLOW}1 minute wait completed, placing buy order now.{LogColors.RESET}")

                try:
                    logging.info(f"{LogColors.YELLOW}Placing buy order at {buy_price}{LogColors.RESET}")
                    buy_order = LimitOrder('BUY', quantity, buy_price)
                    buy_trade = ib.placeOrder(contract, buy_order)

                    while not buy_trade.isDone():
                        await asyncio.sleep(1)

                    if buy_trade.orderStatus.status == 'Filled':
                        logging.info(f"{LogColors.YELLOW}Buy order filled at {buy_price}{LogColors.RESET}")
                        update_ownership(stock_symbol, 'BUY', quantity, buy_price)
                    else:
                        logging.error("Buy order was not filled.")
                except Exception as e:
                    logging.error(f"{stock_symbol}: Failed to place buy order: {e}")
            else:
                logging.error("Sell order was not filled.")
        except Exception as e:
            logging.error(f"Error during sell to buy strategy for {stock_symbol}: {e}")


# # Trail Buy and Sell Strategy
# async def trail_buy_and_sell_strategy(stock_symbol, exchange, currency, quantity, ib, trail_percentage=0.10):
#     contract = Stock(stock_symbol, exchange, currency)

#     with app.app_context():
#         try:
#             await qualify_contract(contract, ib)  # Use await to qualify contracts
#         except Exception as e:
#             logging.error(f"Failed to qualify contract for {stock_symbol}: {e}")
#             return

#         buy_order = MarketOrder('BUY', quantity)
#         buy_trade = ib.placeOrder(contract, buy_order)

#         while not buy_trade.isDone():
#             ib.sleep(1)

#         if buy_trade.orderStatus.status == 'Filled':
#             executed_price = round(buy_trade.orderStatus.avgFillPrice, 2)  # Round executed price to 2 decimal places
#             highest_price = executed_price
#             trailing_sell_price = round(highest_price * (1 + trail_percentage), 2)  # Round trailing sell price to 2 decimal places
#             logging.info(f"{LogColors.YELLOW}Buy order filled at {executed_price}. Initial trailing sell price set at {trailing_sell_price}{LogColors.RESET}")

#             while True:
#                 ib.sleep(5)
#                 ticker = ib.reqMktData(contract, '', False, False)
#                 ib.sleep(1)
#                 current_price = ticker.last
#                 ib.cancelMktData(ticker)

#                 if current_price is None:
#                     continue

#                 logging.debug(f"{LogColors.YELLOW}Current price: {current_price}, Highest price: {highest_price}{LogColors.RESET}")

#                 if current_price > highest_price:
#                     highest_price = current_price
#                     trailing_sell_price = round(highest_price * (1 + trail_percentage), 2)  # Round trailing sell price to 2 decimal places
#                     logging.info(f"{LogColors.YELLOW}New highest price detected: {highest_price}. Adjusted trailing sell price to {trailing_sell_price}{LogColors.RESET}")

#                 if current_price <= trailing_sell_price:
#                     logging.info(f"{LogColors.YELLOW}Current price {current_price} reached trailing sell price. Placing sell order at {trailing_sell_price}{LogColors.RESET}")
#                     sell_order = MarketOrder('SELL', quantity)
#                     ib.placeOrder(contract, sell_order)
#                     break
#         else:
#             logging.error(f"Buy order for {stock_symbol} was not filled.")


# # Trail Sell and Buy Back Strategy
# async def trail_sell_and_buy_back_strategy(stock_symbol, exchange, currency, quantity, ib, trail_percentage=0.10):
#     contract = Stock(stock_symbol, exchange, currency)

#     with app.app_context():
#         try:
#             await qualify_contract(contract, ib)  # Use await to qualify contracts
#         except Exception as e:
#             logging.error(f"Failed to qualify contract for {stock_symbol}: {e}")
#             return

#         sell_order = MarketOrder('SELL', quantity)
#         sell_trade = ib.placeOrder(contract, sell_order)

#         while not sell_trade.isDone():
#             ib.sleep(1)

#         if sell_trade.orderStatus.status == 'Filled':
#             executed_price = round(sell_trade.orderStatus.avgFillPrice, 2)  # Round executed price to 2 decimal places
#             lowest_price = executed_price
#             trailing_buy_price = round(lowest_price * (1 - trail_percentage), 2)  # Round trailing buy price to 2 decimal places
#             logging.info(f"{LogColors.YELLOW}Sell order filled at {executed_price}. Initial trailing buy price set at {trailing_buy_price}{LogColors.RESET}")

#             while True:
#                 ib.sleep(5)
#                 ticker = ib.reqMktData(contract, '', False, False)
#                 ib.sleep(1)
#                 current_price = ticker.last
#                 ib.cancelMktData(ticker)

#                 if current_price is None:
#                     continue

#                 logging.debug(f"{LogColors.YELLOW}Current price: {current_price}, Lowest price: {lowest_price}{LogColors.RESET}")

#                 if current_price < lowest_price:
#                     lowest_price = current_price
#                     trailing_buy_price = round(lowest_price * (1 - trail_percentage), 2)  # Round trailing buy price to 2 decimal places
#                     logging.info(f"{LogColors.YELLOW}New lowest price detected: {lowest_price}. Adjusted trailing buy price to {trailing_buy_price}{LogColors.RESET}")

#                 if current_price >= trailing_buy_price:
#                     logging.info(f"{LogColors.YELLOW}Current price {current_price} reached trailing buy price. Placing buy order at {trailing_buy_price}{LogColors.RESET}")
#                     buy_order = MarketOrder('BUY', quantity)
#                     ib.placeOrder(contract, buy_order)
#                     break
#         else:
#             logging.error(f"Sell order for {stock_symbol} was not filled.")


# Trail Buy and Sell Strategy
async def trail_buy_and_sell_strategy(stock_symbol, exchange, currency, quantity, ib, trail_percentage=0.10):
    contract = Stock(stock_symbol, exchange, currency)

    with app.app_context():
        try:
            logging.info(f"Qualifying contract for {stock_symbol}")
            await qualify_contract(contract, ib)
            logging.info(f"Contract for {stock_symbol} qualified successfully")
        except Exception as e:
            logging.error(f"Failed to qualify contract for {stock_symbol}: {e}")
            return

        try:
            logging.info(f"Placing market buy order for {stock_symbol}")
            buy_order = MarketOrder('BUY', quantity)
            buy_trade = ib.placeOrder(contract, buy_order)

            # Wait for the buy order to be filled
            while not buy_trade.isDone():
                await asyncio.sleep(1)

            if buy_trade.orderStatus.status == 'Filled':
                executed_price = round(buy_trade.orderStatus.avgFillPrice, 2)
                highest_price = executed_price
                trailing_sell_price = round(highest_price * (1 + trail_percentage), 2)
                logging.info(f"{LogColors.YELLOW}Buy order filled at {executed_price}. Initial trailing sell price set at {trailing_sell_price}{LogColors.RESET}")

                while True:
                    await asyncio.sleep(5)
                    ticker = ib.reqMktData(contract, '', False, False)
                    await asyncio.sleep(1)
                    current_price = ticker.last
                    ib.cancelMktData(contract)

                    if current_price is None:
                        continue

                    logging.debug(f"{LogColors.YELLOW}Current price: {current_price}, Highest price: {highest_price}{LogColors.RESET}")

                    if current_price > highest_price:
                        highest_price = current_price
                        trailing_sell_price = round(highest_price * (1 + trail_percentage), 2)
                        logging.info(f"{LogColors.YELLOW}New highest price detected: {highest_price}. Adjusted trailing sell price to {trailing_sell_price}{LogColors.RESET}")

                    if current_price <= trailing_sell_price:
                        logging.info(f"{LogColors.YELLOW}Current price {current_price} reached trailing sell price. Placing sell order at {trailing_sell_price}{LogColors.RESET}")
                        sell_order = MarketOrder('SELL', quantity)
                        ib.placeOrder(contract, sell_order)
                        break
            else:
                logging.error(f"Buy order for {stock_symbol} was not filled.")
        except Exception as e:
            logging.error(f"Failed to place buy order for {stock_symbol}: {e}")


# Trail Sell and Buy Back Strategy
async def trail_sell_and_buy_back_strategy(stock_symbol, exchange, currency, quantity, ib, trail_percentage=0.10):
    contract = Stock(stock_symbol, exchange, currency)

    with app.app_context():
        try:
            logging.info(f"Qualifying contract for {stock_symbol}")
            await qualify_contract(contract, ib)
            logging.info(f"Contract for {stock_symbol} qualified successfully")
        except Exception as e:
            logging.error(f"Failed to qualify contract for {stock_symbol}: {e}")
            return

        try:
            logging.info(f"Placing market sell order for {stock_symbol}")
            sell_order = MarketOrder('SELL', quantity)
            sell_trade = ib.placeOrder(contract, sell_order)

            # Wait for the sell order to be filled
            while not sell_trade.isDone():
                await asyncio.sleep(1)

            if sell_trade.orderStatus.status == 'Filled':
                executed_price = round(sell_trade.orderStatus.avgFillPrice, 2)
                lowest_price = executed_price
                trailing_buy_price = round(lowest_price * (1 - trail_percentage), 2)
                logging.info(f"{LogColors.YELLOW}Sell order filled at {executed_price}. Initial trailing buy price set at {trailing_buy_price}{LogColors.RESET}")

                while True:
                    await asyncio.sleep(5)
                    ticker = ib.reqMktData(contract, '', False, False)
                    await asyncio.sleep(1)
                    current_price = ticker.last
                    ib.cancelMktData(contract)

                    if current_price is None:
                        continue

                    logging.debug(f"{LogColors.YELLOW}Current price: {current_price}, Lowest price: {lowest_price}{LogColors.RESET}")

                    if current_price < lowest_price:
                        lowest_price = current_price
                        trailing_buy_price = round(lowest_price * (1 - trail_percentage), 2)
                        logging.info(f"{LogColors.YELLOW}New lowest price detected: {lowest_price}. Adjusted trailing buy price to {trailing_buy_price}{LogColors.RESET}")

                    if current_price >= trailing_buy_price:
                        logging.info(f"{LogColors.YELLOW}Current price {current_price} reached trailing buy price. Placing buy order at {trailing_buy_price}{LogColors.RESET}")
                        buy_order = MarketOrder('BUY', quantity)
                        ib.placeOrder(contract, buy_order)
                        break
            else:
                logging.error(f"Sell order for {stock_symbol} was not filled.")
        except Exception as e:
            logging.error(f"Failed to place sell order for {stock_symbol}: {e}")