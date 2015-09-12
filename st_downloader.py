# coding=utf-8
import pandas as pd
import pandas.io.data as web
from datetime import datetime

# This module is to fetch and update the stock data, including stock list and stock meta data


d_source = 'yahoo'

def hk_stock_code(i):
    '''
    generate the hong kong stock code based on number
    '''
    return '.'.join([
        i,
        'HK'
        ])


def fetch_all_stock_list():
    '''
    fetch all the company code from yahoo finance and save to file
    no need to update very frequently
    '''
    st_code_file = open('./data/code.txt', 'w')
    stock_code_list= []
    for i in range(0, 9999):
        for j in range(3,6):
            stock_code = hk_stock_code(str(i).zfill(j))
            # print('trying code {}'.format(stock_code))

            try:
                web.DataReader(stock_code, d_source)
            except OSError:
                # print('code {} failure'.format(stock_code))
                continue

            stock_code_list.append(stock_code)
            print('code {} success!'.format(stock_code))
            break # jump out this inner loop
    st_code_file.write('\n'.join(stock_code_list))
    st_code_file.close()
    return

def update_stock(code, st=None):
    '''
    update one single stock data
    '''
    try:
        if st is None:
            d = web.DataReader(code, d_source, end=datetime.now())
        else:
            d = web.DataReader(code, d_source, start=st, end=datetime.now())
        d.to_csv('./data/{}.csv'.format(code))
        print('stock {} is updated'.format(code))
    except:
        print('Oops, some error happens....sorry')

def update():
    '''
    update the stock data
    '''
    print('updating the stock data...')
    with open('./data/code.txt') as codes:
        for line in codes.readlines():
            update_stock(line.strip())
    print('update completed')



def test():
    print('stock download.')


if __name__ == '__main__':
    update()
