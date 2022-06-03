import datetime
import matplotlib
import matplotlib.pyplot as plt
from churn_data_analysis.draw_time_sequence_chart import dbHandle
from statsmodels.tsa.stattools import adfuller
import os
import numpy as np
from scipy import stats
from scipy.stats import norm,mstats
import pandas as pd
from prettytable import PrettyTable
from churn_data_analysis.draw_return_visit_curve import getRepoUserList
from churn_data_analysis.churn_rate_analysis import drawRateHistogram,drawBoxplot,descriptiveAnalysis

matplotlib.rcParams['font.sans-serif'] = ['KaiTi']
matplotlib.rcParams['axes.unicode_minus'] = False
time_fmt = '%Y-%m-%d'

# 获取某一仓库的净流失率数据
# user_filename:用户数据文件名
# churn_limit_list:仓库的流失期限数据
# step: 7或28
def getNetChurnRateData(repo_id,user_filename,churn_limit_list,step=7):
    churn_count_list = []
    active_count_list = []
    step_list = []
    churn_id_lists = []
    active_id_lists = []
    with open(user_filename, 'r', encoding='utf-8')as f:
        f.readline()
        for line in f.readlines():
            contents = line.split(',')
            step_list.append(int(contents[0]))
            active_count_list.append(len(contents[4].split(' ')) - 1)
            churn_count_list.append(len(contents[5].split(' ')) - 1)
            churn_id_lists.append(contents[5].split(' ')[0:-1])
            active_id_lists.append(contents[4].split(' ')[0:-1])
    rate_list = [0.0]
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select created_at from churn_search_repos_final where repo_id = ' + str(repo_id))
    result = cursor.fetchone()
    create_time = result[0][0:10]
    end_time = '2022-01-01'
    for i in range(1, len(step_list)):
        churn_limit = 53
        start_day = (datetime.datetime.strptime(create_time, time_fmt) + datetime.timedelta(days=step * i)).strftime(
            time_fmt)
        for j in range(len(churn_limit_list) - 1, -1, -1):
            if churn_limit_list[j][0] <= start_day:
                churn_limit = int(churn_limit_list[j][1])
                break
        if i * step < churn_limit:
            rate_list.append(0.0)
        else:
            index = i - int(churn_limit * 7 / step)
            if index < 0:
                index = 0
            max_exist_count = 0  # mode=1,step>7时可能找不到准确的区间，则找近似区间
            max_exist_index = i - int(churn_limit * 7 / step)
            if_find_period = True  # 是否准确找到分母区间
            if churn_count_list[i] > 0:  # 寻找准确的分母区间
                if_find_period = False
                for k in range(i - int(churn_limit * 7 / step) + 9, i - int(churn_limit * 7 / step) - 10,
                               -1):  ##############################
                    if k < 0 or k >= len(active_id_lists):
                        continue
                    exist_count = 0
                    for user_id in churn_id_lists[i]:
                        if user_id in active_id_lists[k]:
                            exist_count += 1
                    if exist_count > max_exist_count:
                        max_exist_index = k
                        max_exist_count = exist_count
                    if exist_count == churn_count_list[i]:
                        index = k
                        if_find_period = True
                        # print(i,index - (i - int(churn_limit*7/step)), exist_count, index, i - int(churn_limit*7/step))
                        break
                if if_find_period == False:
                    index = max_exist_index
                    print(i, index - (i - int(churn_limit * 7 / step)), max_exist_count,
                          churn_count_list[i])  #########################
            if active_count_list[index] == 0:
                rate_list.append(0.0)
            else:
                if if_find_period:
                    rate_list.append(float(churn_count_list[i]) / active_count_list[index])
                else:  # 没有找到合适的分母
                    rate_list.append(float(max_exist_count) / active_count_list[index])
    return step_list,rate_list


# Cox-Stuart趋势存在性检验，分析曲线趋势
# https://blog.csdn.net/weixin_39891262/article/details/111022600
def coxStuartTrendTest(data_list):
    lst = data_list.copy()
    if len(lst)%2==0:
        c = int(len(lst)/2)
    else:
        c = int((len(lst)+1)/2)
    pos_count = 0
    neg_count = 0
    for i in range(c):
        if i+c<len(lst):
            if lst[i+c]>lst[i]:
                pos_count += 1
            elif lst[i+c]<lst[i]:
                neg_count += 1
    num = pos_count + neg_count
    k = min(neg_count,pos_count)
    p_value = 2 * stats.binom.cdf(k, num, 0.5)
    if pos_count < neg_count and p_value < 0.05:    # 递减
        return -1
    elif neg_count < pos_count and p_value < 0.05:  #递增
        return 1
    else:   # 无明显趋势
        return 0


# Mann-Kendall检验,分析曲线趋势
# https://blog.csdn.net/weixin_39891262/article/details/111022600
def mkTest(data_list):
    pass

# 趋势分析，包含增减性分析和波动性分析
# repo_id:仓库id
# start_days:排除的开发初期的天数
# step_list,churn_rate_list:流失率曲线数据
# period_length:统计均值的间隔，默认100天统计一次
# if_draw:是否绘制图像
# figname:存储的图像名，若为空字符串则不存储
def trendAnalysis(repo_id,start_days,step_list,churn_rate_list,period_length=100,if_draw=True,figname=''):
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select created_at from churn_search_repos_final where repo_id = ' + str(repo_id))
    result = cursor.fetchone()
    create_time = result[0][0:10]
    end_time = '2022-01-01'
    step=step_list[1]-step_list[0]
    # churn_rate_sum = 0.0
    step_count = 0
    x_list = []
    avg_list = []
    std_list = []
    period_list = []
    for i in range(len(step_list)):
        if step_list[i]<start_days:
            continue
        # churn_rate_sum += churn_rate_list[i]
        period_list.append(churn_rate_list[i])
        step_count += 1
        if step_count*step>=period_length:
            if step_list[i]>int(step_count/2)*step:
                x_list.append(step_list[i]-int(step_count/2)*step)
            else:
                x_list.append(0)
            avg_list.append(np.average(np.array(period_list)))
            std_list.append(np.std(np.array(period_list)))
            # avg_list.append(churn_rate_sum/step_count)
            step_count = 0
            period_list = []
            # churn_rate_sum = 0
    if step_count>0:
        x_list.append(step_list[-1]-int(step_count/2)*step)
        avg_list.append(np.average(np.array(period_list)))
        std_list.append(np.std(np.array(period_list)))

    cox_stuart_value = coxStuartTrendTest(churn_rate_list[int(start_days/step)+1:])
    cox_stuart = 'no trend'
    if cox_stuart_value>0:
        cox_stuart = 'increasing'
    elif cox_stuart_value < 0:
        cox_stuart = 'decreasing'

    adf_result = adfuller(churn_rate_list[int(start_days/step)+1:])[0:2]
    adf_value = adf_result[0]
    adf_p_value = adf_result[1]
    # print(adf_value,adf_p_value)
    adf = 'not stable'
    if adf_p_value < 0.05:  # 曲线平稳
        adf = 'stable'

    std_average = np.average(np.array(std_list))    # 标准差的平均值

    if if_draw == True:
        fig = plt.figure(figsize=(10, 5))
        ax = fig.add_subplot(111)
        ax.plot(step_list, churn_rate_list, label='开发者流失率', linewidth=1, color='limegreen',
                 marker=',')
        ax.plot(x_list, avg_list, label='流失率均值(step='+str(period_length)+')', linewidth=1.5, color='orangered',
                 marker=',')
        ax.legend(loc='upper left')
        ax.set_xlabel('时间（天）')
        ax.set_ylabel('流失率')
        ax.set_ylim(0.0,1.0)
        ax2 = ax.twinx()
        # max_std = max(std_list)
        # max_std = max(max_std,0.5)
        # ax2.set_ylim(0.0,max_std)
        ax2.set_ylim(0.0, 0.4)
        ax2.plot(x_list,std_list,label='流失率标准差(step='+str(period_length)+')', linewidth=1.5, color='blue',
                 marker=',')
        ax2.legend(loc='upper right')
        plt.title(
            '社区（repo_id = ' + str(repo_id) + '）' + create_time + '~' + end_time + '期间' +
            '开发者净流失率曲线(step=' + str(step) + ')')
        if figname!='':
            plt.savefig(figname)
        plt.show()
    return x_list,avg_list,std_list,std_average,cox_stuart,adf,adf_value,adf_p_value


# 为每个仓库进行趋势分析
# save_dir:保存数据文件和图像文件的路径
# user_dir:保存各类用户数据文件的路径
# churn_limit_lists:各个仓库的流失期限数据，用于绘制流失率曲线
# start_days_list: 每个仓库的start_days数据
# period_length:趋势分析时均值和方差的统计间隔
# step:默认28
def trendAnalysisForRepos(save_dir,user_dir,churn_limit_lists,start_days_list,period_length,step=28):
    dbObejct = dbHandle()
    cursor = dbObejct.cursor()
    cursor.execute('select id,repo_id,repo_name from churn_search_repos_final')
    results = cursor.fetchall()

    user_filenames = os.listdir(user_dir)
    id_user_filenames = dict()
    for filename in user_filenames:
        id_user_filenames[int(filename.split('_')[0])] = filename

    data_filename = save_dir + '/net_churn_rate_trend_report.csv'
    with open(data_filename,'w',encoding='utf-8')as f:
        f.write('id,std_average_value,cox_stuart_trend,adf,adf_value,adf_p_value,\n')
    for result in results:
        id = result[0]
        repo_id = result[1]
        repo_name = result[2]
        step_list, churn_rate_list = getNetChurnRateData(repo_id, user_dir + '/' + id_user_filenames[id],
                                                         churn_limit_lists[id - 1], step)
        figname = save_dir+'/net_churn_rate_trend_fig/'+str(result[0]) + '_' + repo_name.replace('/', '_') + '.png'
        ret = trendAnalysis(repo_id, start_days_list[id - 1], step_list, churn_rate_list, period_length,
                                     figname=figname)
        with open(data_filename, 'a', encoding='utf-8')as f:
            f.write(str(id)+','+str(ret[3])+','+str(ret[4])+','+str(ret[5])+','+str(ret[6])+','+str(ret[7])+',\n')


# 为所有仓库进行频率分布分析，包括
def frequencyAnalysisForRepos(save_dir,user_dir,churn_limit_lists,start_days_list,step=28):
    dbObejct = dbHandle()
    cursor = dbObejct.cursor()
    cursor.execute('select id,repo_id,repo_name from churn_search_repos_final')
    results = cursor.fetchall()

    user_filenames = os.listdir(user_dir)
    id_user_filenames = dict()
    for filename in user_filenames:
        id_user_filenames[int(filename.split('_')[0])] = filename
    for result in results:
        id = result[0]
        repo_id = result[1]
        repo_name = result[2]
        step_list, churn_rate_list = getNetChurnRateData(repo_id, user_dir + '/' + id_user_filenames[id],
                                                         churn_limit_lists[id - 1], step)
        start_days = start_days_list[id-1]
        churn_rate_list = churn_rate_list[int(start_days/step)+1:]

        fig_title = str(repo_id)+'. '+repo_name+' 仓库流失率频率分布图'
        figname = save_dir+'/net_churn_rate_histogram/'+str(result[0]) + '_' + repo_name.replace('/', '_')\
                  + '-histogram.png'
        drawRateHistogram(churn_rate_list,fig_title,figname)

        fig_title = str(repo_id) + '. ' + repo_name + ' 仓库流失率箱线图'
        figname = save_dir + '/net_churn_rate_boxplot/' + str(result[0]) + '_' + repo_name.replace('/', '_') \
                  + '-boxplot.png'
        churn_rate_lists = []
        y_labels = []
        churn_rate_lists.append(churn_rate_list.copy())
        y_labels.append(str(repo_id))
        drawBoxplot(churn_rate_lists,y_labels,fig_title,figname)

        filename = save_dir + '/net_churn_rate_descriptive/' + str(result[0]) + '_' + repo_name.replace('/', '_') \
                  + '-descriptive.csv'
        descriptiveAnalysis(churn_rate_list,filename)


if __name__ == '__main__':
    repo_id = '45717250'
    user_filename = 'E:/bysj_project/repo_users_by_period/data_28/29_tensorflow-tensorflow-28.csv'
    start_days = 100
    period_length = 100
    churn_limit_lists = []
    for i in range(30):
        churn_limit_lists.append([])
    with open('repo_churn_limits.csv', 'r', encoding='utf-8')as f:
        f.readline()
        for line in f.readlines():
            items = line.split(',')
            id = int(items[0])
            new_list = []
            new_list.append(items[1])
            new_list.append(items[3])
            churn_limit_lists[id - 1].append(new_list)
    # step_list,churn_rate_list = getNetChurnRateData(repo_id,user_filename,churn_limit_lists[28],28)


    start_days_list =[
        200, 150, 150, 100, 100,
        100, 200, 100, 100, 200,
        250, 150, 150, 100, 200,
        200, 200, 100, 100, 100,
        100, 150, 150, 250, 250,
        150, 150, 200, 100, 100
    ]

    # 趋势分析
    save_dir = 'E:/bysj_project/net_churn_rate_trend'
    user_dir = 'E:/bysj_project/repo_users_by_period/data_28'
    trendAnalysisForRepos(save_dir,user_dir,churn_limit_lists,start_days_list,period_length,28)

    # 单个仓库频率分析和描述性分析
    save_dir = 'E:/bysj_project/net_churn_rate_frequency'
    user_dir = 'E:/bysj_project/repo_users_by_period/data_28'
    # frequencyAnalysisForRepos(save_dir,user_dir,churn_limit_lists,start_days_list,28)

    # 仓库描述性数据汇总
    dir_name = 'E:/bysj_project/net_churn_rate_frequency/net_churn_rate_descriptive'
    data_file = 'E:/bysj_project/net_churn_rate_frequency/net_churn_rate_descriptive_report.csv'
    filenames = os.listdir(dir_name)
    id_filenames = dict()
    for filename in filenames:
        id_filenames[int(filename.split('_')[0])]=filename
    # with open(data_file,'w',encoding='utf-8')as f:
    #     f.write('id,mean value,median value,standard deviation,max value,min value,\n')
    # for i in range(30):
    #     filename = id_filenames[i+1]
    #     values = []
    #     with open(dir_name+'/'+filename,'r',encoding='utf-8')as f:
    #         f.readline()
    #         for j in range(5):
    #             values.append(float(f.readline().split(',')[1]))
    #     with open(data_file,'a',encoding='utf-8')as f:
    #         f.write(str(i + 1) + ',' + str(values[2]) + ',' + str(values[3]) + ',' + str(values[4]) + ',' + str(
    #             values[1]) + ',' + str(values[0]) + ',\n')

    mean_list = []
    std_list = []
    for i in range(30):
        filename = id_filenames[i + 1]
        values = []
        with open(dir_name + '/' + filename, 'r', encoding='utf-8')as f:
            f.readline()
            for j in range(5):
                values.append(float(f.readline().split(',')[1]))
            mean_list.append(values[2])
            std_list.append(values[4])
    # drawRateHistogram(std_list,'仓库流失率标准差频率分布图')
    drawRateHistogram(mean_list, '仓库平均流失率频率分布图', 'E:/bysj_project/net_churn_rate_frequency/mean_rate_histogram.png')
    # drawBoxplot([mean_list.copy()], ['平均流失率'],'仓库平均流失率箱线图', 'E:/bysj_project/net_churn_rate_frequency/mean_rate_boxplot.png')
    # descriptiveAnalysis(mean_list,'E:/bysj_project/net_churn_rate_frequency/mean_rate_descriptive.csv')