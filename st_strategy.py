# coding=utf-8

# this tool is used to follow the stock trading and give the point to leave the market
import logging
import pandas as pd
from talib.abstract import *
from utility import Stock
from talib.abstract import *

# config the logging system
logging.basicConfig(level=logging.DEBUG)


def atr(stock_code):
    '''
    get the atr value of the stock code
    '''
    s = Stock(stock_code)
    atr = ATR(s.data.tt(), timeperiod=10)
    return atr

def stop_loss(code, str_start_date, price=None):
    '''
    give the stock code and buying date
    return the stop loss price
    code: stock code
    start date: the date buy the stock
    '''
    if price is not None:
        sl_price = 0.95 * price
    else:
        sl_price = 0

    stock = Stock(code)
    start_index = stock.data.index.get_indexer_for(stock.data[stock.data.date == str_start_date].index)[0]
    df = stock.data[start_index:]
    max_close = max(df.close)
    current_close = df.iloc[-1].close
    current_atr = atr(code)[-1]

    light_sl = max_close - 1.77 * current_atr
    yoyo_sl = current_close - 0.77 * current_atr
    # print('max close {}'.format(max_close))
    # print('current atr {}'.format(current_atr))
    # print(sl)
    print(light_sl, yoyo_sl, sl_price)
    return max(light_sl, yoyo_sl, sl_price)

def test():
    stop_loss('2823', '2015-08-05')
    return

def main():
    # read the record file and output the loss and stop price
    record = pd.read_csv('./data/record.csv')
    print('The loss and close price of the stock is:')
    for i in record.index:
        st_code = str(record.ix[i].code)[-4:].zfill(4)
        date = record.ix[i].date
        # print(record.ix[i].date)
        price = record.ix[i].price
        print(st_code, stop_loss(st_code, date, price))



if __name__ == '__main__':
    main()
    # print(atr('0521')[-100:])
