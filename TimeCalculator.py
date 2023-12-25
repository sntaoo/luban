import datetime

def getTodayDate():
    return "20" + datetime.date.today().__format__("%y%m%d")

def getYesterdayDate():
    oneday = datetime.timedelta(days=1) 
    today = datetime.date.today()
    yesterday = today - oneday
    return "20" + yesterday.__format__("%y%m%d")

# 获取bias天前的日期
def getDateWithBias(bias):
    today = datetime.date.today()
    days = datetime.timedelta(days=bias)
    return "20" + (today - days).__format__("%y%m%d") 