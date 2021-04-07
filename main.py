# import libraries
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests, json, websocket
import yfinance as yf

import xgboost as xgb
from xgboost import XGBClassifier
import pickle
from xgb_functions import *


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

# check whether the market is open
if check_market():
	print("Market is open!")
else:
	print("Market is closed, exiting script")
	exit()

print("Checking indexes")
top_indexes=index_check()

print(top_indexes)

groups=get_stock_groups(top_indexes)

# ticker_list=[]
# for g in groups:
# 	ticker_file='models/'+g+'.csv'
# 	ls=get_samples(file=ticker_file,n=5)
# 	ticker_list+=ls

# print(len(ticker_list))

# download data from yfinance
# ct = datetime.datetime.today()+timedelta(days=1)
# end = ct.strftime("%Y-%m-%d")
# start=ct-timedelta(days=120)
# start=start.strftime("%Y-%m-%d")
# prediction_data=get_data(ticker_list,exchange='',start=start,end=end)
# print("Data download complete, calculating technicals...")

# calculate technical 
# predictiondf=SMA(prediction_data,10)
# predictiondf=FI(predictiondf,30)
# predictiondf=RSI(predictiondf,14)
# predictiondf=MACD(predictiondf,10,30)
# predictiondf=MACD(predictiondf,5,10)
# predictiondf=MACDiff(predictiondf,5)
# predictiondf=index(predictiondf,index='SPY',days=30)

group='US_METALS'

get_predictions(group)






