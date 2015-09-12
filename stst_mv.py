# coding=utf-8
# stst_mv means stock trading strategy moving average
from pyalgotrade import strategy
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.technical import ma
from pyalgotrade.technical import atr
from pyalgotrade.technical import cross
import math


class MovingAvgStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, periods, atr_period = 7):
        '''
        there would be different period
        '''
        # set the beginning cash as 10000
        strategy.BacktestingStrategy.__init__(self, feed, 100000)
        self.position = None
        self.instrument = instrument
        # use the adjusted close
        self.setUseAdjustedValues(True)
        self.atr = atr.ATR(feed[instrument], atr_period) # the period of atr is 7 days
        self.price = feed[instrument].getPriceDataSeries() # not getDataSeries
        self.current_high = None

        # the smas
        self.s = []
        for p in periods:
            self.s.append(ma.SMA(feed[instrument].getPriceDataSeries(), p))

    def onBars(self, bars):
        bar = bars[self.instrument]
        for m in self.s:
            if m[-1] is None:
                return
        if self.atr[-1] is None:
            return

        # test if it is open day
        if bar.getVolume() <= 0:
            return

        if self.position is None:
            open_long = False
            if cross.cross_above(self.price, self.s[0]):
            # if bar.getPrice()> self.s[0][-1]:
                open_long = True
                for i in range(0,len(self.s)-1):
                    if self.s[i][-1] < self.s[i+1][-1]:
                        open_long = False
            if open_long:
                shares = min(math.floor(self.getBroker().getCash()*0.01/self.atr[-1]), 0.9*math.floor(self.getBroker().getCash()/bar.getPrice()))
                # print('shares {}'.format(shares))
                self.position = self.enterLong(self.instrument, shares, True)
        elif not self.position.exitActive():
            open_short = False
            # the mv exit
            if cross.cross_below(self.price, self.s[0]):
            # if bar.getPrice() < self.s[0][-1]:
                open_short = True
                for i in range(0,len(self.s)-1):
                    if self.s[i][-1] > self.s[i+1][-1]:
                        open_short=False
            # if bar.getPrice() < self.atr_stop_loss(bar):
            #     open_short = True
            if open_short:
                self.position.exitMarket()
        # self.info('The current price is {}, and atr is {}'.format(self.price[-1], self.atr[-1]))

    def atr_stop_loss(self, bar):
        '''
        calculate the atr stop loss price
        '''
        if self.atr[-1] is None:
            return
        self.current_high = max(self.current_high, bar.getPrice())
        light_atr = self.current_high - 2.5 * self.atr[-1]
        yoyo_atr = self.price[-2] - 2 * self.atr[-1]
        return max(light_atr, yoyo_atr)


    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info("BUY at $%.2f" % (execInfo.getPrice()))

        # set the current highest price of the position
        self.current_high = execInfo.getPrice()

    def onEnterCanceled(self, position):
        self.position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info("SELL at $%.2f" % (execInfo.getPrice()))
        self.position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.position.exitMarket()

def test():
    # test the strategy
    feed = yahoofeed.Feed()
    feed.addBarsFromCSV('2823hk', './data/2846.HK.csv')

    # evaluate the strategy
    myStrategy = MovingAvgStrategy(feed, '2823hk', 5, 10, 20, atr_period=20)
    myStrategy.run()
    print('final portfolio value: {}'.format(myStrategy.getBroker().getEquity()))
    return

if __name__ == '__main__':
    test()
