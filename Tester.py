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
    history = getHistoryData(120, "002875")
    print(checkIf_sstd(history))