# import libraries
import pandas as pd
import numpy as np
import datetime
import requests, json, websocket
import yfinance as yf

# import functions
from config import *
from functions import *
import param

# get public and private keys from config file and set headers
public_key, private_key=get_keys()
headers={'APCA-API-KEY-ID':public_key, 'APCA-API-SECRET-KEY':private_key}

# define urls for get and post requests
base_url="https://paper-api.alpaca.markets"
account_url="{}/v2/account".format(base_url)
positions_url="{}/v2/positions".format(base_url)
orders_url="{}/v2/orders".format(base_url)

print("Checking indexes")
top_indexes=index_check()

print(top_indexes)

#
res=get_stock_groups(top_indexes)
print(res)


