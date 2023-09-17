import numpy as np
from scipy.optimize import minimize_scalar


OPT_INTERVAL = 50 # 50 * 15 min = 12.5 hours
SINGLE_POSITION_AMOUNT = 0.1  # Position with quantity of 0.1 coin1


class PairsTrader:
    def __init__(self):
        self.fuse_margin = 500/100 #5/100  #5% fuse margin
        self.begin_margin = 2.1/100 #2.08/100  #3% begin margin
        self.close_margin = 0.0/100  #0.1% close margin

        self.pair_price_history = { }
        self.pair_price_history['price1'] = []
        self.pair_price_history['price2'] = []

        self.positions = { 'price1': 0, 'price2': 0 }
        self.spread_n = []
        self.opt_count = 0  # If opt_count < OPT_INTERVAL, no active trades
        self.i = 0

    def getLog(self):
        spread = []
        spread_percentage = []
        for i in range(len(self.pair_price_history['price1'])):
            if self.spread_n[i] == None:
                spread.append(None)
                spread_percentage.append(None)
            else:
                curr_spread = self.pair_price_history['price1'][i] - self.pair_price_history['price2'][i] * self.spread_n[i]
                curr_size = self.pair_price_history['price1'][i] + self.pair_price_history['price2'][i] * self.spread_n[i]
                spread.append(curr_spread)
                spread_percentage.append(curr_spread/curr_size*100)

        return { 'spread_n': self.spread_n, 'price_history': self.pair_price_history, 'spread': np.array(spread), 'spread_percentage': np.array(spread_percentage)}

    def initiatePosition(self, buyside, sellside):
        if buyside == 'price1':
            self.positions['price1'] = SINGLE_POSITION_AMOUNT
            self.positions['price2'] = -SINGLE_POSITION_AMOUNT * self.spread_n[self.i]
        else:
            self.positions['price1'] = -SINGLE_POSITION_AMOUNT
            self.positions['price2'] = SINGLE_POSITION_AMOUNT * self.spread_n[self.i]
        print(f'opened, price1 traded: {self.positions["price1"]}, price2 traded: {self.positions["price2"]}')
        return self.positions

    def closePosition(self):
        trades = {}
        trades['price1'] = -self.positions['price1']
        trades['price2'] = -self.positions['price2']
        self.positions['price1'] = 0
        self.positions['price2'] = 0
        print(f'closed, price1 traded: {trades["price1"]}, price2 traded: {trades["price2"]}')
        return trades

    def triggerFuse(self):
        self.opt_count = 0
        print('TRIGGERED_FUSE')
        return self.closePosition()


    # input as np arrays
    def spread(self, p1, p2, n):
        psum = p1-p2*n
        return np.dot(psum,psum)

    def optimize(self, price_history1, price_history2):
        price_history1 = np.array(price_history1)
        price_history2 = np.array(price_history2)
        return minimize_scalar(lambda n: self.spread(price_history1, price_history2, n)).x

    def makeTrades(self, prices):
        trades = {'price1': 0,'price2': 0}

        self.pair_price_history['price1'].append(prices['price1'])
        self.pair_price_history['price2'].append(prices['price2'])
        # if self.i >= 1:
        #     print(f'n: {self.spread_n[self.i-1]}')
        if self.opt_count < OPT_INTERVAL:
            self.spread_n.append(None)
            self.opt_count += 1
            self.i += 1
            return trades
        elif self.opt_count == OPT_INTERVAL:
            n = self.optimize(self.pair_price_history['price1'][self.i - OPT_INTERVAL:self.i],
                                            self.pair_price_history['price2'][self.i - OPT_INTERVAL:self.i])
            self.spread_n.append(n)
            self.opt_count += 1
            self.i += 1
            return trades
        else:
            n = self.optimize(self.pair_price_history['price1'][self.i - OPT_INTERVAL:self.i],
                              self.pair_price_history['price2'][self.i - OPT_INTERVAL:self.i])
            spread_prev = self.pair_price_history['price1'][self.i-1] - self.spread_n[self.i-1] * self.pair_price_history['price2'][self.i-1]
            spread_curr = self.pair_price_history['price1'][self.i] - self.spread_n[self.i-1] * self.pair_price_history['price2'][self.i]
            position_size_curr = self.pair_price_history['price1'][self.i] + self.spread_n[self.i-1] * self.pair_price_history['price2'][self.i]

            # print(f'spread%: {np.abs(spread_curr / position_size_curr)}')
            # Trade active
            if self.positions['price1'] != 0 or self.positions['price2'] != 0:
                # Close trade
                if spread_prev*spread_curr < 0 or np.abs(spread_curr/position_size_curr) <= self.close_margin:
                    self.spread_n.append(n)
                    trades = self.closePosition()
                    self.i += 1
                    return trades
                # Fuse
                elif np.abs(spread_curr/position_size_curr) >= self.fuse_margin:
                    self.spread_n.append(n)
                    trades = self.triggerFuse()
                    self.i += 1
                    return trades
                # Do not close trade
                else:
                    self.spread_n.append(self.spread_n[-1])
                    self.i += 1
                    return trades
            # Trade inactive
            else:
                # Initiate trade

                if np.abs(spread_curr/position_size_curr) >= self.begin_margin:
                    self.spread_n.append(n)
                    # Spread positive, short price1 buy price2
                    if spread_curr > 0:
                        trades = self.initiatePosition(buyside='price2', sellside='price1')
                    # Spread negative, buy price1 short price2
                    else:
                        trades = self.initiatePosition(buyside='price1', sellside='price2')
                    self.i += 1
                    return trades
                # Do not initiate trade
                else:
                    self.spread_n.append(self.spread_n[-1])
                    self.i += 1
                    return trades














