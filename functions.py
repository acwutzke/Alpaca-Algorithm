import requests, json, datetime
import yfinance as yf
import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None
import param

import xgboost as xgb
from xgboost import XGBClassifier
import pickle
from xgb_functions import *


# get account information
def get_account(account_url, headers):
  r=requests.get(account_url, headers=headers)
  return json.loads(r.content)

# get open positions
def get_positions(positions_url,headers):
  r=requests.get(positions_url, headers=headers)
  return json.loads(r.content)

# create a new stock buy or sell order
def create_order(orders_url,headers,symbol,qty,side,order_type,time_in_force):
  order_info = {
      'symbol':symbol,
      'qty': qty,
      'side':side,
      'type': order_type,
      'time_in_force':time_in_force,
  }
  r=requests.post(orders_url,json=order_info,headers=headers)
  return json.loads(r.content)

# get current index price/ 50 day SMA of index
def index_check():

  # get indexes to evaluate from param file
  index=''
  groups=param.stock_groups
  for g in groups:
    index+=groups[g][0]+' '

  # define start and end time
  ct = datetime.datetime.today()+datetime.timedelta(days=1)
  end = ct.strftime("%Y-%m-%d")
  start=ct-datetime.timedelta(days=100)
  start=start.strftime("%Y-%m-%d")

  # get index information from yahoo finance
  data=yf.download(tickers=index, start=start, end=end,interval="1d") 
  data=pd.DataFrame(data)
  df=df_cleanup(data)

  # calculated sma for each index and add to df
  for c in df.columns:
    if c!='Date' and c[-6:]!='volume':
      n=c+'_sma'
      df[n]=df[c]/df[c].rolling(50).mean()

  # get sma of each index at today's date
  ind={}
  for c in df.columns:
    if c[-3:]=='sma':
      ind[c]=df[c].iloc[-1]

  # sort dictionary
  ind={k: v for k, v in sorted(ind.items(), key=lambda item: item[1], reverse=True)}
  # take top three indexes
  print("Top indexes over 50 day SMA:")
  cntr=0
  topind={}
  for i in ind:
    if ind[i]>1 and cntr<3:
      topind[i]=ind[i]
    cntr+=1
  return topind

# function to clean up yfinance output for pandas
# takes a pandas dataframe 
# removes columns we don't need and renames columns
def df_cleanup(df):
    df=df.reset_index()
    # list to store columns we want to keep
    col_list=[]
    # list to store new names of columns
    col_newname=[]
    # create list of columns to loop through
    cols=df.columns.to_list()
    for c in cols:
        if c[0]=='Date':
            col_list.append(c)
            col_newname.append(c[0])
        if c[0]=='Adj Close':
            col_list.append(c)
            col_newname.append(c[1])
        if c[0]=='Volume':
            col_list.append(c)
            col_newname.append(c[1]+'_volume')
    # create datafram with only desired columns
    dfclean=df[col_list]
    # change the names of the columns
    dfclean.columns=col_newname
    # make change date column to datetime object
    dfclean['Date']=pd.to_datetime(dfclean['Date'], format='%Y-%m-%d')
    # return the clean dataframe
    return dfclean  

def get_stock_groups(top_indexes):
  ls=[]
  groups=param.stock_groups
  print('Stock picks will be made from the following groups:')
  for i in top_indexes:
    for g in groups:
      if i[:len(i)-4]==groups[g][0]:
        print(g)
        ls.append(g)
  return ls

def check_market():
  ct = datetime.datetime.today()+datetime.timedelta(days=1)
  end = ct.strftime("%Y-%m-%d")
  start=ct-datetime.timedelta(days=1)
  start=start.strftime("%Y-%m-%d")
  data = yf.download("SPY", start=start, end=end)
  data=data.reset_index()
  if data['Date'].iloc[0].strftime("%Y-%m-%d")==datetime.datetime.today().strftime("%Y-%m-%d"):
    return True
  return False

def get_predictions(group):

  ticker_file='models/'+group+'.csv'
  ticker_list=get_samples(file=ticker_file,n='all')
  print("downloading ticker list: ",ticker_list)

  # download data from yfinance
  ct = datetime.datetime.today()+timedelta(days=1)
  end = ct.strftime("%Y-%m-%d")
  start=ct-timedelta(days=120)
  start=start.strftime("%Y-%m-%d")
  prediction_data=get_data(ticker_list,exchange='',start=start,end=end)
  print("Data download complete")
  print("calculating technicals...")

   
  predictiondf=SMA(prediction_data,10)
  predictiondf=FI(predictiondf,30)
  predictiondf=RSI(predictiondf,14)
  predictiondf=MACD(predictiondf,10,30)
  predictiondf=MACD(predictiondf,5,10)
  predictiondf=MACDiff(predictiondf,5)
  predictiondf=index(predictiondf,index='SPY',days=30)
  print("Technicals calculated")
  print("Generating dataset for XGBoost...")

  feat=['sma','rsi','fi','macd','index']
  predictionset=generate_xgb_set(predictiondf,features=feat)
  predictionset=predictionset.dropna()

  # Based on correlation with the target these are observed to be the best features
  best_feat=['_sma_10','_rsi_14','_fi_30','_macd_5_10','_macd_10_30_diff5','_index_SPY30']

  # dump train and test sets into numpy arrays for training
  x_prediction=predictionset[best_feat].to_numpy()
  extra_prediction=predictionset[['Date','STOCK']].to_numpy()
  print(x_prediction.shape)
  print("Dataset for XGBoost prepared")
  print("Loading model...")

  model_name='models/'+group+'_model.pickle.dat'

  try:
    model = pickle.load(open(model_name, "rb"))
  except:
    print("Model not found, make sure the model exists in the models folder.")
    exit()

  print("Model loaded! making predictions...")
  pred=model.predict_proba(x_prediction)
  predyes=[]
  for p in pred:
    predyes.append(p[1])

  resultdf=pd.DataFrame(extra_prediction)
  resultdf.columns=['Date','Stock']
  resultdf['prediction']=predyes
  resultdf=resultdf.sort_values(by=['Date','prediction'], ascending=False).head(5)
  print(resultdf)