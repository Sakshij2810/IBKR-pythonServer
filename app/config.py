# server/app/config.py

import os

class Config:
    HOST = os.getenv('IB_HOST', '127.0.0.1')
    PORT = os.getenv('IB_PORT', 4001)
    CLIENT_ID = os.getenv('IB_CLIENT_ID', 5)

