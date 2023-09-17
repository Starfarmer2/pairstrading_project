from trader_class import PairsTrader
from backtesting import Backtest
import requests
import pandas as pd
import numpy as np
import seaborn
import matplotlib.pyplot as plt
import time


if __name__ == '__main__':
    price1_history = pd.read_pickle('price1_history.pkl')
    price2_history = pd.read_pickle('price2_history.pkl')

    price_history = pd.DataFrame(np.array([price1_history['open_price'], price2_history['open_price']]).transpose(),
                                 columns=['price1', 'price2'], dtype='float64')

    trader = PairsTrader()
    backtester = Backtest(trader,price_history)
    backtest_results = backtester.run_game()
    pnl_history = backtest_results[0]
    sig_pnl_history = [pnl for pnl in pnl_history if pnl != 0]
    print(f'sig_pnl_history: {sig_pnl_history}')
    print(f'pnl: {backtest_results[1]}')
    print(f'transaction history: \n{backtest_results[2]}')



    log = trader.getLog()
    graph_df = pd.DataFrame(np.array([price1_history['open_time'],
                                      log['price_history']['price1'],
                                      log['price_history']['price2'],
                                      log['spread'],
                                      log['spread_percentage'],
                                      ]).transpose(),
                            columns=['time',
                                     'price1',
                                     'price2',
                                     'spread',
                                     'spread_percentage',
                                     ])
    graph_transaction_df = pd.DataFrame(np.array([price1_history['open_time'][np.array(backtest_results[2]['time'],dtype='int')],
                                                  np.sign(backtest_results[2]['price1'])
                                                  ]).transpose(),
                                        columns=['transaction_time',
                                                 'buy_or_sell'])
    seaborn.scatterplot(data=graph_df,x='time',y='spread_percentage',c='r',s=5)
    seaborn.scatterplot(data=graph_transaction_df, x='transaction_time', y='buy_or_sell', c='b', s=30)
    # seaborn.scatterplot(data=graph_df, x='time', y='price2',c='b',s=5)
    ax = plt.gca()
    ax.get_xaxis().set_visible(False)
    plt.show()
