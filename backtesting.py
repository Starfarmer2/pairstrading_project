import pandas as pd
from typing import Type
import numpy as np

class Backtest:
    def __init__(self, trader, price_history: pd.DataFrame, BIDASK_SPREAD=0.2/100, TRADING_FEE = 0.1/100):
        self.pnl_history = []
        self.transaction_history = []
        self.positions = {'price1': [], 'price2': []}
        self.trader = trader
        self.price_history = price_history
        self.bidask_spread = BIDASK_SPREAD
        self.trading_fee = TRADING_FEE

    def run_game(self):

        for t in range(len(self.price_history['price1'])):
            trades = self.trader.makeTrades(self.price_history.loc[t])
            trade1_price_factor = 1 + np.sign(trades['price1'])*(self.bidask_spread/2+self.trading_fee)
            trade2_price_factor = 1 + np.sign(trades['price2']) * (self.bidask_spread / 2 + self.trading_fee)
            curr_pnl = 0
            curr_pnl -= trades['price1']*self.price_history['price1'][t]*trade1_price_factor
            curr_pnl -= trades['price2'] * self.price_history['price2'][t] * trade2_price_factor
            self.pnl_history.append(curr_pnl)
            if trades['price1'] != 0 or trades['price2'] != 0:
                self.transaction_history.append([t, trades['price1'], trades['price2'], trades['price1']*self.price_history['price1'][t], trades['price2']*self.price_history['price2'][t], trades['price1']*self.price_history['price1'][t] + trades['price2']*self.price_history['price2'][t]])
        self.transaction_history = pd.DataFrame(np.array(self.transaction_history), columns = ['time', 'price1', 'price2', 'total1', 'total2', 'totalt'])
        return (self.pnl_history,np.sum(self.pnl_history), self.transaction_history)