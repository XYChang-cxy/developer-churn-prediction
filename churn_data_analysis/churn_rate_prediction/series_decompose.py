# 通过移动平均或STL进行时间序列的季节性分解
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.seasonal import STL
import matplotlib.pyplot as plt
import pandas as pd
from churn_data_analysis.churn_rate_prediction.nbeats_prediction import getTimeData


# method: 'MA'或'STL'
# model: additive 或 multiplicative
def decomposeSeries(series,method='MA',model='additive',period=13,if_draw=False):
    if method == 'MA':
        res = seasonal_decompose(series,model=model,period=period)
    else: # method = 'STL'
        res = STL(series,seasonal=7,period=period).fit()#

    if if_draw:
        series.plot(figsize=(6,3))
        res.trend.plot()
        plt.show()
    return res.trend


if __name__ == '__main__':
    id = 2

    ret = getTimeData(id, 0)
    time_index = ret[0]
    all_data_frame = ret[1]
    col_names = ret[2]
    churn_rate_order = ret[3]

    start_point = 0  # 10
    origin_df = all_data_frame.iloc[start_point:, [-1]]
    series = pd.Series(origin_df.iloc[:,0].values,time_index[start_point:])  ########### df.iloc[:,0].values
    # print(series)

    decomposeSeries(series,method='MA',period=6,if_draw=True)