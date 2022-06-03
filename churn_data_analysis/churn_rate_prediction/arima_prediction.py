import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from churn_data_analysis.draw_time_sequence_chart import dbHandle
import datetime
import torch
import os
import time

from darts import TimeSeries
from darts.metrics import mse, rmse, mae, mape, smape, mase
from darts.models import ARIMA as ARIME_darts
from darts.dataprocessing.transformers import Scaler
from sklearn.preprocessing import MinMaxScaler
from churn_data_analysis.churn_rate_prediction.nbeats_prediction import getTimeData
from churn_data_analysis.Granger_causality_test import adfTest
from churn_data_analysis.churn_rate_prediction.series_decompose import *

from statsmodels.graphics.tsaplots import plot_acf,plot_pacf  # 自相关图，偏自相关图
from statsmodels.tsa.stattools import adfuller  # ADF检验
from statsmodels.stats.diagnostic import acorr_ljungbox  # LB白噪声检验
import statsmodels.api as sm  # 一阶自相关检验
from statsmodels.graphics.api import qqplot  # Q-Q图
from statsmodels.tsa.arima.model import ARIMA  # ARIMA模型


from matplotlib.pylab import style
# style.use('ggplot')

plt.rcParams['font.sans-serif']=['Simhei']
plt.rcParams['axes.unicode_minus']=False

fmt_day = '%Y-%m-%d'
fmt_second = '%Y-%m-%d %H:%M:%S'

torch.manual_seed(1);np.random.seed(1)  # for reproducibility

#显示所有列
pd.set_option('display.max_columns', None)
#显示所有行
pd.set_option('display.max_rows',None)


def part_2(churn_rate_df):
    # 2.1 绘制时序图
    churn_rate_df.plot(figsize=(8, 3),color='limegreen')
    plt.show()
    # 2.2 绘制自相关系数图，自相关性是指总体回归模型的误差项ui之间存在相关关系
    plt.figure(figsize=(8, 5))
    plot_acf(churn_rate_df,lags=int(churn_rate_df.shape[0]/2),color='b').show()
    qqplot(churn_rate_df,line='q',fit=True).show()
    # 2.3 单位根检验
    ret = adfTest(churn_rate_df)
    if ret[0] == 0:
        print('经ADF检验，是平稳序列，p=' + "{0:.4f}".format(ret[1]))
    else:
        print('经ADF检验，不是平稳序列，p=' + "{0:.4f}".format(ret[1]))


def part_3(churn_rate_df):
    # LB检验：LB检验可同时用于时间序列以及时序模型的残差是否存在自相关性（是否为白噪声）
    ret = acorr_ljungbox(churn_rate_df)
    print('序列的白噪声检验结果为:',ret)
    plt.figure(figsize=(8,5))
    plt.plot(ret.iloc[:,[1]])
    plt.show()


def part_4_1(churn_rate_df):
    # 4.1 人工识图
    plot_acf(churn_rate_df,lags=int(churn_rate_df.shape[0]/2)).show()
    plot_pacf(churn_rate_df, lags=int(churn_rate_df.shape[0]/2)-5).show()
    # 2号仓库：ACF 7阶截尾，PACF 为拖尾（用MA模型拟合更好）

def part_4_2(churn_rate_df):
    # 4.2参数调优
    pmax = int(churn_rate_df.shape[0]/10) # p和q的阶数一般不超过样本量/10
    qmax = pmax
    # print(pmax,qmax)
    aic_matrix = []
    bic_matrix = []
    hqic_matrix = []
    for p in range(pmax+1):
        tmp1 = []
        tmp2 = []
        tmp3 = []
        for q in range(qmax + 1):
            print(p,q)
            try:
                r = ARIMA(churn_rate_df,order=(p,0,q)).fit()
                # print(r.summary())
                tmp1.append(r.aic)
                tmp2.append(r.bic)
                tmp3.append(r.hqic)
            except BaseException as e:
                print(e)
                tmp1.append(None)
                tmp2.append(None)
                tmp3.append(None)
        aic_matrix.append(tmp1)
        bic_matrix.append(tmp2)
        hqic_matrix.append(tmp3)
    aic_matrix = pd.DataFrame(aic_matrix)
    bic_matrix = pd.DataFrame(bic_matrix)
    hqic_matrix = pd.DataFrame(hqic_matrix)
    print(aic_matrix)
    print(bic_matrix)
    print(hqic_matrix)
    dir = 'ARIMA_p_q'
    aic_matrix.to_csv(dir+'\\'+'aic_matrix.csv')
    bic_matrix.to_csv(dir + '\\' + 'bic_matrix.csv')
    hqic_matrix.to_csv(dir + '\\' + 'hqic_matrix.csv')
    p, q = aic_matrix.stack().idxmin()
    print('AIC准则下参数p,q分别为：', p, q)
    p,q = bic_matrix.stack().idxmin()
    print('BIC准则下参数p,q分别为：',p,q)
    p, q = hqic_matrix.stack().idxmin()
    print('HQIC准则下参数p,q分别为：', p, q)


def part_5_1(churn_rate_df,resid):
    # 残差白噪声检验（ACF、PACF、Q-Q图）
    resid.plot(figsize=(8, 3))
    plt.show()
    plot_acf(resid, lags=int(churn_rate_df.shape[0]/2)).show()
    plot_pacf(resid, lags=int(resid.shape[0]/2)-5).show()
    # 如果ACF和PACF两图都零阶截尾，这说明模型拟合良好
    qqplot(resid,line='q',fit=True).show()
    # QQ图：残差服从正态分布，均值为0，方差为常数

def part_5_2(resid):
    # 残差白噪声检验：D-W检验,检验一阶自相关性
    print('D-W检验的结果为：',sm.stats.durbin_watson(resid.values))
    # 对于样本量100，解释变量数1，du=1.69,即1.69~2.31范围内不存在相关关系

    # 白噪声检验：LB检验
    ret = acorr_ljungbox(resid)
    print('残差序列的白噪声检验（LB检验）结果为:\n', ret)
    # p值大于0.05则是白噪声
    plt.figure(figsize=(8, 5))
    plt.plot(ret.iloc[:, [1]])
    plt.show()


def part_6():
    predictions_in = model.predict(time_index[start_point], time_index[divide_point-1])
    predictions_out = model.predict(time_index[divide_point], time_index[-1])
    origin_df.plot(figsize=(6, 3))
    predictions_in.plot()
    predictions_out.plot()
    plt.show()

    predictions = predictions_in.append(predictions_out)
    trend = decomposeSeries(predictions,method='STL',period=6)
    trend_1 = trend[:divide_point-start_point]
    trend_2 = trend[divide_point-start_point-1:]

    origin_trend = decomposeSeries(origin_df,method='STL',period=6)
    origin_trend.plot(figsize=(6, 3))
    trend_1.plot()
    trend_2.plot()
    plt.show()



if __name__ == '__main__':
    id = 2
    # 1. 获取数据
    ret = getTimeData(id, 0)
    time_index = ret[0]
    all_data_frame = ret[1]
    col_names = ret[2]
    churn_rate_order = ret[3]
    if churn_rate_order > 0:
        print('churn rate order:',churn_rate_order)
    all_data_frame.index=time_index
    # print(all_data_frame)
    divide_point = len(time_index)-36
    start_point = 2  # 10
    origin_df = all_data_frame.iloc[start_point:,[-1]]
    churn_rate_df = all_data_frame.iloc[start_point:divide_point,[-1]]
    # print(churn_rate_df)

    # 2. 原始序列的检验
    # part_2(churn_rate_df)

    # 3. 平稳序列（原序列或一阶差分序列）的白噪声检验，如果该序列是白噪声序列，则终止建模
    # part_3(churn_rate_df)

    # 4. 定阶，选取参数p q
    # part_4_1(churn_rate_df)  # 根据acf和pacf, p=0 q=7
    # part_4_2(churn_rate_df)  #2-- AIC:5 4; BIC:0 0; HQIC: 2 2 #10-- AIC:4 5; BIC:0 0; HQIC: 1 1

    # 5. 建模及残差检验(检验残差是否为白噪声）
    p = 4
    q = 5
    model = ARIMA(churn_rate_df,order=(p,0,q)).fit()
    # print(model.summary())
    resid = model.resid
    # part_5_1(churn_rate_df,resid)
    # part_5_2(resid)

    # 6. 预测
    part_6()


