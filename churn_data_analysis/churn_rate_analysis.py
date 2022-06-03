import datetime
import matplotlib
import matplotlib.pyplot as plt
from churn_data_analysis.draw_time_sequence_chart import dbHandle
import os
import numpy as np
import pandas as pd
from prettytable import PrettyTable
from churn_data_analysis.draw_return_visit_curve import getRepoUserList

matplotlib.rcParams['font.sans-serif'] = ['KaiTi']
matplotlib.rcParams['axes.unicode_minus'] = False
fmt_MySQL = '%Y-%m-%d'


# 获取某一寿命时间点下，不同社区的累计流失率
# data_dir_name: 存储流失率曲线数据的文件夹
# life_time_point: 寿命时间点,单位：天
# step: 必须和data_dir_name的step一致！！！
# 返回：两个列表，一个包含所有仓库数据（如果仓库寿命<life_time_point，则对应流失率为-1），一个仅包含有效流失率数据
def getChurnRateLists1(data_dir_name,life_time_point,step=28):
    '''dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select id, created_at from churn_search_repos_final')
    results = cursor.fetchall()
    id_create_time = dict()
    for result in results:
        id_create_time[result[0]]=result[1][0:10]'''

    # 读取数据文件名
    filenames = os.listdir(data_dir_name)
    # 为filenames根据仓库id排序
    id_filenames = dict()
    for filename in filenames:
        id_filenames[int(filename.split('_')[0])] = filename
    filenames = []
    for i in range(30):
        if i + 1 in id_filenames.keys():
            filenames.append(id_filenames[i + 1])

    churn_rate_list_all = []
    churn_rate_list = []
    point = int(life_time_point/step)
    for filename in filenames:
        with open(data_dir_name+'/'+filename,'r',encoding='utf-8')as f:
            user_count_list = f.readline().strip(',\n').split(',')[1:]
            churn_count_list = f.readline().strip(',\n').split(',')[1:]
        churn_rate = -1.0
        if life_time_point == 0:# life_time_point为 0 时获取的是第一次流失时的流失率
            for i in range(1,len(churn_count_list)):
                if int(churn_count_list[i]) != 0:
                    churn_rate = float(churn_count_list[i])/int(user_count_list[i-1])
                    break
        elif life_time_point == -1:# life_time_point为-1时获取的是最后一次流失时的流失率
            churn_rate = float(churn_count_list[-1])/int(user_count_list[-2])
        elif point < len(churn_count_list) and point > 0:
            churn_rate = float(churn_count_list[point])/int(user_count_list[point-1])
        churn_rate_list_all.append(churn_rate)
        if churn_rate >=0:
            churn_rate_list.append(churn_rate)
    return churn_rate_list_all,churn_rate_list


# 获取某一时间点下，不同社区的累计流失率
# data_dir_name: 存储流失率曲线数据的文件夹
# time_point: 寿命时间点,格式：%Y-%m-%d
# step: 必须和data_dir_name的step一致！！！
# 返回：两个列表，一个包含所有仓库数据（如果仓库create time>time_point,则对应流失率为-1），一个仅包含有效流失率数据
def getChurnRateLists2(data_dir_name,time_point,step=28):
    if time_point > '2022-01-01':
        time_point = '2022-01-01'

    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select id, created_at from churn_search_repos_final')
    results = cursor.fetchall()
    id_create_time = dict()
    for result in results:
        id_create_time[result[0]]=result[1][0:10]

    # 读取数据文件名
    filenames = os.listdir(data_dir_name)
    # 为filenames根据仓库id排序
    id_filenames = dict()
    for filename in filenames:
        id_filenames[int(filename.split('_')[0])] = filename
    filenames = []
    for i in range(30):
        if i + 1 in id_filenames.keys():
            filenames.append(id_filenames[i + 1])

    churn_rate_list_all = []
    churn_rate_list = []
    for filename in filenames:
        with open(data_dir_name+'/'+filename,'r',encoding='utf-8')as f:
            user_count_list = f.readline().strip(',\n').split(',')[1:]
            churn_count_list = f.readline().strip(',\n').split(',')[1:]
        churn_rate = -1.0
        id = int(filename.split('_')[0])
        create_time = id_create_time[id]
        if create_time < time_point:
            timedelta = datetime.datetime.strptime(time_point,fmt_MySQL)-datetime.datetime.strptime(create_time,fmt_MySQL)
            point = int(timedelta.days/step)
            if point > len(churn_count_list)-1:
                point = len(churn_count_list)-1
            churn_rate = float(churn_count_list[point]) / int(user_count_list[point - 1])
        churn_rate_list_all.append(churn_rate)
        if churn_rate >=0:
            churn_rate_list.append(churn_rate)
    return churn_rate_list_all,churn_rate_list


# 对data_list进行描述性分析
# filename: 存储的文件名，如果为空则不存储
def descriptiveAnalysis(data_list,filename=''):
    data_array = np.array(data_list)
    '''val_count = dict()
    for data in data_list:
        if data not in val_count.keys():
            val_count[data]=0
        val_count[data]+=1
    mode_val = data_list[0]   #众数
    for key in val_count.keys():
        if val_count[key]>val_count[mode_val]:
            mode_val = val_count'''
    mean_val = float("{0:.4f}".format(np.mean(data_array)))  # 均值
    median_val = float("{0:.4f}".format(np.median(data_array)))    # 中位数
    max_val = float("{0:.4f}".format(np.max(data_array)))  # 最大值
    min_val = float("{0:.4f}".format(np.min(data_array)))  # 最小值
    std_val = float("{0:.4f}".format(np.std(data_array)))  # 标准差
    var_val = float("{0:.4f}".format(np.var(data_array)))  # 方差
    Q1_val = float("{0:.4f}".format(np.percentile(data_array,25)))     # 第一四分位数
    Q3_val = float("{0:.4f}".format(np.percentile(data_array,75)))     # 第三四分位数
    IQR_val = float("{0:.4f}".format(Q3_val - Q1_val))   # 四分位距
    s = pd.Series(data_list)
    kurt_val = float("{0:.4f}".format(s.kurt()))     # 峰度
    skew_val = float("{0:.4f}".format(s.skew()))     # 偏度
    name_list = ['minimum value','maximum value','mean value','median value','standard deviation','variance',
                 'Q1','Q3','IQR','kurtosis','skewness']
    value_list = [min_val,max_val,mean_val,median_val,std_val,var_val,Q1_val,Q3_val,IQR_val,kurt_val,skew_val]
    if filename != '':
        with open(filename,'w',encoding='utf-8')as f:
            f.write('name,value,\n')
            for i in range(len(name_list)):
                f.write(name_list[i]+','+str(value_list[i])+',\n')

    print('描述性分析结果如下：')
    table = PrettyTable(['name','value'])
    for i in range(len(name_list)):
        table.add_row([name_list[i],value_list[i]])
    print(table)



# 正态分布的概率密度函数
#   x      数据集中的某一具体测量值
#   miu     数据集的平均值，反映测量值分布的集中趋势
#   sigma  数据集的标准差，反映测量值分布的分散程度
def normfun(x, miu, sigma):
    fx = np.exp(-((x - miu) ** 2) / (2 * sigma ** 2)) / (sigma * np.sqrt(2 * np.pi))
    return fx


#绘制流失率的频率分布直方图
def drawRateHistogram(data_list,title='流失率频率分布直方图',figname=''):
    data_array = np.array(data_list)
    mean_val = np.mean(data_array)
    std_val = np.std(data_array)
    min_val = np.min(data_array)
    max_val = np.max(data_array)
    x_step = 0.001
    x = np.arange(min_val*0.95,max_val*1.05,x_step)
    y = normfun(x,mean_val,std_val)

    plt.figure(figsize=(7,4))

    plt.hist(data_list, bins=30, rwidth=0.9, density=True,range=(0.0,1.0),
             color='#6699DD',alpha=0.9)
             # color='cornflowerblue',alpha=0.7)

    plt.plot(x,y, linewidth=2, marker=',',color='coral',label='标准正态分布曲线')
    x_ticks = np.arange(0.0,1.05,0.1)
    plt.xticks(x_ticks)
    plt.legend(loc='upper right')
    # plt.title(title)
    if figname!='':
        plt.savefig(figname,dpi=300,bbox_inches = 'tight')
    plt.show()


def drawBoxplot(churn_rate_lists,y_labels,title='流失率箱线图',figname=''):
    height = max(2,len(churn_rate_lists))
    plt.figure(figsize=(9,height))
    x_ticks = np.arange(0.0,1.05,0.1)
    plt.boxplot(churn_rate_lists,labels=y_labels,vert=False)
    plt.title(title)
    plt.xticks(x_ticks)
    if figname != '':
        plt.savefig(figname)
    plt.show()


# 根据时间段获取所有社区的累计流失率
# startDay:筛选时间段的起始日期（包含）
# endDay:筛选时间段的终止日期（不含）
# churn_limit_lists: 不同社区的流失期限数据列表，每个列表每行格式为：起始时间,流失期限
# output_file: 存储数据的文件名
# step:统计步长，为7的倍数（若不是7的倍数则选择最近值）
def getChurnRatesByPeriod(startDay,endDay,churn_limit_lists,output_file,step=7):
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select id,repo_id,created_at from churn_search_repos_final')
    results = cursor.fetchall()

    if step < 7:
        step = 7
    elif step % 7 != 0:
        if step - int(step / 7) * 7 < int(step / 7) * 7 + 7 - step:
            step = int(step / 7) * 7
        else:
            step = int(step / 7) * 7 + 7

    id_churn_rate = dict()

    filename = output_file.split('.')[0] + '_' + startDay + '_' + endDay + '.' + output_file.split('.')[1]
    with open(filename, 'w', encoding='utf-8')as f:
        line = 'id,churn_rate,\n'
        f.write(line)
    f.close()

    for result in results:
        id = result[0]
        repo_id = result[1]
        create_time = result[2][0:10]
        if datetime.datetime.strptime(startDay,fmt_MySQL)<datetime.datetime.strptime(create_time,fmt_MySQL):
            start_day = create_time
        else:
            start_day = startDay
        end_day = (datetime.datetime.strptime(start_day, fmt_MySQL) + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
        print(str(id)+' --',start_day,'-', end_day)

        timedelta = datetime.datetime.strptime(endDay, fmt_MySQL) - datetime.datetime.strptime(start_day, fmt_MySQL)
        period_weeks = int(timedelta.days / 7)  # 时间段总周数

        churn_limit_list = churn_limit_lists[id-1]

        all_user_list = []  # 每个统计间隔内所有用户列表
        churn_user_list = []  # 每个统计间隔内流失用户列表
        step_list = []
        user_count_list = []  # 不同统计间隔的所有用户数
        churn_count_list = []  # 不同统计间隔的流失用户数，当前间隔的流失用户数/上一间隔的所有用户数=流失率
        user_inactive_weeks = dict()

        for i in range(period_weeks):
            week_user_list = getRepoUserList(repo_id, startDay=start_day, endDay=end_day)
            churn_limit = 53
            for j in range(len(churn_limit_list) - 1, -1, -1):
                if churn_limit_list[j][0] <= start_day:
                    churn_limit = int(churn_limit_list[j][1])
                    break
            for user_id in user_inactive_weeks.keys():
                if user_id in week_user_list and user_inactive_weeks[user_id] > 0:  # 上周无活动，本周有活动
                    user_inactive_weeks[user_id] = 0
                    if user_id in churn_user_list:  # 流失用户回归
                        churn_user_list.remove(user_id)
                elif user_id not in week_user_list:  # 本周没有活动
                    user_inactive_weeks[user_id] += 1
                    if user_inactive_weeks[user_id] == churn_limit and user_id not in churn_user_list:
                        churn_user_list.append(user_id)

            for user_id in week_user_list:
                if user_id not in all_user_list:
                    # newcomer_count += 1
                    all_user_list.append(user_id)  # all_user_list只增不减
                if user_id not in user_inactive_weeks.keys():
                    user_inactive_weeks[user_id] = 0

            if step == 7 or (i + 1) * 7 % step == 0:
                user_count_list.append(len(all_user_list))
                churn_count_list.append(len(churn_user_list))
                step_list.append(i * 7)
                # newcomer_count_list.append(newcomer_count)
                # newcomer_count = 0

            start_day = end_day
            end_day = (datetime.datetime.strptime(start_day, fmt_MySQL) + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
            if end_day > endDay:
                end_day = endDay
            print(start_day, end_day)
        if len(user_count_list)>=2:
            churn_rate = "{0:.4f}".format(float(churn_count_list[-1])/user_count_list[-2])
        else:
            churn_rate = 0.0
        print(str(id)+':',churn_rate)
        id_churn_rate[id]=churn_rate
        with open(filename, 'a+', encoding='utf-8')as f:
            line = str(result[0])+','+str(churn_rate)+',\n'
            f.write(line)
        f.close()

    return id_churn_rate


def drawHistogramByLifetime(life_time_point):
    churn_rate_list_all, churn_rate_list = getChurnRateLists1(
        'E:/bysj_project/churn_rate_with_newcomer_28/churn_rate_data_0', life_time_point=life_time_point, step=step)
    drawRateHistogram(churn_rate_list, '仓库' + str(life_time_point) + '天时的流失率频率分布图')
    return churn_rate_list


def drawHistogramByTime(time_point):
    churn_rate_list_all, churn_rate_list = getChurnRateLists2(
        'E:/bysj_project/churn_rate_with_newcomer_28/churn_rate_data_0', time_point=time_point, step=step)
    drawRateHistogram(churn_rate_list, time_point + '时不同仓库的流失率频率分布图')
    return churn_rate_list


def getChurnRatesByFile(filename,startDay,endDay):
    filename = filename.split('.')[0] + '_' + startDay + '_' + endDay + '.' + filename.split('.')[1]
    churn_rate_list = []
    filenames = os.listdir('E:/bysj_project/period_churn_rate_data')
    if filename.split('/')[-1] not in filenames:
        print('filename error!')
    else:
        with open(filename, 'r', encoding='utf-8')as f:
            f.readline()
            for line in f.readlines():
                churn_rate = float(line.split(',')[1])
                if churn_rate > 0.0:
                    churn_rate_list.append(churn_rate)
    return churn_rate_list


if __name__ == '__main__':
    step = 28

    '''# ① 绘制相同寿命长度的仓库流失率频率分布图
    life_time_point = 0
    churn_rate_list1=drawHistogramByLifetime(life_time_point)
    life_time_point = 365
    churn_rate_list2=drawHistogramByLifetime(life_time_point)
    life_time_point = 730
    churn_rate_list3=drawHistogramByLifetime(life_time_point)
    life_time_point = 1000
    churn_rate_list4=drawHistogramByLifetime(life_time_point)'''

    '''# ② 绘制相同时间点下仓库流失率频率分布图
    time_point = '2019-01-01'
    churn_rate_list1=drawHistogramByTime(time_point)
    time_point = '2020-01-01'
    churn_rate_list2 = drawHistogramByTime(time_point)
    time_point = '2021-01-01'
    churn_rate_list3 = drawHistogramByTime(time_point)
    time_point = '2022-01-01'
    churn_rate_list4 = drawHistogramByTime(time_point)'''

    '''# ③ 获取相同时间段不同仓库的流失率
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
    id_churn_rate_1 = getChurnRatesByPeriod('2017-01-01', '2018-01-01', churn_limit_lists,
                                            'E:/bysj_project/period_churn_rate_data/churn_rate_data.csv', step=step)
    id_churn_rate_2 = getChurnRatesByPeriod('2018-01-01','2019-01-01',churn_limit_lists,
                                            'E:/bysj_project/period_churn_rate_data/churn_rate_data.csv',step=step)
    # id_churn_rate_3 = getChurnRatesByPeriod('2019-01-01', '2020-01-01', churn_limit_lists,
    #                                         'E:/bysj_project/period_churn_rate_data/churn_rate_data.csv', step=step)
    print(id_churn_rate_1)
    print(id_churn_rate_2)
    # print(id_churn_rate_3)'''


    # ④ 绘制相同时间段不同社区流失率频率分布图
    filename = 'E:/bysj_project/period_churn_rate_data/churn_rate_data.csv'
    y_labels = []
    startDay = '2017-01-01'
    endDay = '2019-01-01'
    y_labels.append(startDay+' ~ '+endDay)
    churn_rate_list_1 = getChurnRatesByFile(filename,startDay,endDay)
    drawRateHistogram(churn_rate_list_1, startDay + '~' + endDay + '期间不同社区流失率频率分布图')
    startDay = '2018-01-01'
    endDay = '2020-01-01'
    y_labels.append(startDay + ' ~ ' + endDay)
    churn_rate_list_2 = getChurnRatesByFile(filename,startDay,endDay)
    drawRateHistogram(churn_rate_list_2, startDay + '~' + endDay + '期间不同社区流失率频率分布图')
    startDay = '2019-01-01'
    endDay = '2021-01-01'
    y_labels.append(startDay + ' ~ ' + endDay)
    churn_rate_list_3 = getChurnRatesByFile(filename,startDay,endDay)
    drawRateHistogram(churn_rate_list_3, startDay + '~' + endDay + '期间不同社区流失率频率分布图')
    startDay = '2020-01-01'
    endDay = '2022-01-01'
    y_labels.append(startDay + ' ~ ' + endDay)
    churn_rate_list_4 = getChurnRatesByFile(filename, startDay, endDay)
    drawRateHistogram(churn_rate_list_4, startDay + '~' + endDay + '期间不同社区流失率频率分布图')


    churn_rate_lists = [churn_rate_list_1,churn_rate_list_2,churn_rate_list_3,churn_rate_list_4]
    # y_labels = ['2019-01-01','2020-01-01','2021-01-01','2022-01-01']
    # ⑤ 绘制流失率箱线图
    drawBoxplot(churn_rate_lists,y_labels)

    # ⑥ 描述性分析
    descriptiveAnalysis(churn_rate_list_1,'C:/Users/cxy/Desktop/test/descriptive_analysis_test_1.csv')
    descriptiveAnalysis(churn_rate_list_2, 'C:/Users/cxy/Desktop/test/descriptive_analysis_test_2.csv')
    descriptiveAnalysis(churn_rate_list_3, 'C:/Users/cxy/Desktop/test/descriptive_analysis_test_3.csv')
    descriptiveAnalysis(churn_rate_list_4, 'C:/Users/cxy/Desktop/test/descriptive_analysis_test_4.csv')