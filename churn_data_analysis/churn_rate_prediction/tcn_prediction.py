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
from darts.models import RNNModel, TCNModel, TransformerModel, NBEATSModel
from darts.dataprocessing.transformers import Scaler
from sklearn.preprocessing import MinMaxScaler
from churn_data_analysis.churn_rate_prediction.nbeats_prediction import getTimeData

torch.manual_seed(1);np.random.seed(1)  # for reproducibility

fmt_day = '%Y-%m-%d'
fmt_second = '%Y-%m-%d %H:%M:%S'

torch.manual_seed(1);np.random.seed(1)  # for reproducibility



def darts_tcnmodel(repo_id,time_index, data_frame,col_names, divide_point=-12, predict_length=12,
                   input_chunk_length=24, output_chunk_length=12, n_epochs=200,batch_size=32,
                   kernel_size=3,num_filters=3, num_layers=None, dilation_base=2,lr=1e-3,
                   weight_norm=False,dropout=0.2,random_state=42,work_dir='tcn_work_dir',fig_dir='',
                   variate_mode=0,save_model=False,scalered=True):
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
    model = TCNModel(
        input_chunk_length=input_chunk_length,
        output_chunk_length=output_chunk_length,
        n_epochs=n_epochs,
        batch_size=batch_size,
        kernel_size=kernel_size,  # 卷积核的大小
        num_filters=num_filters,  # 卷积层过滤器数
        num_layers=num_layers,  # 卷积层个数，如果为None时，选择最小的数量，使得每个输出都依赖于全部输入
        dilation_base=dilation_base,  # 每一级膨胀的指数基数
        weight_norm=weight_norm,  # 是否使用权重正则化
        dropout=dropout,
        optimizer_kwargs={"lr": lr},
        random_state=random_state,
        work_dir=work_dir,
    )

    if variate_mode==0:  # 单变量预测
        model.fit(train,verbose=True)
        pred = model.predict(n=predict_length)
        if scalered:
            pred = transformer0.inverse_transform(pred)
    elif variate_mode==1:
        model.fit(train_multi, verbose=True)
        preds = model.predict(n=predict_length)

        if scalered:
            preds = transformer1.inverse_transform(preds)

        pred = TimeSeries.from_times_and_values(time_index[divide_point:divide_point+predict_length],
                         preds.pd_dataframe().iloc[:,-1])
    else:
        for series in series_list:
            train_list.append(series[:divide_point])
            val_list.append(series[divide_point:divide_point + predict_length])
        model.fit(train_list,verbose=True)
        if scalered:
            pred_list = model.predict(n=predict_length,series=train_list)
            pred = transformer2.inverse_transform(pred_list)[-1]
        else:
            pred=model.predict(n=predict_length,series=train)

    plt.figure(figsize=(10,5))
    target_series.plot(label='actual')
    pred.plot(label='forecast')
    plt.legend()
    if col_names[0][0]=='n':
        churn_rate_name='净流失率'
    else:
        churn_rate_name='重要开发者流失率'
    '''if variate_mode == 1:
        plt.title('TCN 社区('+str(repo_id)+')'+churn_rate_name+'曲线预测图(multivariate预测)')
    elif variate_mode == 0:
        plt.title('TCN 社区(' + str(repo_id) + ')' + churn_rate_name + '曲线预测图(univariate预测)')
    else:
        plt.title('TCN 社区(' + str(repo_id) + ')' + churn_rate_name + '曲线预测图(multiple series预测)')'''
    if fig_dir!='':
        plt.savefig(fig_dir + '\\' + time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime()) + '_tcn_' +
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
        model.save_model('tcn_models/' + model_filename)


def get_best_tcnmodel(repo_id,time_index, data_frame,col_names, divide_point=-12, predict_length=12,
                      work_dir='tcn_work_dir',variate_mode=0,scalered=True,fig_dir=''):
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

    model = TCNModel(input_chunk_length=24,output_chunk_length=12)

    if variate_mode == 0:  # 单变量预测
        parameters = {
            'work_dir': [work_dir],
            'random_state':[42],
            'weight_norm':[True],
            'num_layers': [None],
            #########################
            'input_chunk_length':[24],#[12,24,36],#[6,12,24,36],
            'output_chunk_length':[3],#[3,6],
            'optimizer_kwargs': [{"lr": 1e-2}], #[{"lr": 0.05}, {"lr": 1e-2}, {"lr": 1e-3}],
            #########################
            'n_epochs':[500,600,700,800],
            'batch_size':[16,32,64],#[16,32,64],
            # #########################
            'kernel_size':[3],#[3,5,7],
            'num_filters':[3],#[3,5,7],
            # ##########################
            'dilation_base':[2],#[2,3,4],
            'dropout':[0.1],#[0.0,0.1,0.2,0.3],
            # ###########################
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

        model_filename = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())+'_tcn_model.pth.tar'
        best_model.save_model('rnn_models/'+model_filename)
        print(best_parameter)
        print('GridSearch metric value:',metric_value)

        best_model.fit(train,verbose=True)
        pred = best_model.predict(n=predict_length)
        if scalered:
            pred = transformer0.inverse_transform(pred)
    elif variate_mode==1:
        parameters = {
            'work_dir': [work_dir],
            'random_state': [42],
            'weight_norm': [True],
            'num_layers': [None],
            #########################
            'input_chunk_length': [12],#[12, 24, 36],
            'output_chunk_length': [6],#[3, 6],
            'dropout': [0.0, 0.1, 0.2, 0.3],
            'optimizer_kwargs': [{"lr": 1e-2}, {"lr": 1e-3}, {"lr": 1e-1}],  # [{"lr": 0.05}, {"lr": 1e-2}, {"lr": 1e-3}],
            #########################
            'n_epochs': [400],  # [100,200,300],
            'batch_size': [16],  # [16,32,64],
            #########################
            # 'kernel_size': [3, 5, 7],
            # 'num_filters': [3, 5, 7],
            # ##########################
            # 'dilation_base': [2, 4, 6],
        }

        best_model, best_parameter, metric_value = model.gridsearch(
            parameters=parameters,
            series=train_multi,
            start=0.6,  # 开始评估模型的划分点，默认0.5
            val_series=val_multi,  # 使用该参数时，是split window mode，用验证集来评估
            metric=mape,  # 模型评估指标,默认MAPE
            verbose=True
        )

        model_filename = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime()) +'_multi_model.pth.tar'
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

    plt.figure(figsize=(10, 5))
    target_series.plot(label='actual')
    pred.plot(label='forecast')
    plt.legend()
    if col_names[0][0] == 'n':
        churn_rate_name = '净流失率'
    else:
        churn_rate_name = '重要开发者流失率'
    '''if variate_mode == 1:
        plt.title('TCN 社区(' + str(repo_id) + ')' + churn_rate_name + '曲线预测图(multivariate预测)')
    elif variate_mode == 0:
        plt.title('TCN 社区(' + str(repo_id) + ')' + churn_rate_name + '曲线预测图(univariate预测)')
    else:
        plt.title('TCN 社区(' + str(repo_id) + ')' + churn_rate_name + '曲线预测图(multiple series预测)')'''
    if fig_dir!='':
        plt.savefig(fig_dir + '\\' + time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime()) + '_tcn_' +
                    str(variate_mode) + '.png',dpi=300, bbox_inches='tight')
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

        variate_mode=1

        # darts_tcnmodel(repo_id, time_index, data_frame, col_names, divide_point=-36, predict_length=36,
        #                input_chunk_length=24, output_chunk_length=12, n_epochs=200, batch_size=32,
        #                kernel_size=3, num_filters=3, num_layers=None, dilation_base=2, lr=1e-3,
        #                weight_norm=False, dropout=0.2,
        #                #fig_dir=fig_dir,
        #                variate_mode=variate_mode)

        get_best_tcnmodel(repo_id,time_index,data_frame,col_names,divide_point=-36,predict_length=36,
                          variate_mode=variate_mode)