from ShareDataLoader import getHistoryData
from TrendDetector import *
import akshare as ak

def selectGoodStock(stocks):
    good_stock = []
    for index, row in stocks.iterrows():
        code = row["代码"]
        name = row["名称"]
        if isLowPriceLargeAmountIncrease(code):
            good_stock.append({"代码":code, "名称":name, "原因":"低位放量涨"})
    return good_stock
 
 
if __name__ == '__main__':
    stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
    stock_cy_a_spot_em_df = ak.stock_cy_a_spot_em() # 创业板数据
    # 过滤创业板数据
    filtered_share = stock_zh_a_spot_em_df[~stock_zh_a_spot_em_df["代码"].isin(stock_cy_a_spot_em_df["代码"])]
    # 过滤ST股
    filtered_share = filtered_share[~filtered_share["名称"].str.contains('ST|st')]
    stocks = filtered_share[["代码", "名称"]]
    good_stock = selectGoodStock(stocks)
    print(good_stock)



