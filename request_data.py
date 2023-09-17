import requests
import pandas as pd
import numpy as np

url = 'https://data.binance.com'
klines_url = '/api/v3/klines'
time_url = '/api/v3/time'

symbol1 = 'BTCBUSD'
symbol2 = 'ETHBUSD'
interval = '15m'  #15 minute intervals
limit = 1000

#days per request: 1000 intervals * 15 minutes per interval / 60 minutes per hour / 24 hours per day
#=10.41667

DURATION = int(1000 * 3600 * 1000 / 4) # miliseconds
TIME_NOW = 1669054998231#1661278998231 #1681278998231 #int(time.time()*1000) - int(DURATION * 0) # microseconds
print("TIME_NOW: ", TIME_NOW)
PERIODS = 16 # number of requests

if __name__ == '__main__':
    params1 = {'symbol': symbol1, 'interval': interval, 'limit': limit, 'startTime': TIME_NOW - DURATION * PERIODS}
    params2 = {'symbol': symbol2, 'interval': interval, 'limit': limit, 'startTime': TIME_NOW - DURATION * PERIODS}

    klines1 = []
    klines2 = []
    for i in range(PERIODS):
        klines1 += requests.get(url + klines_url, params1).json()
        klines2 += requests.get(url + klines_url, params2).json()

        params1['startTime'] += DURATION
        params2['startTime'] += DURATION

    price1_history = pd.DataFrame(np.array(klines1),
                              columns=['open_time', 'open_price', 'high_price', 'low_price', 'close_price', 'volume',
                                       'close_time', 'quote_asset_volume', 'number_of_trades',
                                       'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'unused'])
    price2_history = pd.DataFrame(np.array(klines2),
                              columns=['open_time', 'open_price', 'high_price', 'low_price', 'close_price', 'volume',
                                       'close_time', 'quote_asset_volume', 'number_of_trades',
                                       'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'unused'])
    price1_history.to_pickle('price1_history.pkl')
    price2_history.to_pickle('price2_history.pkl')
