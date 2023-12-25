from ShareDataLoader import getHistoryData, display
from ShareSelecter import selectGoodStock
from TrendDetector import *

import akshare as ak
from Analytics import *

def testDraw(code):
    history_raw = getHistoryData(120, code)
    history = history_raw[["日期", "开盘", "收盘", "最高", "最低", "成交量"]]
    display(history)


def testSelect():
    stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
    stocks = stock_zh_a_spot_em_df[["代码", "名称"]]
    selectGoodStock(stocks)

def testIsLowPriceLargeAmountIncrease(code):
    print(isLowPriceLargeAmountIncrease(code))



if __name__ == '__main__':
    # testDraw("601600")
    x = np.array([100,110,120,130,140,150,160,170,180,190])
    y = np.array([45,51,54,61,66,70,74,78,85,89])

    history_raw = getHistoryData(120, code)
    history = history_raw[["收盘", "成交量"]]
    polified_close = getPolifiedFromRaw(history, "收盘")
    polified_amount = getPolifiedFromRaw(history, "成交量")
    lmin_close, lmax_close = get_lmin_lmax(polified_close)