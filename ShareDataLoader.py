import akshare as ak
import numpy as np
from matplotlib  import pyplot as plt
from Analytics import *
from TimeCalculator import *

# 获取近一段时间的历史数据, 粒度为天
'''
' duration: 时间窗口
' period: 时间单位, {'daily'}
' code: 股票代码
'''
def getHistoryData(duration, code):
    start_date = getDateWithBias(duration)
    stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start_date, end_date=getTodayDate(), adjust="")
    return stock_zh_a_hist_df

def display(ticker_df):
    plt.rcParams['font.family']='SimHei'
    x_data = ticker_df.index.tolist()      
    y_close = ticker_df['收盘']
    y_amount = ticker_df['成交量']
    x = np.linspace(0, max(ticker_df.index.tolist()), max(ticker_df.index.tolist()) + 1)

    close = getPolifyValue(x_data, y_close, x, 12)
    amount = getPolifyValue(x_data, y_amount, x, 12)
    lmin_close, lmax_close = get_lmin_lmax(close)
    lmin_amount, lmax_amount = get_lmin_lmax(amount)

    print(lmin_close)
    print(lmax_close)
    print(close[lmin_close])
    print(close[lmax_close])
    print(amount[lmin_close])
    plt.figure(figsize=(15, 2), dpi= 120, facecolor='w', edgecolor='k')
    plt.plot(x, close, color='grey')
    # plt.plot(x, amount, color='black')
    plt.plot(x[lmin_close], close[lmin_close], "*", label="min_close", color='r')        # 最小
    plt.plot(x[lmax_close], close[lmax_close], "o", label="max_close", color='r')        # 最大
    # plt.plot(x[lmin_amount], amount[lmin_amount], "*", label = "min_amount", color='g')
    # plt.plot(x[lmax_amount], amount[lmax_amount], "o", label = "max_amount", color = "g")
    plt.title('局部最小 & 最大')
    plt.show()

