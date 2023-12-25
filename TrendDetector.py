from scipy.stats import norm, mstats
import numpy as np
from ShareDataLoader import *
def mk_trend_detect(x, alpha=0.1):
    n = len(x)

    # calculate S
    s = 0
    for k in range(n-1):
        for j in range(k+1, n):
            s += np.sign(x[j] - x[k])

    # calculate the unique data
    unique_x, tp = np.unique(x, return_counts=True)
    g = len(unique_x)

    # calculate the var(s)
    if n == g:  # there is no tie
        var_s = (n*(n-1)*(2*n+5))/18
    else:  # there are some ties in data
        var_s = (n*(n-1)*(2*n+5) - np.sum(tp*(tp-1)*(2*tp+5)))/18

    if s > 0:
        z = (s - 1)/np.sqrt(var_s)
    elif s < 0:
        z = (s + 1)/np.sqrt(var_s)
    else: # s == 0:
        z = 0

    # calculate the p_value
    p = 2*(1-norm.cdf(abs(z)))  # two tail test
    h = abs(z) > norm.ppf(1-alpha/2)
    if (z < 0) and h:
        trend = -1 # 下降趋势
    elif (z > 0) and h:
        trend = 1 # 上升趋势
    else:
        trend = 0 #

    return trend


'''
检查是否是低位放量涨的股票
    收盘价：
    1. 倒数六天内有极值点且最后一个极点为极小值点
    2. 1中选出来的点和上一个极大值点之间的间隔交易日大于等于10
    3. 1, 2中的两个极点之间跌幅超过10%
    交易量：
    4. 1中交易日之后量价齐升高(低alpha MK检验)
    5. 最后一日的交易量为1中的点的两倍以上
'''
def isLowPriceLargeAmountIncrease(code):
    try :
        history_raw = getHistoryData(120, code)
        history = history_raw[["收盘", "成交量"]]
        polified_close = getPolifiedFromRaw(history, "收盘")
        polified_amount = getPolifiedFromRaw(history, "成交量")
        lmin_close, lmax_close = get_lmin_lmax(polified_close)
        
        x = history.index.to_list()
        low = polified_close[lmin_close[-1]]
        high = polified_close[lmax_close[-1]]
        # 价格检验
        if x[-1] - 6 + 1 > lmin_close[-1]:
            return False # 倒数四天内没有极小值点
        if lmax_close[-1] > lmin_close[-1]:
            return False # 最后一个人极值点不是极小值点
        if lmin_close[-1] - lmax_close[-1] < 10:
            return False # 大小极值点之间间隔交易日不足
        if ((high - low) / high) * 100 < 10:
            return False # 跌幅不足
        
        priceAfterSpot = polified_close[lmin_close[-1]:]
        amountAfterSpot = polified_amount[lmin_close[-1]:]
        if mk_trend_detect(priceAfterSpot) != 1 or mk_trend_detect(amountAfterSpot) != 1:
            return False # 量价齐升检验失不通过
        if amountAfterSpot[-1] - amountAfterSpot[0] < amountAfterSpot[0]:
            return False # 升量不够

        return True
    except:
        return False



def getLpoint(ticker_df, name):
    polified_y = getPolifiedFromRaw(ticker_df, name)
    return get_lmin_lmax(polified_y)

def getPolifiedFromRaw(ticker_df, name):
    x_data = ticker_df.index.tolist()   
    y = ticker_df[name]
    x = np.linspace(0, max(ticker_df.index.tolist()), max(ticker_df.index.tolist()) + 1)
    return getPolifyValue(x_data, y, x, 12)

'''
检查是否是上升通道的股票
    线性拟合120天内收盘价的所有极大值点, 斜率为正，越大越强
    线性拟合120天内收盘价的所有极小值点, 斜率为正，越大越强
    二者同为真
'''
