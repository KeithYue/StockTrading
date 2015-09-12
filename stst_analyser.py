# coding=utf-8
# analyse the performance of the strategy
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.stratanalyzer import returns as rts
from pyalgotrade.stratanalyzer import sharpe
from pyalgotrade.stratanalyzer import drawdown
from pyalgotrade.stratanalyzer import trades
from utility import Stock
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import csv
import stst_mv
import logging
# logging.basicConfig(level=logging.DEBUG)

def best_mv(stock):
    '''
    calculate best mv period for the stock code
    '''
    atr = 7 # the default atr period is 7
    path = stock.path
    stock_code = stock.code
    best_mv = 0
    lowest = -1000
    r = None
    for i in range(5,50):
        print('tring {}'.format(i))
        feed = yahoofeed.Feed()
        feed.addBarsFromCSV(stock_code, path)
        s = stst_mv.MovingAvgStrategy(feed, stock_code, (i, ), atr_period=atr)
        try:
            results = run_analyse(s)
        except Exception as e:
            print(e)
            continue

        # print(results)
        if results['cumulative_return'] > lowest:
            lowest = results['cumulative_return']
            r = results
            best_mv = i
    r['stock_code'] = stock_code
    r['best_moving_average'] = best_mv
    print(r)
    return r

def run_analyse(myStrategy):
    # Attach different analyzers to a strategy before executing it.
    retAnalyzer = rts.Returns()
    myStrategy.attachAnalyzer(retAnalyzer)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    myStrategy.attachAnalyzer(sharpeRatioAnalyzer)
    drawDownAnalyzer = drawdown.DrawDown()
    myStrategy.attachAnalyzer(drawDownAnalyzer)
    tradesAnalyzer = trades.Trades()
    myStrategy.attachAnalyzer(tradesAnalyzer)

    # Run the strategy.
    myStrategy.run()
    print("Final portfolio value: $%.2f" % myStrategy.getResult())
    print("Cumulative returns: %.2f %%" % (retAnalyzer.getCumulativeReturns()[-1] * 100))
    print("Sharpe ratio: %.2f" % (sharpeRatioAnalyzer.getSharpeRatio(0.05)))
    print("Max. drawdown: %.2f %%" % (drawDownAnalyzer.getMaxDrawDown() * 100))
    print("Longest drawdown duration: %s" % (drawDownAnalyzer.getLongestDrawDownDuration()))

    print()
    print("Total trades: %d" % (tradesAnalyzer.getCount()))
    if tradesAnalyzer.getCount() > 0:
        profits = tradesAnalyzer.getAll()
        print("Avg. profit: $%2.f" % (profits.mean()))
        print("Profits std. dev.: $%2.f" % (profits.std()))
        print("Max. profit: $%2.f" % (profits.max()))
        print("Min. profit: $%2.f" % (profits.min()))
        r = tradesAnalyzer.getAllReturns()
        print("Avg. return: %2.f %%" % (r.mean() * 100))
        print("r std. dev.: %2.f %%" % (r.std() * 100))
        print("Max. return: %2.f %%" % (r.max() * 100))
        print("Min. return: %2.f %%" % (r.min() * 100))

    print()
    print("Profitable trades: %d" % (tradesAnalyzer.getProfitableCount()))
    if tradesAnalyzer.getProfitableCount() > 0:
        profits = tradesAnalyzer.getProfits()
        print("Avg. profit: $%2.f" % (profits.mean()))
        print("Profits std. dev.: $%2.f" % (profits.std()))
        print("Max. profit: $%2.f" % (profits.max()))
        print("Min. profit: $%2.f" % (profits.min()))
        returns = tradesAnalyzer.getPositiveReturns()
        print("Avg. return: %2.f %%" % (returns.mean() * 100))
        print("Returns std. dev.: %2.f %%" % (returns.std() * 100))
        print("Max. return: %2.f %%" % (returns.max() * 100))
        print("Min. return: %2.f %%" % (returns.min() * 100))

    print()
    print("Unprofitable trades: %d" % (tradesAnalyzer.getUnprofitableCount()))
    if tradesAnalyzer.getUnprofitableCount() > 0:
        losses = tradesAnalyzer.getLosses()
        print("Avg. loss: $%2.f" % (losses.mean()))
        print("Losses std. dev.: $%2.f" % (losses.std()))
        print("Max. loss: $%2.f" % (losses.min()))
        print("Min. loss: $%2.f" % (losses.max()))
        returns = tradesAnalyzer.getNegativeReturns()
        print("Avg. return: %2.f %%" % (returns.mean() * 100))
        print("Returns std. dev.: %2.f %%" % (returns.std() * 100))
        print("Max. return: %2.f %%" % (returns.max() * 100))
        print("Min. return: %2.f %%" % (returns.min() * 100))

    return dict(cumulative_return=retAnalyzer.getCumulativeReturns()[-1], sharp_ratio = sharpeRatioAnalyzer.getSharpeRatio(0.05), max_dropdown= drawDownAnalyzer.getMaxDrawDown() * 100)
def test():
    feed = yahoofeed.Feed()
    feed.addBarsFromCSV('test_stock', './data/0285.HK.csv')

    myStrategy = stst_mv.MovingAvgStrategy(feed, 'test_stock', (20, ), atr_period=7)
    run_analyse(myStrategy)

if __name__ == '__main__':
    test()
    # stocks = []
    # with open('./data/code.txt') as c:
    #     for l in c.readlines():
    #         s = Stock(l.strip())
    #         # only process regular stock
    #         if s.data['adj close'].iloc[-1]  > 0.5 and s.data['volume'].iloc[-1] > 5000000:
    #             # print(s.data['adj close'].iloc[-1])
    #             stocks.append(s)

    # # init the process pool
    # pool = Pool()
    # rs = pool.map(best_mv, stocks)
    # pool.close()
    # # wait for the work to finish
    # pool.join()

    # #write to the file
    # with open('./results/best_singleMV.csv', 'w') as f:
    #     writer = csv.DictWriter(f, rs[0].keys())
    #     writer.writeheader()
    #     for r in rs:
    #         writer.writerow(r)


