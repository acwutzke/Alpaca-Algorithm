import requests, json, datetime
import yfinance as yf
import pandas as pd
pd.options.mode.chained_assignment = None
import param


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
  print("Top indexes over 50 day SMA")
  cntr=0
  topind={}
  for i in ind:
    if ind[i]>1 and cntr<3:
      topind[i]=ind[i]
    cntr+=1
  return topind


  # data=data.reset_index()[['Date','Adj Close']]
  # data[20]=data['Adj Close'].rolling(20).mean()
  # 
  # data['MACD']=data[20]/data[50]
  # data['index']=data['Adj Close']/data[50]

  # return data['index'].iloc[-1]



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
