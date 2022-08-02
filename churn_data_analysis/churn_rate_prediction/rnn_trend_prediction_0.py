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
from darts.models import RNNModel
from darts.dataprocessing.transformers import Scaler
from sklearn.preprocessing import MinMaxScaler
from churn_data_analysis.churn_rate_prediction.nbeats_prediction import getTimeData
from churn_data_analysis.churn_rate_prediction.series_decompose import *

fmt_day = '%Y-%m-%d'
fmt_second = '%Y-%m-%d %H:%M:%S'

torch.manual_seed(1);np.random.seed(1)  # for reproducibility


# divide_point: 预测划分时间点，如果是小数则按比例划分，否则按下标
# predict_length:预测时间段长度
# variate_mode: 0--单变量预测;1--多变量预测;2--多时间序列(series list)预测
# model: 'RNN'/'LSTM'/'GRU'
# training_length: 必须大于input_chunk_length
# scalered: 是否对数据进行标准化处理，默认为True;多变量时建议标准化
def darts_rnnmodel(repo_id,time_index, data_frame,col_names, divide_point=-12, predict_length=12,
                   model_str='RNN',input_chunk_length=12,hidden_dim=25, n_rnn_layers=1,lr=1e-3,
                   dropout=0.0, training_length=24,n_epochs=100,batch_size=32,log_tensorboard=True,
                   work_dir='rnn_work_dir',fig_dir='',
                   variate_mode=0,save_model=False,scalered=True):
    '''time_index_0 = time_index.copy()
    data_frame_0 = data_frame.copy()
    data_frame_trend = decomposeSeries(data_frame.iloc[:,-1],'STL',period=6)

    time_index = time_index[1:]
    data_frame = data_frame_trend.diff(periods=1).dropna()'''

    if divide_point > 0 and divide_point <1:
        divide_point = int(len(time_index)*divide_point)
    elif divide_point < 0:
        divide_point += len(time_index)
    if divide_point + predict_length > len(time_index):
        predict_length = len(time_index)-1-divide_point

    while training_length <= input_chunk_length:
        if input_chunk_length >= 6:
            input_chunk_length = int(input_chunk_length/2)
        else:
            training_length *= 2

    scaler0 = MinMaxScaler(feature_range=(0, 1))
    transformer0 = Scaler(scaler0)
    scaler1 = MinMaxScaler(feature_range=(0, 1))
    transformer1 = Scaler(scaler1)
    scaler2 = MinMaxScaler(feature_range=(0, 1))
    transformer2 = Scaler(scaler2)

    # variate_mode=2: multiple time series
    '''series_list = []
    for i in range(data_frame.shape[1]):
        series = TimeSeries.from_times_and_values(time_index, data_frame.iloc[:, [i]])
        series_list.append(series)
    if scalered:  # 数据标准化
        series_list = transformer2.fit_transform(series_list)'''

    # chun rate series(variate_mode=0)
    target_series = TimeSeries.from_times_and_values(time_index, data_frame.iloc[:, [-1]])
    target_trend_series = decomposeSeries(target_series.pd_series(),'STL',period=6)
    diff_target_trend = target_trend_series.diff(periods=1).dropna()
    target_trend_series = TimeSeries.from_series(target_trend_series)
    diff_target_trend = TimeSeries.from_series(diff_target_trend)

    if scalered:
        uni_diff = transformer0.fit_transform(diff_target_trend)
    else:
        uni_diff = diff_target_trend
    train, val = uni_diff[:divide_point], uni_diff[divide_point:divide_point + predict_length]

    # variate_mode=1:multivariate
    multi_series = TimeSeries.from_times_and_values(time_index, data_frame)
    if scalered:
        multi_series = transformer1.fit_transform(multi_series)
    train_multi, val_multi = multi_series[:divide_point], multi_series[divide_point:divide_point + predict_length]

    train_list = []
    val_list = []

    # print(target_trend_series.pd_series().loc[target_trend_series.pd_series().index[0]])

    model = RNNModel(
        model=model_str,# 'RNN','LSTM','GRU'
        input_chunk_length=input_chunk_length,
        n_epochs=n_epochs,
        batch_size=batch_size,
        work_dir=work_dir,
        optimizer_kwargs={"lr": lr},
        log_tensorboard=log_tensorboard,
        hidden_dim=hidden_dim,
        n_rnn_layers=n_rnn_layers,
        dropout=dropout,
        training_length=training_length,
        force_reset=True,
        # random_state=42
    )
    if variate_mode==0:  # 单变量预测
        model.fit(train,verbose=True)
        # pred = model.predict(n=predict_length)
        his_pred = model.historical_forecasts(
            train,
            start=input_chunk_length,
            forecast_horizon=6,
            retrain=False,
            verbose=True,
        )
        pred = model.historical_forecasts(
            uni_diff,
            start=divide_point - 6,
            forecast_horizon=6,
            retrain=False,
            verbose=True,
        )
        if scalered:
            his_pred = transformer0.inverse_transform(his_pred)
            pred = transformer0.inverse_transform(pred)
    elif variate_mode==1:
        model.fit(train_multi, verbose=True)
        preds = model.predict(n=predict_length)

        if scalered:
            preds = transformer1.inverse_transform(preds)

        pred = TimeSeries.from_times_and_values(time_index[divide_point:divide_point+predict_length],
                         preds.pd_dataframe().iloc[:,-1])
    else:
        pass
        '''for series in series_list:
            train_list.append(series[:divide_point])
            val_list.append(series[divide_point:divide_point + predict_length])
        model.fit(train_list,verbose=True)
        if scalered:
            pred_list = model.predict(n=predict_length,series=train_list)
            pred = transformer2.inverse_transform(pred_list)[-1]
        else:
            pred=model.predict(n=predict_length,series=train)'''

    plt.figure(figsize=(6,3))
    # target_series.plot(label='actual',linewidth=1.5)
    # diff_target_trend.plot(label='actual diff',linewidth=1.5)
    target_trend_series.plot(label='actural',linewidth=1.5)
    print(target_trend_series.pd_series().index[len(target_trend_series)-len(his_pred)-len(pred)],
          his_pred.pd_series().index[0])
    print(target_trend_series.pd_series().index[divide_point-1],
          pred.pd_series().index[0])

    his_pred = his_pred.pd_series().cumsum()+\
               target_trend_series.pd_series()[len(target_trend_series)-len(his_pred)-len(pred)]
    pred = pred.pd_series()[1:].cumsum()+target_trend_series.pd_series()[divide_point-1]

    his_pred.plot(label='historical forecasts', linewidth=1.5)
    pred.plot(label='forecast',linewidth=1.5)
    plt.legend()
    if fig_dir!='':
        plt.savefig(fig_dir + '\\' + time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime()) + '_' + model_str + '_' +
                    str(variate_mode) + '.png', dpi=300, bbox_inches='tight')
    plt.show()
    print('MAPE = {:.2f}%'.format(mape(target_series, pred)))
    print('MSE = {:.2f}'.format(mse(target_series, pred)))
    print('RMSE = {:.2f}'.format(rmse(target_series, pred)))
    print('MAE = {:.2f}'.format(mae(target_series, pred)))
    print('sMAPE = {:.2f}%'.format(smape(target_series, pred)))

    if variate_mode==0:
        model_filename = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime()) + 'univariate_model.pth.tar'
    elif variate_mode == 1:
        model_filename = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime()) + 'multivariate_model.pth.tar'
    else:
        model_filename = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime()) + 'multi_series_model.pth.tar'
    if save_model:
        model.save_model('rnn_models/' + model_filename)



def get_best_rnnmodel(repo_id,time_index, data_frame,col_names, divide_point=-12, predict_length=12,
                      model_str='RNN',work_dir='rnn_work_dir',variate_mode=0,scalered=True,fig_dir=''):
    if divide_point > 0 and divide_point <1:
        divide_point = int(len(time_index)*divide_point)
    elif divide_point < 0:
        divide_point += len(time_index)
    if divide_point + predict_length > len(time_index):
        predict_length = len(time_index)-1-divide_point

    scaler0 = MinMaxScaler(feature_range=(0, 1))
    transformer0 = Scaler(scaler0)
    scaler1 = MinMaxScaler(feature_range=(0, 1))
    transformer1 = Scaler(scaler1)
    scaler2 = MinMaxScaler(feature_range=(0, 1))
    transformer2 = Scaler(scaler2)

    # variate_mode=2: multiple time series
    series_list = []
    for i in range(data_frame.shape[1]):
        series = TimeSeries.from_times_and_values(time_index, data_frame.iloc[:, [i]])
        series_list.append(series)
    if scalered:  # 数据标准化
        series_list = transformer2.fit_transform(series_list)

    # chun rate series(variate_mode=0)
    target_series = TimeSeries.from_times_and_values(time_index, data_frame.iloc[:, [-1]])
    if scalered:
        uni_series = transformer0.fit_transform(target_series)
    else:
        uni_series = target_series
    train, val = uni_series[:divide_point], uni_series[divide_point:divide_point + predict_length]

    # variate_mode=1:multivariate
    multi_series = TimeSeries.from_times_and_values(time_index, data_frame)
    if scalered:
        multi_series = transformer1.fit_transform(multi_series)
    train_multi, val_multi = multi_series[:divide_point], multi_series[divide_point:divide_point + predict_length]

    train_list = []
    val_list = []

    model = RNNModel(model=model_str,input_chunk_length=24)

    if variate_mode == 0:  # 单变量预测
        parameters = {
            'model':[model_str],
            'input_chunk_length':[24],#[6,12,24,36],#
            'optimizer_kwargs':[{"lr": 1e-2}],  #[{"lr": 0.05}, {"lr": 1e-2}, {"lr": 1e-3}],#
            'n_epochs':[300],#[200,300,400,500,600],#[300],#
            'batch_size':[32],#[16,32,64],
            'work_dir':[work_dir],
            'hidden_dim': [25],#[20,25,30],  # RNN隐藏层特征映射大小
            'n_rnn_layers': [4],#[1,2,3,4,5],  # 递归层的个数
            'dropout':[0.1],#[0.0,0.1,0.2,0.3],#[0.2],#
            'training_length': [24],#[20, 24, 28]
        }
        # # random_state=42,0

        best_model, best_parameter, metric_value = model.gridsearch(
            parameters=parameters,
            series=train,
            start=0.6,  # 开始评估模型的划分点，默认0.5
            # forecast_horizon=6,  # 使用该参数时，是expanding window mode，速度慢，所有参数都要重新训练模型
            val_series=val,  # 使用该参数时，是split window mode，用验证集来评估
            # use_fitted_values=True,  # 该参数为True时，是fitted value mode，速度快，但可能过拟合
            metric=mape,  # 模型评估指标,默认MAPE
            verbose=True
        )

        model_filename = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())+'_'+model_str+'_model.pth.tar'
        best_model.save_model('rnn_models/'+model_filename)
        print(best_parameter)
        print('GridSearch metric value:',metric_value)

        best_model.fit(train,verbose=True)
        pred = best_model.predict(n=predict_length)
        if scalered:
            pred = transformer0.inverse_transform(pred)
    elif variate_mode==1:
        parameters = {#################################3
            'model': [model_str],
            'input_chunk_length': [36],  # [6, 12, 24, 36],
            'optimizer_kwargs': [{"lr": 0.1}],  # [{"lr": 0.1}, {"lr": 1e-2}, {"lr": 1e-3}],
            'n_rnn_layers': [3],  # [1,2,3,4,5],  # 递归层的个数
            'dropout': [0.0],  # [0.0,0.1,0.2,0.3],
            'batch_size': [32, 64],  # [16,32,64],
            'n_epochs': [200, 400, 600, 800],  # [100, 200, 300, 400, 500],
            'work_dir': [work_dir],
            # 'hidden_dim': [20,25,30],  # RNN隐藏层特征映射大小
            # 'training_length':[]
        }
        '''parameters = {
            'model': [model_str],
            'input_chunk_length': [36],#[6, 12, 24, 36],
            'optimizer_kwargs':  [{"lr": 0.1},{"lr": 1e-2}],#[{"lr": 0.1}, {"lr": 1e-2}, {"lr": 1e-3}],
            'n_rnn_layers': [3],#[1,2,3,4,5],  # 递归层的个数
            'dropout':[0.0],#[0.0,0.1,0.2,0.3],
            'batch_size':[16,32,64],#[16,32,64],
            'n_epochs': [200,400,600,800],#[100, 200, 300, 400, 500],
            'work_dir':[work_dir],
            # 'hidden_dim': [20,25,30],  # RNN隐藏层特征映射大小
            # 'training_length':[]
        }'''

        best_model, best_parameter, metric_value = model.gridsearch(
            parameters=parameters,
            series=train_multi,
            start=0.6,  # 开始评估模型的划分点，默认0.5
            val_series=val_multi,  # 使用该参数时，是split window mode，用验证集来评估
            metric=mape,  # 模型评估指标,默认MAPE
            verbose=True
        )

        model_filename = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime()) +'_'+model_str+'_multi_model.pth.tar'
        best_model.save_model('rnn_models/' + model_filename)
        print(best_parameter)
        print('GridSearch metric value:', metric_value)

        best_model.fit(train_multi, verbose=True)
        preds = best_model.predict(n=predict_length,series=train_multi)

        if scalered:
            preds = transformer1.inverse_transform(preds)

        pred = TimeSeries.from_times_and_values(time_index[divide_point:divide_point+predict_length],
                         preds.pd_dataframe().iloc[:,-1])
    else:
        pass

    plt.figure(figsize=(6,3))
    target_series.plot(label='actual',linewidth=1.5)
    pred.plot(label='forecast',linewidth=1.5)
    plt.legend()
    if col_names[0][0] == 'n':
        churn_rate_name = '净流失率'
    else:
        churn_rate_name = '重要开发者流失率'
    '''if variate_mode == 1:
        plt.title(model_str+' 社区(' + str(repo_id) + ')' + churn_rate_name + '曲线预测图(multivariate预测)')
    elif variate_mode == 0:
        plt.title(model_str+' 社区(' + str(repo_id) + ')' + churn_rate_name + '曲线预测图(univariate预测)')
    else:
        plt.title(model_str+' 社区(' + str(repo_id) + ')' + churn_rate_name + '曲线预测图(multiple series预测)')'''
    if fig_dir!='':
        plt.savefig(fig_dir+'\\'+time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime()) +'_'+model_str+'_'+
                    str(variate_mode)+'.png',dpi=300,bbox_inches = 'tight')
    plt.show()
    print('MAPE = {:.2f}%'.format(mape(target_series, pred)))
    print('MSE = {:.2f}'.format(mse(target_series, pred)))
    print('RMSE = {:.2f}'.format(rmse(target_series, pred)))
    print('MAE = {:.2f}'.format(mae(target_series, pred)))
    print('sMAPE = {:.2f}%'.format(smape(target_series, pred)))


if __name__ == '__main__':
    id = 2
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select repo_id from churn_search_repos_final where id = ' + str(id))
    result = cursor.fetchone()
    repo_id = result[0]
    fig_dir = r'C:\Users\cxy\Desktop\model_figs'

    ret = getTimeData(id,0)
    if ret != None:
        time_index = ret[0]
        data_frame = ret[1]
        col_names = ret[2]
        churn_rate_order = ret[3]

        model_str = 'RNN'
        variate_mode = 0
        # darts_rnnmodel(repo_id,time_index,data_frame,col_names,divide_point=-36,predict_length=36,
        #                model_str=model_str,input_chunk_length=12,n_epochs=300,batch_size=16,variate_mode=variate_mode,
        #                n_rnn_layers=3,dropout=0.0,lr=1e-3,fig_dir=fig_dir)
        # darts_rnnmodel(repo_id, time_index, data_frame, col_names, divide_point=-36, predict_length=36,
        #                model_str=model_str,variate_mode=variate_mode,fig_dir=fig_dir)
        darts_rnnmodel(repo_id, time_index, data_frame, col_names, divide_point=-36, predict_length=36,
                       model_str=model_str, input_chunk_length=12, n_epochs=300, batch_size=16,
                       variate_mode=variate_mode,
                       n_rnn_layers=4, dropout=0.0, lr=1e-3,fig_dir='')
        # get_best_rnnmodel(repo_id,time_index,data_frame,col_names,divide_point=-36,predict_length=36,
        #                   model_str=model_str,variate_mode=variate_mode)

        model_str='RNN'
        variate_mode=1
        # darts_rnnmodel(repo_id,time_index,data_frame,col_names,divide_point=-36,predict_length=36,
        #                model_str=model_str,input_chunk_length=12,n_epochs=600,batch_size=32,variate_mode=variate_mode,
        #                n_rnn_layers=3,dropout=0.0,lr=0.1)
        '''darts_rnnmodel(repo_id,time_index,data_frame,col_names,divide_point=-36,predict_length=36,
                       model_str=model_str,input_chunk_length=24,n_epochs=600,batch_size=64,variate_mode=variate_mode,
                       n_rnn_layers=1,dropout=0.0,lr=0.01,fig_dir='')'''

        # get_best_rnnmodel(repo_id,time_index,data_frame,col_names,divide_point=-36,predict_length=36,
        #                   model_str=model_str,variate_mode=variate_mode)