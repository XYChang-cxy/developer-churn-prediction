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

torch.manual_seed(1);np.random.seed(1)  # for reproducibility

fmt_day = '%Y-%m-%d'
fmt_second = '%Y-%m-%d %H:%M:%S'


# 获取仓库的time_index和data_frame;排除无效数据时间段
# mode: 0--原序列通过格兰杰因果检验的（流失率原因）；1--原序列和一阶差分序列通过格兰杰因果检验的（流失率原因）；2--各类数量曲线
# churn_rate:0--全体流失率；1--重要开发者流失率
# startDay、endDay：确定始末时间，如果都为空则默认全段数据
# 返回：time_index, data_frame, churn_rate_order(流失率数据单整阶数)
def getTimeData(id,mode,churn_rate=0,startDay='',endDay='',step=28):
    granger_data_dir_2 = r'E:\bysj_project\granger_causality_test\data_28_start'
    granger_data_diff_dir_2 = r'E:\bysj_project\granger_causality_test\data_28_start_diff'
    granger_result_dir_2 = r'E:\bysj_project\granger_results\data_28_start'
    granger_result_diff_dir_2 = r'E:\bysj_project\granger_results\data_28_start_diff'

    if mode == 0:
        data_dir = granger_data_dir_2
        result_dir = granger_result_dir_2
    else:
        data_dir = granger_data_diff_dir_2
        result_dir = granger_result_diff_dir_2

    filenames = os.listdir(data_dir)
    id_filenames = dict()
    for filename in filenames:
        id_filenames[int(filename.split('_')[0])] = filename

    repo_filename = id_filenames[id]

    churn_rate_index = 47+churn_rate
    churn_rate_col_name = pd.read_csv(data_dir+'/'+repo_filename).columns.to_list()[churn_rate_index]

    if mode == 0:
        churn_rate_order = 0
    else:
        churn_rate_order = int(churn_rate_col_name.split('_')[-1])
    if churn_rate_order > 1:
        print('There is no data for',churn_rate_col_name)
        return None

    col_names = [churn_rate_col_name]

    if mode == 2:
        extend_list = pd.read_csv(data_dir+'/'+repo_filename).columns.to_list()[1:8]
        col_names.extend(extend_list)
    else:
        with open(result_dir+'/'+repo_filename,'r',encoding='utf-8')as f:
            f.readline()
            for line in f.readlines():
                col = line.split(',')[0]
                if churn_rate == 1 and len(line.split(','))<4:
                    print('There is no data for imp_churn_rate!')
                    return None
                value = line.split(',')[1+2*churn_rate]
                if value == 'cause and effect' or value == 'effect':
                    col_names.append(col)

    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select repo_id,created_at from churn_search_repos_final where id = ' + str(id))
    result = cursor.fetchone()
    create_time = result[1][0:10]
    skip_days = int(pd.read_csv(data_dir+'/'+repo_filename, usecols=[0]).loc[0]) + step
    start_time = (datetime.datetime.strptime(create_time, fmt_day) + datetime.timedelta(days=skip_days)).strftime(
        fmt_day)

    if startDay == '' or startDay <= start_time:
        startDay = start_time
        start_rows = 0
    else:
        timedelta = (datetime.datetime.strptime(startDay,fmt_day)-datetime.datetime.strptime(start_time,fmt_day)).days
        startDay = (datetime.datetime.strptime(startDay,fmt_day)+datetime.timedelta(days=step-timedelta%step)).strftime(fmt_day)
        timedelta = (datetime.datetime.strptime(startDay, fmt_day) - datetime.datetime.strptime(start_time,
                                                                                                fmt_day)).days
        start_rows = int(timedelta/step)

    if endDay == '':
        endDay = '2022-01-01'
    if endDay <= startDay:
        print('Time range error!')
        return None

    time_index = pd.date_range(start=startDay, end=endDay, freq=str(step) + 'D')
    data_frame = pd.read_csv(data_dir+'/'+repo_filename,usecols=col_names)[start_rows:start_rows+len(time_index)]

    # 剔除包含负数的时间段的数据
    dropped_lines = 0
    for i in range(len(time_index)):
        flag = True
        for col in col_names:
            if data_frame.iloc[i].at[col] == -1:
                flag = False
                break
        if flag:
            dropped_lines = i
            break
    # print(time_index)
    # print(data_frame)
    # print(time_index[dropped_lines:])
    # print(data_frame[dropped_lines:])
    # print(id,churn_rate_col_name,'mode =',mode,dropped_lines, dropped_lines/len(time_index)*100.0)

    # print(id,churn_rate_order)
    return time_index[dropped_lines:],data_frame[dropped_lines:],col_names,churn_rate_order


# divide_point: 预测划分时间点，如果是小数则按比例划分，否则按下标
# predict_length:预测时间段长度
# variate_mode: 0--单变量预测;1--多变量预测;2--多时间序列(series list)预测
# scalered: 是否对数据进行标准化（归一化）
def darts_nbeadsmodel(repo_id,time_index, data_frame,col_names, divide_point=-12, predict_length=12,
                      input_chunk_length=24, output_chunk_length=12,
                      n_epochs=200,batch_size=32,num_stacks=30,num_blocks=1,
                      num_layers=4,layer_widths=256,
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
        series = TimeSeries.from_times_and_values(time_index,data_frame.iloc[:,[i]])
        series_list.append(series)
    if scalered: # 数据标准化
        series_list = transformer2.fit_transform(series_list)

    # chun rate series(variate_mode=0)
    target_series = TimeSeries.from_times_and_values(time_index,data_frame.iloc[:,[-1]])
    if scalered:
        uni_series = transformer0.fit_transform(target_series)
    else:
        uni_series = target_series
    train, val = uni_series[:divide_point], uni_series[divide_point:divide_point + predict_length]

    # variate_mode=1:multivariate
    multi_series = TimeSeries.from_times_and_values(time_index, data_frame)
    if scalered:
        multi_series = transformer1.fit_transform(multi_series)
    train_multi,val_multi = multi_series[:divide_point], multi_series[divide_point:divide_point + predict_length]

    train_list = []
    val_list = []

    model = NBEATSModel(
        input_chunk_length=input_chunk_length,
        output_chunk_length=output_chunk_length,
        n_epochs=n_epochs,
        batch_size=batch_size,
        num_stacks=num_stacks,  # 模型总stack数
        num_blocks=num_blocks,  # 每个stack的blocks数
        num_layers=num_layers,  # 每个block的全连接层数
        layer_widths=layer_widths  # 全连接层的神经元数
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
    if variate_mode == 1:
        plt.title('N-BEATS 社区('+str(repo_id)+')'+churn_rate_name+'曲线预测图(multivariate预测)')
    elif variate_mode == 0:
        plt.title('N-BEATS 社区(' + str(repo_id) + ')' + churn_rate_name + '曲线预测图(univariate预测)')
    else:
        plt.title('N-BEATS 社区(' + str(repo_id) + ')' + churn_rate_name + '曲线预测图(multiple series预测)')
    plt.show()
    print('MAPE = {:.2f}%'.format(mape(target_series, pred)))
    print('MSE = {:.2f}'.format(mse(target_series, pred)))
    print('RMSE = {:.2f}'.format(rmse(target_series, pred)))
    print('MAE = {:.2f}'.format(mae(target_series, pred)))
    print('sMAPE = {:.2f}%'.format(smape(target_series, pred)))
    # if variate_mode==0:
    #     print('MASE = {:.2f}'.format(mase(target_series, pred,train)))
    # elif variate_mode == 1:
    #     print('MASE = {:.2f}'.format(mase(series, preds, train_multi)))
    # else:
    #     print('MASE = {:.2f}'.format(mase(target_series, pred, train)))

    if variate_mode==0:
        model_filename = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime()) + 'univariate_model.pth.tar'
    elif variate_mode == 1:
        model_filename = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime()) + 'multivariate_model.pth.tar'
    else:
        model_filename = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime()) + 'multi_series_model.pth.tar'
    if save_model:
        model.save_model('nbeats_models/'+model_filename)


def get_best_nbeatsmodel(repo_id,time_index, data_frame,col_names, divide_point=-12, predict_length=12,
                         variate_mode=0,scalered=True):
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

    model = NBEATSModel(input_chunk_length=24,output_chunk_length=12)

    if variate_mode == 0:  # 单变量预测
        parameters = {
            'input_chunk_length':[24],#[12,24,36]
            'output_chunk_length':[3],#[3,6,12]
            'n_epochs':[100],#[100,200,300],
            'batch_size':[32],#[16,32,64],
            'num_blocks':[1],
            'layer_widths':[256]
        }

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

        model_filename = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())+'_model.pth.tar'
        best_model.save_model('nbeats_models/'+model_filename)
        print(best_parameter)
        print('GridSearch metric value:',metric_value)

        best_model.fit(train,verbose=True)
        pred = best_model.predict(n=predict_length)
        if scalered:
            pred = transformer0.inverse_transform(pred)
    elif variate_mode==1:
        parameters = {
            'input_chunk_length': [36],
            'output_chunk_length': [12],
            'n_epochs': [200],
            'batch_size': [64],
            'num_blocks': [1],#[1, 2, 3],
            'layer_widths': [256],#[128, 256, 512]
        }

        best_model, best_parameter, metric_value = model.gridsearch(
            parameters=parameters,
            series=train_multi,
            start=0.6,  # 开始评估模型的划分点，默认0.5
            val_series=val_multi,  # 使用该参数时，是split window mode，用验证集来评估
            metric=mape,  # 模型评估指标,默认MAPE
            verbose=True
        )

        model_filename = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime()) + '_multi_model.pth.tar'
        best_model.save_model('nbeats_models/' + model_filename)
        print(best_parameter)
        print('GridSearch metric value:', metric_value)

        best_model.fit(train_multi, verbose=True)
        preds = best_model.predict(n=predict_length,series=train_multi)
        if scalered:
            preds = transformer1.inverse_transform(preds)
        pred = TimeSeries.from_times_and_values(time_index[divide_point:divide_point+predict_length],
                         preds.pd_dataframe().iloc[:,-1])
    else:
        for series in series_list:
            train_list.append(series[:divide_point])
            val_list.append(series[divide_point:divide_point + predict_length])
        parameters = {
            'input_chunk_length': [6, 12, 24, 36],
            'output_chunk_length': [3, 6, 12],
            'n_epochs': [100, 200, 300],
            'batch_size': [16, 32, 64],
            'num_blocks': [1, 2, 3],
            'layer_widths': [128, 256, 512]
        }
        min_mape = 200
        input_chunk_length = 12
        output_chunk_length = 6
        n_epochs = 200
        batch_size = 32
        num_blocks = 1
        layer_widths = 256
        count = 0
        all_count = len(parameters['input_chunk_length']) * len(parameters['output_chunk_length']) \
                    + len(parameters['n_epochs']) * len(parameters['batch_size']) \
                    + len(parameters['num_blocks']) * len(parameters['layer_widths']) - 2

        param_filename = 'nbeats_models/'+time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime()) + '_params.csv'

        for i in parameters['input_chunk_length']:
            for o in parameters['output_chunk_length']:
                new_model = NBEATSModel(input_chunk_length=i, output_chunk_length=o,
                                        n_epochs=n_epochs, batch_size=batch_size,
                                        num_blocks=num_blocks, layer_widths=layer_widths)
                new_model.fit(train_list, verbose=True)
                pred = new_model.predict(n=predict_length, series=train)
                mape_value = mape(uni_series, pred)
                if mape_value < min_mape:
                    min_mape = mape_value
                    input_chunk_length = i
                    output_chunk_length = o
                count += 1
                print('Progress:', count, '/', all_count)
        with open(param_filename, 'w', encoding='utf-8')as f:
            f.write(str(input_chunk_length) + ',\n')
            f.write(str(output_chunk_length) + ',\n')
        for n in parameters['n_epochs']:
            for b in parameters['batch_size']:
                if n == 200 and b == 32:
                    continue
                new_model = NBEATSModel(input_chunk_length=input_chunk_length, output_chunk_length=output_chunk_length,
                                        n_epochs=n, batch_size=b,
                                        num_blocks=num_blocks, layer_widths=layer_widths)
                new_model.fit(train_list, verbose=True)
                pred = new_model.predict(n=predict_length, series=train)
                mape_value = mape(uni_series, pred)
                if mape_value < min_mape:
                    min_mape = mape_value
                    n_epochs = n
                    batch_size = b
                count += 1
                print('Progress:', count, '/', all_count)
        with open(param_filename, 'a', encoding='utf-8')as f:
            f.write(str(n_epochs) + ',\n')
            f.write(str(batch_size) + ',\n')
        for num in parameters['num_blocks']:
            for l in parameters['layer_widths']:
                if num == 1 and l == 256:
                    continue
                new_model = NBEATSModel(input_chunk_length=input_chunk_length,
                                        output_chunk_length=output_chunk_length,
                                        n_epochs=n_epochs, batch_size=batch_size,
                                        num_blocks=num, layer_widths=l)
                new_model.fit(train_list, verbose=True)
                pred = new_model.predict(n=predict_length, series=train)
                mape_value = mape(uni_series, pred)
                if mape_value < min_mape:
                    min_mape = mape_value
                    num_blocks = num
                    layer_widths = l
                count += 1
                print('Progress:', count, '/', all_count)
        with open(param_filename, 'a', encoding='utf-8')as f:
            f.write(str(num_blocks) + ',\n')
            f.write(str(layer_widths) + ',\n')
        print('input_chunk_length:', input_chunk_length, ', output_chunk_length:', output_chunk_length,
              ', n_epochs:', n_epochs, ', batch_size:', batch_size, ', num_blocks:', num_blocks,
              ', layer_widths:', layer_widths)
        print('Min MAPE:', min_mape)

        model = NBEATSModel(input_chunk_length=input_chunk_length,
                            output_chunk_length=output_chunk_length,
                            n_epochs=n_epochs, batch_size=batch_size,
                            num_blocks=num_blocks, layer_widths=layer_widths)
        model.fit(train_list, verbose=True)
        if scalered:
            pred_list = model.predict(n=predict_length,series=train_list)
            pred = transformer2.inverse_transform(pred_list)[-1]
        else:
            pred = model.predict(n=predict_length, series=train)


    plt.figure(figsize=(10,5))
    target_series.plot(label='actual')
    pred.plot(label='forecast')
    plt.legend()
    if col_names[0][0]=='n':
        churn_rate_name='净流失率'
    else:
        churn_rate_name='重要开发者流失率'
    if variate_mode == 1:
        plt.title('社区(' + str(repo_id) + ')' + churn_rate_name + '曲线预测图(multivariate预测)')
    elif variate_mode == 0:
        plt.title('社区(' + str(repo_id) + ')' + churn_rate_name + '曲线预测图(univariate预测)')
    else:
        plt.title('社区(' + str(repo_id) + ')' + churn_rate_name + '曲线预测图(multiple series预测)')
    plt.show()
    print('MAPE = {:.2f}%'.format(mape(target_series, pred)))
    print('MSE = {:.2f}'.format(mse(target_series, pred)))
    print('RMSE = {:.2f}'.format(rmse(target_series, pred)))
    print('MAE = {:.2f}'.format(mae(target_series, pred)))
    print('sMAPE = {:.2f}%'.format(smape(target_series, pred)))
    # if variate_mode == 0:
    #     print('MASE = {:.2f}'.format(mase(target_series, pred, train)))
    # elif variate_mode == 1:
    #     print('MASE = {:.2f}'.format(mase(series, preds, train_multi)))
    # else:
    #     print('MASE = {:.2f}'.format(mase(target_series, pred, train)))


if __name__ == '__main__':
    id = 2
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select repo_id from churn_search_repos_final where id = ' + str(id))
    result = cursor.fetchone()
    repo_id = result[0]

    ret = getTimeData(id,0)
    if ret != None:
        time_index = ret[0]
        data_frame = ret[1]
        col_names = ret[2]
        churn_rate_order = ret[3]
        # darts_nbeadsmodel(repo_id,time_index,data_frame,col_names,divide_point=-36,predict_length=36,
        #                   input_chunk_length=24,output_chunk_length=3,n_epochs=100,batch_size=32,
        #                   num_blocks=1,layer_widths=256,variate_mode=0,scalered=False)
        # darts_nbeadsmodel(repo_id, time_index, data_frame, col_names, divide_point=-36,predict_length=36,
        #                   input_chunk_length=36, output_chunk_length=12, n_epochs=200, batch_size=32,
        #                   num_blocks=1, layer_widths=256, variate_mode=1,scalered=False)
        # darts_nbeadsmodel(repo_id, time_index, data_frame, col_names, divide_point=-36,predict_length=36,
        #                   input_chunk_length=12, output_chunk_length=3, n_epochs=200, batch_size=32,
        #                   num_blocks=1, layer_widths=256, variate_mode=2,scalered=True)
        # darts_nbeadsmodel(repo_id, time_index, data_frame, col_names, divide_point=-36, predict_length=36,
        #                   input_chunk_length=24, output_chunk_length=3, n_epochs=200, batch_size=32,
        #                   num_blocks=1, layer_widths=256, variate_mode=2)

        # get_best_nbeatsmodel(repo_id, time_index, data_frame, col_names, divide_point=-36, predict_length=36,
        #                      variate_mode=0,scalered=True)
        # get_best_nbeatsmodel(repo_id, time_index, data_frame, col_names, divide_point=-36, predict_length=36,
        #                      variate_mode=1,scalered=True)
        # get_best_nbeatsmodel(repo_id, time_index, data_frame, col_names, divide_point=-36, predict_length=36,
        #                      variate_mode=2,scalered=False)
