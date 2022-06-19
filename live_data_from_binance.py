from socket import socket
import pandas as pd
import sqlalchemy
import asyncio
from binance.client import Client
from binance import BinanceSocketManager
from secrets import api_key, api_secret

def create_frame(msg):
    df = pd.DataFrame([msg])
    df = df.loc[:, ['s', 'E', 'p']]
    df.columns = ['symbol', 'time', 'price']
    df.price = df.price.astype(float)
    df.time = pd.to_datetime(df.time, unit='ms')
    return df

async def main():

    client = Client(api_key, api_secret)
    bsm = BinanceSocketManager(client)
    socket = bsm.trade_socket('BTCUSDT')
    engine = sqlalchemy.create_engine('sqlite:///BTCUSDTstream.db')
    
    while True:
        await socket.__aenter__()
        msg = await socket.recv()
        frame = create_frame(msg)
        frame.to_sql('BTCUSDT', engine, if_exists = 'append', index = False)




    





