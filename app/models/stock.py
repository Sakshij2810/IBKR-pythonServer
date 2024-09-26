# server/app/models/stock.py

# Define a Stock model if you want to persist stock data
class Stock:
    def __init__(self, symbol, exchange, currency):
        self.symbol = symbol
        self.exchange = exchange
        self.currency = currency

