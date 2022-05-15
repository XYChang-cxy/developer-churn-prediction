import os
from churn_data_analysis.draw_time_sequence_chart import dbHandle
import datetime
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from churn_data_analysis.draw_return_visit_curve import getRepoUserList, getRepoUserRoleDict
from churn_data_analysis.developer_collaboration_network import *
from churn_data_analysis.draw_activity_curve import getUserActivity
from churn_data_analysis.churn_rate_analysis import drawBoxplot
from churn_data_analysis.churner_classification_analysis import *

matplotlib.rcParams['font.sans-serif'] = ['KaiTi']
matplotlib.rcParams['axes.unicode_minus'] = False
time_fmt = '%Y-%m-%d'


# 根据活跃度、合并PR数、节点加权度、时间、角色等指标划分流失开发者，并绘制曲线
# repo_id: 仓库id
# metric: 划分流失开发者指标：0--平均活跃度、1--合并PR数、2--平均节点加权度、3--留存时间、4--角色
# user_filename: 仓库对应的用户id数据文件名，用于获取每周流失用户和活动用户
# user_data_filename: 仓库对应的用户活跃度等数据文件名，用于计算指标
# threshold_value: 划分流失开发者的指标对应阈值（实际值）
# time_window: 求一段时间平均（加权平均）重要开发者占比的时间窗口，默认为365（天）
# fig_name_1: 流失率曲线图像保存的文件名,若为空字符串则不保存
# fig_name_2: 重要流失开发者占比曲线图像的文件名，若为空字符串则不保存
# step: 与其他参数对应文件一致，默认28
# if_draw: 是否绘制图像，仅当该参数是True时fig_name_1和fig_name_2才有意义
def getChurnerCompositionCurveByMetric(repo_id, user_filename, user_data_filename, threshold_value, churn_limit_list=None,
                                       time_window=365,fig_name_1='',fig_name_2='', metric=0, step=28,
                                       if_draw_1=True,if_draw_2=False):
    if churn_limit_list is None:
        churn_limit_list = []
    churn_id_lists = []  # 每个step流失开发者列表
    active_id_lists = []  # 每个step内活动开发者列表
    step_list = []  # 不同文件的step不一定一致，统一为: step,2*step,3*step...

    # 获取社区的创建时间
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select created_at from churn_search_repos_final where repo_id = ' + str(repo_id))
    result = cursor.fetchone()
    create_time = result[0][0:10]
    end_time = '2022-01-01'

    # 获取每step的流失用户和活动用户
    with open(user_filename, 'r', encoding='utf-8')as f:
        f.readline()
        for line in f.readlines():
            contents = line.split(',')
            step_list.append(int(contents[0]) + 7)  # 用户文件的时间列表是从step-7开始的
            churn_id_lists.append(contents[5].split(' ')[0:-1])
            active_id_lists.append(contents[4].split(' ')[0:-1])
    f.close()

    type_count = 8  # user_data_file的数据类型数
    user_time = dict()  # 用户留存时间
    user_metric_value = dict()  # 用户的metric值，可能是sum，也可能是单独的value（角色）
    churn_rate_list = []  # 总流失率数据
    imp_churn_rate_list = []  # 重要流失开发者流失率
    other_churn_rate_list = []  # 其他流失开发者流失率

    with open(user_data_filename, 'r', encoding='utf-8')as f:
        f.readline()
        line_index = 0  # user_data_file的行数下标
        for line in f.readlines():
            if line_index % type_count == 0:  # time as metric
                tmp_list = line.split(',')[1].strip(' ').split(' ')
                for item in tmp_list:
                    user_id = item.split(':')[0]
                    user_time[user_id] = int(item.split(':')[1])
                    if metric == 3:  # 以时间metric
                        user_metric_value[user_id] = int(item.split(':')[1])
            elif metric == 4 and line_index % type_count == 1:  # role as metric
                tmp_list = line.split(',')[1].strip(' ').split(' ')
                for item in tmp_list:
                    user_id = item.split(':')[0]
                    role = item.split(':')[1]
                    if role == 'NONE':
                        value = 0
                    elif role == 'CONTRIBUTOR':
                        value = 1
                    elif role == 'COLLABORATOR':
                        value = 2
                    elif role == 'MEMBER':
                        value = 3
                    else:
                        value = 4
                    user_metric_value[user_id] = value
            elif (metric == 0 and line_index % type_count == 2) or (  # activity as metric
                    metric == 1 and line_index % type_count == 5) or (  # merged pull as metric
                    metric == 2 and line_index % type_count == 6):  # weighted degree as metric
                tmp_list = line.split(',')[1].strip(' ').split(' ')
                for item in tmp_list:
                    user_id = item.split(':')[0]
                    value = float(item.split(':')[1])
                    if user_id in user_metric_value.keys():
                        user_metric_value[user_id] += value
                    else:
                        user_metric_value[user_id] = value
            elif line_index % type_count == 7:  # 统计完一个step的所有用户metric数据，然后计算当前step流失率
                step_index = int(line_index / type_count)

                # 获取当前step对应的流失期限
                churn_limit = 53
                start_day = (
                        datetime.datetime.strptime(create_time, time_fmt) + datetime.timedelta(days=step * step_index)
                ).strftime(time_fmt)
                for j in range(len(churn_limit_list) - 1, -1, -1):
                    if churn_limit_list[j][0] <= start_day:
                        churn_limit = int(churn_limit_list[j][1])
                        break

                if len(churn_id_lists[step_index]) == 0:
                    churn_rate_list.append(0.0)
                    imp_churn_rate_list.append(0.0)
                    other_churn_rate_list.append(0.0)
                else:  # 分子不为零
                    index = step_index - int(churn_limit * 7 / step)
                    if index < 0:
                        index = 0
                    max_exist_count = 0  # step>7时可能找不到准确的区间，则找近似区间
                    max_exist_users = []
                    max_exist_index = step_index - int(churn_limit * 7 / step)  # 近似区间对应index
                    if_find_period = True  # 是否准确找到分母区间
                    if len(churn_id_lists[step_index]) > 0:  # 分子大于零，需要寻找准确的分母区间
                        if_find_period = False
                        for k in range(step_index - int(churn_limit * 7 / step) + 9,
                                       step_index - int(churn_limit * 7 / step) - 10,
                                       -1):  ##############################
                            if k < 0 or k >= len(active_id_lists):
                                continue
                            exist_count = 0
                            exist_users = []
                            for user_id in churn_id_lists[step_index]:
                                if user_id in active_id_lists[k]:
                                    exist_count += 1
                                    exist_users.append(user_id)
                            if exist_count > max_exist_count:
                                max_exist_index = k
                                max_exist_count = exist_count
                                max_exist_users = exist_users.copy()
                            if exist_count == len(churn_id_lists[step_index]):
                                index = k
                                if_find_period = True
                                break
                        if not if_find_period:
                            index = max_exist_index
                            step_churner_list = max_exist_users.copy()  # 当前step内（在active_id_lists[index]出现的）流失人员列表
                            print(step_index, index - (step_index - int(churn_limit * 7 / step)), max_exist_count,
                                  len(churn_id_lists[step_index]),
                                  "{0:.3f}".format(100 * float(max_exist_count) / len(
                                      churn_id_lists[step_index])) + '%')  #########################
                        else:
                            step_churner_list = churn_id_lists[step_index].copy()
                    if len(active_id_lists[index]) == 0:  # 分母为 0
                        churn_rate_list.append(0.0)
                        imp_churn_rate_list.append(0.0)
                        other_churn_rate_list.append(0.0)
                    else:
                        churn_rate_list.append(float(len(step_churner_list)) / len(active_id_lists[index]))
                        imp_count = 0
                        for user_id in step_churner_list:
                            if metric == 0 or metric == 2: # 平均活跃度或平均节点加权度
                                user_time_step = float(user_time[user_id] * 7) / step
                                metric_value = float(user_metric_value[user_id]) / user_time_step
                            else:
                                metric_value = user_metric_value[user_id]
                            if metric_value >= threshold_value:
                                imp_count += 1
                            user_metric_value[user_id] = 0  # 流失后数据清零!!!!!!
                        imp_churn_rate_list.append(float(imp_count) / len(active_id_lists[index]))
                        other_churn_rate_list.append(float(len(step_churner_list)-imp_count) / len(active_id_lists[index]))
            line_index += 1
    f.close()

    if if_draw_1:
        metric_list = [
            'average activity',
            'merged PR count',
            'average degree',
            'retain time',
            'role'
        ]

        plt.figure(figsize=(10, 5))
        plt.plot(step_list, churn_rate_list, label='开发者流失率', linewidth=1, color='limegreen', marker=',')
        plt.fill_between(step_list,churn_rate_list,color='limegreen',alpha=0.2)
        plt.plot(step_list, imp_churn_rate_list, label='重要开发者流失率', linewidth=1, color='orange', marker=',')
        plt.fill_between(step_list, imp_churn_rate_list, color='orange', alpha=0.3)
        plt.title(
            '社区(repo_id = ' + str(repo_id) + ')' + create_time + '~' + end_time + '期间' + '(重要）开发者流失率曲线('
            + metric_list[metric]
            + ',step=' + str(step) + ')')
        if fig_name_1 != '':
            plt.savefig(fig_name_1)
        plt.show()

    imp_rate_list = []
    time_list = []
    j = 0
    rate_sum = 0.0  # 加权和
    churn_rate_sum = 0.0  # 权值和
    for i in range(len(step_list)):
        if (j + 1) * step <= time_window:
            if churn_rate_list[i] != 0:
                churn_rate_sum += churn_rate_list[i]
                rate_sum += imp_churn_rate_list[i]
            j += 1
        else:
            if churn_rate_sum == 0:
                imp_rate_list.append(0.0)
            else:
                imp_rate_list.append(100 * float(rate_sum) / churn_rate_sum)  # 占比的加权平均值
            time_list.append(int((i - float(j) / 2) * step))
            j = 1
            rate_sum = imp_churn_rate_list[i]
            churn_rate_sum = churn_rate_list[i]
    if j > float(time_window) / (step * 2):
        if churn_rate_sum == 0:
            imp_rate_list.append(0.0)
        else:
            imp_rate_list.append(100 * float(rate_sum) / churn_rate_sum)  # 占比的加权平均值
        time_list.append(time_list[-1] + int(time_window / step) * step)

    print(time_list)
    if if_draw_2:
        plt.figure(figsize=(10, 5))
        plt.plot(time_list, imp_rate_list, label='重要流失开发者比例', linewidth=1, color='deepskyblue', marker=',')
        plt.xlim([0,step_list[-1]])
        plt.ylim([0,100])
        plt.title(
            '社区(repo_id = ' + str(repo_id) + ')' + create_time + '~' + end_time + '期间' + '重要流失开发者比例曲线(metric='
            + metric_list[metric] + ')')
        if fig_name_2 != '':
            plt.savefig(fig_name_2)
        plt.show()
    return step_list,churn_rate_list,imp_churn_rate_list, time_list, imp_rate_list


# 根据score(由活跃度等metric计算所得)划分流失开发者，并绘制曲线
# repo_id: 仓库id
# user_filename: 仓库对应的用户id数据文件名，用于获取每周流失用户和活动用户
# user_data_filename: 仓库对应的用户活跃度等数据文件名，用于计算score
# threshold_list: 划分流失开发者的5个metric的阈值列表
# time_window: 求一段时间平均（加权平均）重要开发者占比的时间窗口，默认为365（天）
# fig_name_1: 流失率曲线图像保存的文件名,若为空字符串则不保存
# fig_name_2: 重要流失开发者占比曲线图像的文件名，若为空字符串则不保存
# step: 与其他参数对应文件一致，默认28
# if_draw: 是否绘制图像，仅当该参数是True时fig_name_1和fig_name_2才有意义
def getChurnerCompositionCurveByScore(repo_id, user_filename, user_data_filename, threshold_list, churn_limit_list=None,
                                      time_window=365,fig_name_1='',fig_name_2='',step=28,
                                      if_draw_1=True,if_draw_2=False):
    if churn_limit_list is None:
        churn_limit_list = []
    churn_id_lists = []  # 每个step流失开发者列表
    active_id_lists = []  # 每个step内活动开发者列表
    step_list = []  # 不同文件的step不一定一致，统一为: step,2*step,3*step...

    # 获取社区的创建时间
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select created_at from churn_search_repos_final where repo_id = ' + str(repo_id))
    result = cursor.fetchone()
    create_time = result[0][0:10]
    end_time = '2022-01-01'

    # 获取每step的流失用户和活动用户
    with open(user_filename, 'r', encoding='utf-8')as f:
        f.readline()
        for line in f.readlines():
            contents = line.split(',')
            step_list.append(int(contents[0]) + 7)  # 用户文件的时间列表是从step-7开始的
            churn_id_lists.append(contents[5].split(' ')[0:-1])
            active_id_lists.append(contents[4].split(' ')[0:-1])
    f.close()

    type_count = 8  # user_data_file的数据类型数
    user_time = dict()  # 用户留存时间
    user_activity_sum = dict()
    user_degree_sum = dict()
    user_merged_pr = dict()
    user_role = dict()
    churn_rate_list = []  # 总流失率数据
    imp_churn_rate_list = []  # 重要流失开发者流失率
    other_churn_rate_list = []  # 其他流失开发者流失率

    with open(user_data_filename, 'r', encoding='utf-8')as f:
        f.readline()
        line_index = 0  # user_data_file的行数下标
        for line in f.readlines():
            if line_index % type_count == 0:  # time
                tmp_list = line.split(',')[1].strip(' ').split(' ')
                for item in tmp_list:
                    user_id = item.split(':')[0]
                    user_time[user_id] = int(item.split(':')[1])
            elif line_index % type_count == 1:  # role
                tmp_list = line.split(',')[1].strip(' ').split(' ')
                for item in tmp_list:
                    user_id = item.split(':')[0]
                    role = item.split(':')[1]
                    if role == 'NONE':
                        value = 0
                    elif role == 'CONTRIBUTOR':
                        value = 1
                    elif role == 'COLLABORATOR':
                        value = 2
                    elif role == 'MEMBER':
                        value = 3
                    else:
                        value = 4
                    user_role[user_id] = value
            elif line_index % type_count == 2:  # activity
                tmp_list = line.split(',')[1].strip(' ').split(' ')
                for item in tmp_list:
                    user_id = item.split(':')[0]
                    value = float(item.split(':')[1])
                    if user_id in user_activity_sum.keys():
                        user_activity_sum[user_id] += value
                    else:
                        user_activity_sum[user_id] = value
            elif line_index % type_count == 5: # merged pull
                tmp_list = line.split(',')[1].strip(' ').split(' ')
                for item in tmp_list:
                    user_id = item.split(':')[0]
                    value = float(item.split(':')[1])
                    if user_id in user_merged_pr.keys():
                        user_merged_pr[user_id] += value
                    else:
                        user_merged_pr[user_id] = value
            elif line_index % type_count == 6:
                tmp_list = line.split(',')[1].strip(' ').split(' ')
                for item in tmp_list:
                    user_id = item.split(':')[0]
                    value = float(item.split(':')[1])
                    if user_id in user_degree_sum.keys():
                        user_degree_sum[user_id] += value
                    else:
                        user_degree_sum[user_id] = value
            elif line_index % type_count == 7:  # 统计完一个step的所有用户metric数据，然后计算当前step流失率
                step_index = int(line_index / type_count)

                # 获取当前step对应的流失期限
                churn_limit = 53
                start_day = (
                        datetime.datetime.strptime(create_time, time_fmt) + datetime.timedelta(days=step * step_index)
                ).strftime(time_fmt)
                for j in range(len(churn_limit_list) - 1, -1, -1):
                    if churn_limit_list[j][0] <= start_day:
                        churn_limit = int(churn_limit_list[j][1])
                        break

                if len(churn_id_lists[step_index]) == 0:
                    churn_rate_list.append(0.0)
                    imp_churn_rate_list.append(0.0)
                    other_churn_rate_list.append(0.0)
                else:  # 分子不为零
                    index = step_index - int(churn_limit * 7 / step)
                    if index < 0:
                        index = 0
                    max_exist_count = 0  # step>7时可能找不到准确的区间，则找近似区间
                    max_exist_users = []
                    max_exist_index = step_index - int(churn_limit * 7 / step)  # 近似区间对应index
                    if_find_period = True  # 是否准确找到分母区间
                    if len(churn_id_lists[step_index]) > 0:  # 分子大于零，需要寻找准确的分母区间
                        if_find_period = False
                        for k in range(step_index - int(churn_limit * 7 / step) + 9,
                                       step_index - int(churn_limit * 7 / step) - 10,
                                       -1):  ##############################
                            if k < 0 or k >= len(active_id_lists):
                                continue
                            exist_count = 0
                            exist_users = []
                            for user_id in churn_id_lists[step_index]:
                                if user_id in active_id_lists[k]:
                                    exist_count += 1
                                    exist_users.append(user_id)
                            if exist_count > max_exist_count:
                                max_exist_index = k
                                max_exist_count = exist_count
                                max_exist_users = exist_users.copy()
                            if exist_count == len(churn_id_lists[step_index]):
                                index = k
                                if_find_period = True
                                break
                        if not if_find_period:
                            index = max_exist_index
                            step_churner_list = max_exist_users.copy()  # 当前step内（在active_id_lists[index]出现的）流失人员列表
                            print(step_index, index - (step_index - int(churn_limit * 7 / step)), max_exist_count,
                                  len(churn_id_lists[step_index]),
                                  "{0:.3f}".format(100 * float(max_exist_count) / len(
                                      churn_id_lists[step_index])) + '%')  #########################
                        else:
                            step_churner_list = churn_id_lists[step_index].copy()
                    if len(active_id_lists[index]) == 0:  # 分母为 0
                        churn_rate_list.append(0.0)
                        imp_churn_rate_list.append(0.0)
                        other_churn_rate_list.append(0.0)
                    else:
                        churn_rate_list.append(float(len(step_churner_list)) / len(active_id_lists[index]))
                        imp_count = 0
                        for user_id in step_churner_list:
                            user_time_step = float(user_time[user_id] * 7) / step
                            activity_avg = float(user_activity_sum[user_id]) / user_time_step
                            degree_avg = float(user_degree_sum[user_id]) / user_time_step
                            values = []
                            values.append(activity_avg)
                            values.append(user_merged_pr[user_id])
                            values.append(degree_avg)
                            values.append(user_time[user_id])
                            values.append(user_role[user_id])
                            # 流失后以下用户累计数据清零
                            user_activity_sum[user_id] = 0.0
                            user_merged_pr[user_id] = 0
                            user_degree_sum[user_id] = 0
                            score = 0
                            for j in range(len(values)):
                                if values[j] >= threshold_list[j]:
                                    score += 1
                            if score > 0:
                                imp_count += 1
                        imp_churn_rate_list.append(float(imp_count) / len(active_id_lists[index]))
                        other_churn_rate_list.append(float(len(step_churner_list)-imp_count) / len(active_id_lists[index]))
            line_index += 1
    f.close()
    if if_draw_1:
        plt.figure(figsize=(10, 5))
        plt.plot(step_list, churn_rate_list, label='开发者流失率', linewidth=1, color='limegreen', marker=',')
        plt.fill_between(step_list, churn_rate_list, color='limegreen', alpha=0.2)
        plt.plot(step_list, imp_churn_rate_list, label='重要开发者流失率', linewidth=1, color='orangered', marker=',')
        plt.fill_between(step_list, imp_churn_rate_list, color='orangered', alpha=0.3)
        plt.title(
            '社区(repo_id = ' + str(repo_id) + ')' + create_time + '~' + end_time + '期间' + '(重要）开发者流失率曲线(metric=score)'
            + ',step=' + str(step) + ')')
        if fig_name_1 != '':
            plt.savefig(fig_name_1)
        plt.show()

    imp_rate_list = []
    time_list = []
    j = 0
    rate_sum = 0.0  # 加权和
    churn_rate_sum = 0.0  # 权值和
    for i in range(len(step_list)):
        if (j + 1) * step <= time_window:
            if churn_rate_list[i] != 0:
                churn_rate_sum += churn_rate_list[i]
                rate_sum += imp_churn_rate_list[i]
            j += 1
        else:
            if churn_rate_sum == 0:
                imp_rate_list.append(0.0)
            else:
                imp_rate_list.append(100 * float(rate_sum) / churn_rate_sum)  # 占比的加权平均值
            time_list.append(int((i - float(j) / 2) * step))
            j = 1
            rate_sum = imp_churn_rate_list[i]
            churn_rate_sum = churn_rate_list[i]
    if j > float(time_window) / (step * 2):
        if churn_rate_sum == 0:
            imp_rate_list.append(0.0)
        else:
            imp_rate_list.append(100 * float(rate_sum) / churn_rate_sum)  # 占比的加权平均值
        time_list.append(time_list[-1] + int(time_window / step) * step)

    print(time_list)
    if if_draw_2:
        plt.figure(figsize=(10, 5))
        plt.plot(time_list, imp_rate_list, label='重要流失开发者比例', linewidth=1, color='deepskyblue', marker=',')
        plt.xlim([0, step_list[-1]])
        plt.ylim([0, 100])
        plt.title(
            '社区(repo_id = ' + str(repo_id) + ')' + create_time + '~' + end_time + '期间' + '重要流失开发者比例曲线(metric=score)')
        if fig_name_2 != '':
            plt.savefig(fig_name_2)
        plt.show()
    return step_list, churn_rate_list, imp_churn_rate_list, time_list, imp_rate_list


# 根据5种metric和score分别为每个社区绘制重要开发者流失率曲线，并统一绘制重要流失开发者占比曲线（6种划分合并），存储图像到指定目录
# user_dir: 存储每周用户id数据的文件夹
# user_data_dir: 存储每周用户各类数据的文件夹
# save_dir:存储各类图像的总文件夹
# churn_limit_lists:每个仓库的流失期限
# threshold_filename: 各个仓库不同数据阈值文件
def drawChurnerCompositionCurveForRepos(user_dir,user_data_dir,save_dir,churn_limit_lists,threshold_filename,step=28):
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select id,repo_id,created_at from churn_search_repos_final')
    results = cursor.fetchall()

    filenames = os.listdir(user_dir)
    id_user_filename = dict()
    for filename in filenames:
        id_user_filename[int(filename.split('_')[0])] = filename

    filenames = os.listdir(user_data_dir)
    id_user_data_filename = dict()
    for filename in filenames:
        id_user_data_filename[int(filename.split('_')[0])] = filename

    id_threshold_lists = dict()
    with open(threshold_filename, 'r', encoding='utf-8')as f:
        f.readline()
        for line in f.readlines():
            threshold_list = []
            id = int(line.split(',')[0])
            threshold_list.append(float(line.split(',')[2]))
            threshold_list.append(float(line.split(',')[5]))
            threshold_list.append(float(line.split(',')[6]))
            threshold_list.append(float(line.split(',')[8]))
            threshold_list.append(float(line.split(',')[9]))
            id_threshold_lists[id] = threshold_list.copy()

    metric_dirs = [
        '0_activity',
        '1_merged_pull',
        '2_degree',
        '3_time',
        '4_role'
    ]
    colors = [
        'red',
        'darkorange',
        'cyan',
        'limegreen',
        'dodgerblue',
        'blue'
    ]
    score_dirname = 'SCORE'
    rate_dirname = 'composition_rate'
    time_window = 196

    for result in results:
        id = result[0]
        repo_id = result[1]
        create_time = result[2][0:10]
        end_time = '2022-01-01'
        user_filename = user_dir + '/' + id_user_filename[id]
        user_data_filename = user_data_dir + '/' + id_user_data_filename[id]
        threshold_list = id_threshold_lists[id]

        imp_rate_lists = []

        for metric in range(5):
            fig_name_1 = save_dir+'/'+metric_dirs[metric]+'/'+id_user_data_filename[id].replace('.csv','.png')
            threshold_value = threshold_list[metric]
            imp_rate_list = getChurnerCompositionCurveByMetric(repo_id,user_filename,user_data_filename,threshold_value,
                                                               churn_limit_lists[id-1],time_window=time_window,
                                                               fig_name_1=fig_name_1,metric=metric,step=step)[-1]
            imp_rate_lists.append(imp_rate_list.copy())
        fig_name_1 = save_dir + '/' + score_dirname + '/' + id_user_data_filename[id].replace('.csv', '.png')
        ret = getChurnerCompositionCurveByScore(repo_id,user_filename,user_data_filename,threshold_list,
                                                churn_limit_lists[id-1],time_window,fig_name_1,step=step)
        time_list = ret[3]
        imp_rate_list = ret[4]
        fig_name_2 = save_dir + '/' + rate_dirname + '/' + id_user_data_filename[id].replace('.csv', '.png')

        plt.figure(figsize=(10, 5))
        plt.plot(time_list, imp_rate_list, label='SCORE', linewidth=2, color=colors[-1], marker=',')
        for metric in range(5):
            plt.plot(time_list, imp_rate_lists[metric], label=metric_dirs[metric][2:], linewidth=2,
                     color=colors[metric], marker=',')
        plt.xlim([0, ret[0][-1]])
        plt.ylim([0, 100])
        plt.title(
            '社区(repo_id = ' + str(repo_id) + ')' + create_time + '~' + end_time + '期间' + '重要流失开发者比例曲线')
        plt.legend(loc="upper right")
        if fig_name_2 != '':
            plt.savefig(fig_name_2)
        plt.show()


if __name__ == '__main__':
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

    user_dir = 'E:/bysj_project/repo_users_by_period/data_28'
    user_data_dir = 'E:/bysj_project/repo_user_data_by_period/data_28'

    tmp_id_list = [2]
    filenames = os.listdir(user_dir)
    id_user_filename = dict()
    for filename in filenames:
        id_user_filename[int(filename.split('_')[0])] = filename
    filenames = os.listdir(user_data_dir)
    id_user_data_filename = dict()
    for filename in filenames:
        id_user_data_filename[int(filename.split('_')[0])] = filename

    threshold_dir = 'E:/bysj_project/repo_churner_classification'
    # threshold_filename = threshold_dir + '/' + 'repo_churner_threshold.csv'   # 对流失开发者进行划分
    threshold_filename = threshold_dir + '/' + 'repo_user_threshold.csv'   # 对所有开发者进行划分
    id_threshold_lists = dict()
    with open(threshold_filename,'r',encoding='utf-8')as f:
        f.readline()
        for line in f.readlines():
            threshold_list = []
            id = int(line.split(',')[0])
            threshold_list.append(float(line.split(',')[2]))
            threshold_list.append(float(line.split(',')[5]))
            threshold_list.append(float(line.split(',')[6]))
            threshold_list.append(float(line.split(',')[8]))
            threshold_list.append(float(line.split(',')[9]))
            id_threshold_lists[id] = threshold_list.copy()

    # save_dir = 'E:/bysj_project/repo_churner_classification/repo_churner_composition_curve'  # 对流失开发者进行划分
    save_dir = 'E:/bysj_project/repo_churner_classification/repo_churner_composition_curve_user'  # 对所有开发者进行划分
    drawChurnerCompositionCurveForRepos(user_dir,user_data_dir,save_dir,churn_limit_lists,threshold_filename,28)

    # for i in range(len(tmp_id_list)):
    #     id = tmp_id_list[i]
    #     user_filename = user_dir+'/'+id_user_filename[id]
    #     user_data_filename = user_data_dir + '/' + id_user_data_filename[id]
    #     dbObject = dbHandle()
    #     cursor = dbObject.cursor()
    #     cursor.execute('select repo_id from churn_search_repos_final where id = '+str(id))
    #     result = cursor.fetchone()
    #     repo_id = result[0]
    #
    #     metric = 0
    #     threshold_value = id_threshold_lists[id][metric]
    #     threshold_list = id_threshold_lists[id]
    #
    #     getChurnerCompositionCurveByMetric(repo_id,user_filename,user_data_filename,threshold_value,churn_limit_lists[id-1],
    #                                    metric=metric,step=28,time_window=196)
    #
    #     getChurnerCompositionCurveByScore(repo_id,user_filename,user_data_filename,threshold_list,churn_limit_lists[id-1],
    #                                   time_window=196,step=28)
    