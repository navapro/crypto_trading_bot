from pickle import FALSE
from socket import socket
from statistics import quantiles
import pandas as pd
import sqlalchemy
from binance.client import Client
from binance import BinanceSocketManager
from secrets import api_key, api_secret

client = Client(api_key, api_secret)
engine = sqlalchemy.create_engine('sqlite:///BTCUSDTstream.db')
df = pd.read_sql('BTCUSDT', engine)

# Trendfollowing

def strategy(entry, lookback, qty, open_postition = False):
    while True:
        df = pd.read_sql('BTCUSDT', engine)
        lookback_period = df.iloc[-lookback:]
        cum_ret = (lookback_period.Price.pct_change() + 1).cumprod() - 1
        
        if not open_postition:
            if cum_ret[cum_ret.last_valid_index()] > entry:
                order = client.create_order(symbol = 'BTCUSDT', side = 'BUY', type = 'MARKET', quantity = qty)
                open_postition = True
                print(order)
                break

    if open_postition:
        while True:
            df = df = pd.read_sql('BTCUSDT', engine)
            since_buy = df.loc[df.time > pd.to_datetime(order['transactTime'], unit = 'ms')]

            if len(since_buy) > 1:

                since_buy_ret = ((since_buy.Price.pct_change() + 1).cumprod() - 1)
                last_entry = since_buy_ret[since_buy_ret.last_valid_index()]
                if last_entry > 0.0015 or last_entry < -0.0015:
                    order = client.create_order(symbol = 'BTCUSDT', side = 'SELL', type = 'MARKET', quantity = qty)
                    print(order)
                    break

    return last_entry

def main():

    risen = 0.001
    time_in_sec = 60
    quantity = 0.001
    total_return = 0
    max_loss = 0.001

    while True:
        trade_return = strategy(risen, time_in_sec, quantity)
        total_return += trade_return
        
        if total_return < - max_loss:
            print('Reached maximum loss')
            return