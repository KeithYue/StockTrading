# coding=utf-8
import pandas as pd
import pandas.io.data as web
import os
import numpy as np
import logging
# config the logging system
logging.basicConfig(level=logging.DEBUG)

from scipy.signal import argrelextrema, argrelmin, argrelextrema

from talib.abstract import *

# load the utility function
from utility import Stock, gold_cross_number, send_email, smooth
from tools.tabulate import tabulate

# this module is used to select stock whose price would increase
st_list = [] # list containing candidate stock
indicators = [] # a set of function that indicates a positive stock
total_cash = 40000

macd_parameters = dict(fastperiod=12, slowperiod=26, signalperiod=9)

# window size of the history data
window_size = 40

# the indicators
def is_increasing(stock):
    return stock.data.iloc[-1].close > stock.data.iloc[-2].close

# whether the volumn in top 100 among all stock
def is_vol_increasing(stock):
    return stock.data.iloc[-1].volume > stock.data.iloc[-2].volume

def is_in_vol_top100(stock):
    '''
    whether the volumn is larger than 50000000
    '''
    return stock.data.iloc[-1].volume > 10000000

def field_vol(stock):
    '''
    whether there is recent field volume recently
    '''
    floor_vol_index = stock.data.iloc[-20:].volume.idxmin()
    # logging.info(floor_vol_index - len(stock.data))
    floor_vol_index = floor_vol_index - len(stock.data)
    return floor_vol_index in range(-4,0)

def field_price(stock):
    floor_price_index = stock.data.iloc[-20:].close.idxmin()
    floor_price_index = floor_price_index - len(stock.data)
    return floor_price_index == -1


def MACD_gold_number(stock, freq=window_size):
    dif, dae, macd = MACD(stock.data.tt(), **macd_parameters)
    if len(macd) < freq:
        return False
    return np.max(dif[-freq:]) < 0 and gold_cross_number(macd) > 2

def MACD_X(stock):
    '''
    whether there a X  in recent days
    '''
    dif, dae, macd = MACD(stock.data.tt(), **macd_parameters)
    return dif[-1]>dae[-1] and dif[-2]<dae[-2]

def MACD_deviate(stock,freq = window_size):
    '''
    whether there is deviate between
    '''
    dif, dae, macd = MACD(stock.data.tt(), **macd_parameters)
    close_data = stock.data['adj close']
    dates = stock.data['date']
    if len(dif) < freq:
        return False
    # smooth the dif
    # dif = smooth(dif,window_len=3)
    local_mini_indexes_cand = argrelextrema(dif, lambda x,y:  x-y<0)[0]

    # the day of the local minimum
    # ensure the stock is in the time window
    local_mini_indexes = [i for i in local_mini_indexes_cand  if dif[i] < dae[i] and dif[i] <0 and i > len(dif)-freq]
    # for i in local_mini_indexes:
    #     print(dates[i], dif[i])

    # generate all the indexes

    # calculate the deviate
    d_count = 0
    # print(stock.code, local_mini_indexes)
    for prev, next_ in zip(local_mini_indexes[0:-1], local_mini_indexes[1:]):
        a = dif[prev] - dif[next_]
        b = close_data.iloc[prev] - close_data.iloc[next_]
        # print(dates[prev], dates[next_])
        if a*b<0:
            d_count += 1
    # the times of deviate higher, the rating is higher
    # print(d_count)
    return d_count

def MA10_breaking(stock):
    '''
    five days is larger than ten days
    '''
    ma10 = SMA(stock.data.tt(), 10)
    return stock.data.iloc[-1].open < ma10[-1] and stock.data.iloc[-1].close> ma10[-1] and stock.data.iloc[-2].close < ma10[-2]

def MA5_MA10_breaking(stock):
    ma10 = SMA(stock.data.tt(), 10)
    ma5 = SMA(stock.data.tt(), 5)
    return ma5[-1] > ma10[-1]

def MA10_MA20_breaking(stock):
    ma10 = SMA(stock.data.tt(), 10)
    ma20 = SMA(stock.data.tt(), 20)
    return ma10[-1] > ma20[-1]





# pattern recognition
def cdl_morning_star(stock):
    '''
    test whether there is a morning star in recent days
    '''
    inds = CDLMORNINGSTAR(stock.data.tt())
    inds2 = CDLMORNINGDOJISTAR(stock.data.tt())
    return sum(inds[-3:])>0 or sum(inds2[-3:])>0

def inverted_hammer(stock):
    return CDLINVERTEDHAMMER(stock.data.tt())[-1] > 0

def hammer(stock):
    return CDLHAMMER(stock.data.tt())[-1] > 0

def is_red(stock):
    l = stock.data.iloc[-1]
    return l.open < l.close

def KDJ(stock):
    '''
    extra buy
    extra sell
    '''
    k,d = STOCH(stock.data.tt())
    return k[-1] <=30 and d[-1] <=30


indicators.extend([
    (MACD_gold_number, 2),
    (MACD_deviate, 2),
    (MACD_X, 2),
    ])

# the sorting rules
def rating(stock):
    '''
    given one stock
    return the rating of this stock as the sorting key
    '''
    r = 0
    meta_rating = []
    for i in indicators:
        results = i[0](stock)
        inc = 0
        if type(results) is bool:
            if results:
                inc = 1 * i[1]
        else:
            inc = results
        r = r + inc
        # record the score
        meta_rating.append((i[0].__name__, inc))
    stock.rating = r
    stock.meta_rating = meta_rating
    return r





def test():
    logging.info(st_list[5].code)
    logging.info(CDLMORNINGSTAR(st_list[5].data[:].tt())[-1000:])
    pass

def summary():
    '''
    summerize all the promising stock information
    '''
    summaries = []
    for s in st_list[:20]:
        summaries.append(get_information(s))
    text = tabulate(summaries, headers = 'keys', tablefmt='fancy_grid')
    print(text)
    table_html = tabulate(summaries, headers = 'keys', tablefmt='html')
    return table_html

def get_information(s):
    '''
    get the current information of one stock
    '''
    atr = ATR(s.data.tt())[-1]
    d = {}
    d['code']=s.code
    d['score']=s.rating
    d['atr'] = atr
    d['shares'] = 0.01*total_cash/atr
    d['cost'] = 0.01*total_cash*s.data['adj close'].iloc[-1]/atr
    d['desc'] = str(s.meta_rating)
    return d


def main():
    # load the stock data
    global st_list
    logging.info('loading the sotck data...')

    with open('./data/code.txt') as f:
        for c in f.readlines():
            st_list.append(Stock(c.strip()))


    # filter out the stock
    # sort the stock
    # print(st_list)

    # filter out the stocks
    st_list = [s for s in st_list if s.data.iloc[-1].volume * s.data.iloc[-1]['adj close'] >= 5000000]

    logging.info('STOCK NUM: {}'.format(len(st_list)))

    logging.info('sorting the stock...')

    st_list.sort(key=rating, reverse=True)

    # only preserve the max ratings
    # st_list = [s for s in st_list if s.rating == st_list[0].rating]
    send_email(summary())


if __name__ == '__main__':
    main()
    # MACD_deviate(Stock('0285.HK'), 100)
