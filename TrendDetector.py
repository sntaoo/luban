from scipy.stats import norm, mstats
import numpy as np
from ShareDataLoader import *

'''
MK检验, 检测时序数据趋势
'''
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
    多项式拟合求极值
    收盘价：
    1. 倒数六天内有极值点且最后一个极点为极小值点
    2. 1中选出来的点和上一个极大值点之间的间隔交易日大于等于10
    3. 1, 2中的两个极点之间跌幅超过10%
    交易量：
    4. 1中交易日之后量价齐升高(低alpha MK检验)
    5. 最后一日的交易量为1中的点的两倍以上
'''
def isLowPriceLargeAmountIncrease(history_raw):
    try :
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


def getPolifiedFromRaw(ticker_df, name, degree=12):
    x_data = ticker_df.index.tolist()   
    y = ticker_df[name]
    x = np.linspace(0, max(ticker_df.index.tolist()), max(ticker_df.index.tolist()) + 1)
    return getPolifyValue(x_data, y, x, degree)

'''
检查是否是上升通道的股票
    必须交易超过60日以上
    近30个交易日内收盘价趋势为上升
    均线多头排列, 10日>20日>30日
    5日均线允许与10日线交叉, 但不能比10日线低超过5个百分点
'''
def checkIf_sstd(history_raw):
    tail_60 = history_raw.tail(60)
    if len(tail_60) < 60:
        return False
    result_60 = pd.DataFrame()
    result_60['5日均线'] = tail_60['收盘'].rolling(window=5).mean()
    result_60['10日均线'] = tail_60['收盘'].rolling(window=10).mean()
    result_60["20日均线"] = tail_60['收盘'].rolling(window=20).mean()
    result_60["30日均线"] = tail_60['收盘'].rolling(window=30).mean()
    result_60["收盘"] = tail_60['收盘']
    result = result_60.tail(30)
    # 检查均线是否多头并进，除了5日线外，其他线必须有严格的上下关系
    condition_met = (result['10日均线'] > result['20日均线']) & (result['20日均线'] > result['30日均线']) & (result['5日均线'] > 0.95 * result['10日均线'])
    if (not condition_met.all()):
        return False
    
    # 均线满足多头并进条件，MK检验检查近30个交易日的股价是否是上升趋势
    closing_price = result['收盘'].values
    return (mk_trend_detect(closing_price) == 1)


'''
涨停缩倍量用英文怎么写啊害
10个交易日内有涨停(>=1次)
今日成交量约为某个涨停日的一半(0.45到0.55之间)
当日涨停的成交量为其前5天成交量最低值的三倍以上, 且收盘大于开盘
今日收盘高于20日均线
需要保证在上升通道内调用, 否则可能会抛越界异常
'''
def checkIf_ztsbl(history):
    window = 10
    data = history.tail(window)
    if not any(data[data["涨跌幅"] >= 9.7]):
        return False
    
    closing_mean_last_20 = data['收盘'].tail(20).mean()
    if data.iloc[-1]['收盘'] < closing_mean_last_20:
        return False
    
    zhang_ting = data.loc[data["涨跌幅"] > 9.7].copy()
    zhang_ting['5日内最小成交量'] = 0.0
    for ind in zhang_ting.index:
        left, right = ind - 5, ind - 1
        min_amount = history.loc[left:right, '成交量'].min()
        zhang_ting.at[ind, '5日内最小成交量'] = min_amount
    
    condition_met = (zhang_ting['收盘'] > zhang_ting['开盘']) & (zhang_ting['成交量'] > 3 * zhang_ting['5日内最小成交量'])
    satisfied_zhangting = zhang_ting[condition_met]
    amount_today = data.iloc[-1]['成交量']
    condition_success = (amount_today < satisfied_zhangting['成交量'] * 0.55) & (amount_today > satisfied_zhangting['成交量'] * 0.45)
    return any(satisfied_zhangting[condition_success])