import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from churn_data_analysis.draw_time_sequence_chart import dbHandle
import datetime
import torch
import statsmodels.api as sm
from statsmodels.tsa.api import VAR
from statsmodels.tsa.statespace.varmax import VARMAX

from darts.dataprocessing.transformers import Scaler
from sklearn.preprocessing import MinMaxScaler

import os
from darts import TimeSeries
from darts.metrics import mape, smape
from darts.models.forecasting.varima import VARIMA

torch.manual_seed(1); np.random.seed(1)  # for reproducibility


fmt_day = '%Y-%m-%d'
fmt_second = '%Y-%m-%d %H:%M:%S'

# 使用darts中的VARIMA实现VAR预测
# p: 滞后阶数
# trend: 趋势，{‘n’,’c’,’t’,’ct’}
# divide_point: 预测划分时间点，如果是小数则按比例划分，否则按下标
# predict_length:预测时间段长度
def darts_var(time_index, data_frame, p=1, trend='c',divide_point=0.8,predict_length=12):
    series = TimeSeries.from_times_and_values(time_index, data_frame)
    # print(series)
    object_series = TimeSeries.from_times_and_values(time_index,data_frame.iloc[:,[-1]])

    ################scaler test##############################################
    # scaler = MinMaxScaler(feature_range=(0, 1))
    # transformer = Scaler(scaler)
    # series = transformer.fit_transform(series)
    ################scaler test##############################################

    if divide_point > 0 and divide_point < 1:
        divide_point = int(len(series)*divide_point)
    train = series[:divide_point]

    var_model = VARIMA(p=p,trend=trend)
    var_model.fit(train)

    preds = var_model.predict(predict_length)

    ################scaler test##############################################
    # preds = transformer.inverse_transform(preds)
    ################scaler test##############################################

    plt.figure(figsize=(10,5))
    pred = TimeSeries.from_times_and_values(time_index[divide_point:divide_point+predict_length],preds.pd_dataframe().iloc[:,[-1]])
    var = object_series[divide_point:divide_point+predict_length]
    print(pred)
    print(series[divide_point:])
    object_series.plot(label='actual')
    pred.plot(label='forecast')
    plt.legend()
    plt.show()
    print('MAPE = {:.2f}%'.format(mape(var, pred)))


def stats_var(time_index, data_frame, p=1, trend='c',divide_point=0.8,predict_length=12):
    series = pd.Series(data_frame.values.tolist(),index=time_index)
    if divide_point > 0 and divide_point < 1:
        divide_point = int(len(series)*divide_point)
    train = data_frame[:divide_point]

    data_list = []
    for item in data_frame.iloc[:,[-1]].values.tolist():
        data_list.append(item[0])

    object_series = pd.Series(data_list,index=time_index)

    model = VARMAX(train,order=(p,0),trend=trend)
    model_fit = model.fit(disp=False)
    preds = model_fit.forecast(steps=predict_length)

    pred_data_list = []
    for item in preds.iloc[:,[-1]].values.tolist():
        pred_data_list.append(item[0])
    print(pred_data_list)#################################33
    pred_series = pd.Series(pred_data_list,index=time_index[divide_point:divide_point + predict_length])

    plt.figure(figsize=(10, 5))
    object_series.plot()
    pred_series.plot()
    plt.legend()
    plt.show()

    var = TimeSeries.from_series(object_series[divide_point:divide_point + predict_length])
    pred = TimeSeries.from_series(pred_series)
    print('MAPE = {:.2f}%'.format(mape(var, pred)))


def test_darts_var(id):
    filenames = os.listdir(r'E:\bysj_project\granger_causality_test\data_28_start')
    id_filenames = dict()
    for filename in filenames:
        id_filenames[int(filename.split('_')[0])] = filename
    data_filename = 'E:/bysj_project/granger_causality_test/data_28_start/'+id_filenames[id]
    granger_result_filename = 'E:/bysj_project/granger_results/data_28_start/'+id_filenames[id]

    pred_index = 47
    churn_rate_col_name = pd.read_csv(data_filename).columns.to_list()[-2]

    cause_cols = [churn_rate_col_name]
    '''cause_cols = [
        'repo_issue',
        'repo_pull',
        'repo_commit',
        'repo_review',
        'repo_issue_comment',
        'repo_review_comment'
    ]'''
    with open(granger_result_filename, 'r', encoding='utf-8')as f:
        f.readline()
        for line in f.readlines():
            col = line.split(',')[0]
            value = line.split(',')[1]
            if value == 'cause and effect' or value == 'effect':
                cause_cols.append(col)
    f.close()
    print(cause_cols)

    # other_data_frames = []
    # for col in cause_cols:
    #     other_data_frames.append(pd.read_csv(data_filename, usecols=[col]))
    data_frame = pd.read_csv(data_filename,usecols=cause_cols)
    print(data_frame)

    step = 28
    id = 2
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select repo_id,created_at from churn_search_repos_final where id = ' + str(id))
    result = cursor.fetchone()
    create_time = result[1][0:10]
    end_time = '2022-01-01'

    skip_days = int(pd.read_csv(data_filename, usecols=[0]).loc[0]) + step
    # print(skip_days)
    start_time = (datetime.datetime.strptime(create_time, fmt_day) + datetime.timedelta(days=skip_days)).strftime(
        fmt_day)

    var = VAR(data_frame)
    print(var.select_order())

    time_index = pd.date_range(start=start_time, end=end_time, freq=str(step) + 'D')
    darts_var(time_index,data_frame,p=9,trend='c',divide_point=-24,predict_length=12)


def test_stats_var(id):
    filenames = os.listdir(r'E:\bysj_project\granger_causality_test\data_28_start')
    id_filenames = dict()
    for filename in filenames:
        id_filenames[int(filename.split('_')[0])] = filename
    data_filename = 'E:/bysj_project/granger_causality_test/data_28_start/'+id_filenames[id]
    granger_result_filename = 'E:/bysj_project/granger_results/data_28_start/'+id_filenames[id]

    pred_index = 47
    churn_rate_col_name = pd.read_csv(data_filename).columns.to_list()[-2]

    cause_cols = [churn_rate_col_name]
    '''cause_cols = [
        'repo_issue',
        'repo_pull',
        'repo_commit',
        'repo_review',
        'repo_issue_comment',
        'repo_review_comment'
    ]'''
    with open(granger_result_filename, 'r', encoding='utf-8')as f:
        f.readline()
        for line in f.readlines():
            col = line.split(',')[0]
            value = line.split(',')[1]
            if value == 'cause and effect' or value == 'effect':
                cause_cols.append(col)
    f.close()
    print(cause_cols)

    # other_data_frames = []
    # for col in cause_cols:
    #     other_data_frames.append(pd.read_csv(data_filename, usecols=[col]))
    data_frame = pd.read_csv(data_filename,usecols=cause_cols)
    print(data_frame)

    step = 28
    id = 2
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select repo_id,created_at from churn_search_repos_final where id = ' + str(id))
    result = cursor.fetchone()
    create_time = result[1][0:10]
    end_time = '2022-01-01'

    skip_days = int(pd.read_csv(data_filename, usecols=[0]).loc[0]) + step
    # print(skip_days)
    start_time = (datetime.datetime.strptime(create_time, fmt_day) + datetime.timedelta(days=skip_days)).strftime(
        fmt_day)

    divide_point = -24

    var = VAR(data_frame)#[:divide_point]
    order = var.select_order()
    print(order)

    time_index = pd.date_range(start=start_time, end=end_time, freq=str(step) + 'D')

    stats_var(time_index,data_frame,p=9,trend='c',divide_point=divide_point,predict_length=12)




if __name__ == '__main__':
    test_darts_var(2)
    # test_stats_var(2)