'''
封装统计分析函数
'''
import numpy as np
#一元线性回归
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats


'''
以degree次多项式拟合离散数据点, 并返回拟合值
'''
def getPolifyValue(x_data, y_data, x, degree=17):
    pol = np.polyfit(x_data, y_data, degree)
    y_pol = np.polyval(pol, x)
    return y_pol

'''
传入多项式, 返回局部极值
'''
def get_lmin_lmax(data):
    l_min = (np.diff(np.sign(np.diff(data))) > 0).nonzero()[0] + 1      # 局部最小
    l_max = (np.diff(np.sign(np.diff(data))) < 0).nonzero()[0] + 1      # 局部最大
    return l_min, l_max


'''
线性拟合
'''
def linear_regression_and_display(x, y, no, cl=0.9):
    a, b, t_value, sigma, Sxx, evident = linear_regression(x, y, cl)
    print(a)
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.scatter(x,y,s=1,c='k',)
    ax.plot(x,a*x+b,lw=1,label='Linear regression')
    ax.fill_between(x, 
                    a*x+b - t_value*sigma*np.sqrt(1./len(x)+(x-np.mean(x))**2/Sxx), 
                    a*x+b + t_value*sigma*np.sqrt(1./len(x)+(x-np.mean(x))**2/Sxx), 
                    alpha=0.3,
                    label=r'Confidence limit'.format(100*cl))
    ax.set_xlabel('$x$')
    ax.set_ylabel('$y$')
    ax.legend()
    fig.savefig('Linear regression' + str(no) + '.png',dpi=300)


def linear_regression(x, y, cl=0.9):
    """
    linear regression函数y = ax + b
    cl为置信水平
    alpha为显著性水平
    """

    alpha = 1 - cl
    
    a, b = np.polyfit(x, y, deg=1)
    
    Sxx = np.sum((x-np.mean(x))**2)
    Syy = np.sum((y-np.mean(y))**2)
    Sxy = np.sum((x-np.mean(x))*(y-np.mean(y)))
    
    dof = len(x) - 2
    
    sigma = np.sqrt((Syy - a*Sxy)/dof)

    
    t_value = stats.t.isf(alpha/2, dof)
    
    if np.abs(a)/sigma*np.sqrt(Sxx) >= t_value:
        return a, b, t_value, sigma, Sxx, True
    else:
        return a, b, t_value, sigma, Sxx, False