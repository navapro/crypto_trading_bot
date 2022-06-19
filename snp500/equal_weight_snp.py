import string
from sys import byteorder
import numpy as np
import pandas as pd
import requests
import xlsxwriter
import math
from secrets import IEX_CLOUD_API_TOKEN

# from: https://stackoverflow.com/questions/312443/how-do-i-split-a-list-into-equally-sized-chunks
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# Access data from an API for latest snp500 information.
stocks = pd.read_csv("sp_500_stocks.csv")

my_columns = ['Ticker', 'Stock Price', 'Market Capitalization', 'Number of Shares to Buy']

# Call IEX Cloud API (Sandbox mode)

symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in symbol_groups:
    symbol_strings.append(','.join(i))

final_dataframe = pd.DataFrame(columns= my_columns)

for symbol_string in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        price = data[symbol]['quote']['latestPrice']
        market_cap = data[symbol]['quote']['marketCap']

        final_dataframe = final_dataframe.append(pd.Series([symbol, price, market_cap, 'N/A'], 
        index= my_columns), ignore_index= True)    


portfolio_size = input('Enter the value of your portfolio:')
try:
    value = float(portfolio_size)
except ValueError:
    print("That's not a number ! \n please try again:")
    portfolio_size = input('Enter the value of your portfolio:')
    value = float(portfolio_size)

position_size = value/ len(final_dataframe.index)

for i in final_dataframe.index:
    final_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size/final_dataframe.loc[i, 'Stock Price'])


# Writing the information to .xlsx file
writer = pd.ExcelWriter('recomended_trades.xlsx', engine = 'xlsxwriter')
final_dataframe.to_excel(writer, 'Recommended Trades', index = False)

# Formatting the excel file
background_color = '#0a0a23'
font_color = '#ffffff'
border = 1

string_format = writer.book.add_format(
    {
        'font_color' : font_color,
        'bg_color' : background_color,
        'border' : border,
    }
)

dollar_format = writer.book.add_format(
    {
        'font_color' : font_color,
        'bg_color' : background_color,
        'border' : border,
        'num_format' : '$0.00',
    }
)

integer_format = writer.book.add_format(
    {
        'font_color' : font_color,
        'bg_color' : background_color,
        'border' : border,
        'num_format' : '0',
    }
)

column_formats = { 
                    'A': ['Ticker', string_format],
                    'B': ['Price', dollar_format],
                    'C': ['Market Capitalization', dollar_format],
                    'D': ['Number of Shares to Buy', integer_format]
                    }

for column in column_formats.keys():
    writer.sheets['Recommended Trades'].set_column(f'{column}:{column}', 20, column_formats[column][1])
    writer.sheets['Recommended Trades'].write(f'{column}1', column_formats[column][0], string_format)

writer.save()