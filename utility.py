# coding=utf-8
# utility function of stock
import os
import pandas as pd
import numpy as np
import logging
# config the logging system
logging.basicConfig(level=logging.DEBUG)

# define Stock class
class Stock():
    '''
    the stock class
    '''
    def __init__(self, code):
        self.code=code

        # search and load the stock data
        try:
            for f in os.listdir('./data'):
                if f.startswith(self.code):
                    self.path = './data/{}'.format(f)
                    data = pd.read_csv(self.path, parse_dates=['Date'])
            data.rename(columns=str.lower, inplace=True)
        except Exception as e:
            logging.error(e)
        self.data=data # the raw dataframe data
        # logging.info(self.data)
        return


    def __str__(self):
        return self.code

# modify the DataFrame class to convert dict-like data for talib compudation
def tt(self):
    '''
    convert DataFrame to talib computation data
    tt means to talib
    return dict-like data
    '''
    d = {}
    for c in self.columns:
        d[c] = np.asarray(self[c])
    return d
pd.DataFrame.tt = tt

def gold_cross_number(s):
    '''
    given a time series, return the count of crossing
    '''
    count = 0
    for i in range(0, len(s)-1):
        if s[i] < 0 and s[i+1]>0:
            count = count + 1
    return count

def send_email(body):
    import smtplib
    # Import the email modules we'll need
    from email.mime.text import MIMEText
    user = "comp5331.ust@gmail.com"
    pwd = "keith5805880"
    recipient = "ywangby@connect.ust.hk"
    subject = "From Keith: Promising Stock Codes"
    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    msg['From'] = user
    msg['To'] = recipient
    try:
        # server = smtplib.SMTP_SSL('smtp.gmail.com:465')
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.send_message(msg)
        server.quit()
        print('successfully sent the mail')
    except Exception as e :
        print(e)

# smooth the timeseries function
def smooth(x,window_len=11,window='hanning'):
    """smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    input:
      x: the input signal
      window_len: the dimension of the smoothing window; should be an odd integer
      window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
          flat window will produce a moving average smoothing.

    output:
      the smoothed signal

    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)

    see also:

    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter

    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
      raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
      raise ValueError("Input vector needs to be bigger than window size.")


    if window_len<3:
      return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
      raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")


    s=np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
#print(len(s))
    if window == 'flat': #moving average
      w=np.ones(window_len,'d')
    else:
      w=eval('np.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='valid')
    return y[(window_len/2-1):-(window_len/2)]


def test():
    s = Stock('0001')
    print(s.data)

if __name__ == '__main__':
    test()
