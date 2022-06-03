from churn_data_analysis.churn_rate_prediction.series_decompose import *
from churn_data_analysis.churn_rate_prediction.arima_prediction import part_2,part_3,part_4_1,\
    part_4_2,part_5_1,part_5_2,adfTest,ARIMA


def part_2_1(trend_series,diff_series):
    print(adfTest(diff_series))
    trend_series.plot(label='original', figsize=(6, 3))
    diff_series.plot(label='1-diff')
    plt.legend(loc='upper right')
    plt.show()


def part_6_diff(model,start_point,divide_point,trend_series,time_index):
    predictions_in = model.predict(time_index[start_point], time_index[divide_point-1])
    predictions_out = model.predict(time_index[divide_point], time_index[-1])
    trend_series.plot(figsize=(6, 3))

    predictions_in = predictions_in.cumsum()+trend_series[start_point-1]
    predictions_in[time_index[start_point-1]]=trend_series[start_point-1]
    predictions_in = predictions_in.sort_index()

    predictions_out = predictions_out.cumsum()+trend_series[divide_point-1]

    predictions_in.plot()
    predictions_out.plot()
    plt.show()


def main1():
    id = 2

    ret = getTimeData(id, 0)
    time_index = ret[0]
    all_data_frame = ret[1]
    col_names = ret[2]
    churn_rate_order = ret[3]

    start_point = 0  # 10
    divide_point = len(time_index) - 36
    origin_df = all_data_frame.iloc[start_point:, [-1]]
    series = pd.Series(origin_df.iloc[:, 0].values, time_index[start_point:])

    trend_series = decomposeSeries(series, method='STL', period=6)

    # print(type(trend_series))

    # 2. 原始序列的检验
    # part_2(trend_series)

    # 不是平稳序列，要一阶差分，d=1
    diff_series = trend_series.diff(periods=1).dropna()
    # part_2_1(trend_series,diff_series)

    # 3. 平稳序列（原序列或一阶差分序列）的白噪声检验，如果该序列是白噪声序列，则终止建模
    # part_3(diff_series)

    # 4. 定阶，选取参数p q
    # part_4_1(diff_series)  # acf 3阶截尾，pacf拖尾，p=0,q=3
    # part_4_2(diff_series)
    # AIC准则下参数p, q分别为： 0, 9
    # BIC准则下参数p, q分别为： 1, 5
    # HQIC准则下参数p, q分别为： 0, 9

    # 5. 建模及残差检验(检验残差是否为白噪声）
    p = 0
    q = 9
    d = 1
    model = ARIMA(diff_series, order=(p, d, q)).fit()
    # print(model.summary())
    resid = model.resid
    # part_5_1(trend_series,resid)
    # part_5_2(resid)

    # 6. 预测
    # part_6_diff(model,start_point+1,-1,trend_series,time_index) # 全段拟合


def main2():
    id = 2

    ret = getTimeData(id, 0)
    time_index = ret[0]
    all_data_frame = ret[1]
    col_names = ret[2]
    churn_rate_order = ret[3]

    start_point = 0  # 10
    divide_point = len(time_index) - 36
    origin_df = all_data_frame.iloc[start_point:, [-1]]
    series = pd.Series(origin_df.iloc[:, 0].values, time_index[start_point:])

    trend_series = decomposeSeries(series, method='STL', period=6)
    part_trend_series = trend_series[start_point:divide_point]

    # print(type(trend_series))

    # 2. 原始序列的检验
    # part_2(part_trend_series)

    # 不是平稳序列，要一阶差分，d=1
    part_diff_series = part_trend_series.diff(periods=1).dropna()
    # part_2_1(part_diff_series,part_diff_series)

    # 3. 平稳序列（原序列或一阶差分序列）的白噪声检验，如果该序列是白噪声序列，则终止建模
    # part_3(part_diff_series)

    # 4. 定阶，选取参数p q
    # part_4_1(part_diff_series)  # acf 3阶截尾，pacf拖尾，p=0,q=3
    # part_4_2(part_diff_series)
    # AIC准则下参数p, q分别为： 1, 5
    # BIC准则下参数p, q分别为： 2, 0
    # HQIC准则下参数p, q分别为： 2, 0

    # 5. 建模及残差检验(检验残差是否为白噪声）
    p = 1
    q = 5
    d = 1
    model = ARIMA(part_diff_series, order=(p, d, q)).fit()
    # print(model.summary())
    resid = model.resid
    # part_5_1(part_trend_series,resid)
    # part_5_2(resid)

    # 6. 预测
    part_6_diff(model, start_point + 1, divide_point, trend_series, time_index)


if __name__ == '__main__':
    main2()
