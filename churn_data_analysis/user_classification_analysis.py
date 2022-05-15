# 该文件代码用户分析仓库所有人员的整体组成比例，分类时根据活跃度、参与时间、合作程度、角色等角度考虑
# 和churner_classification_analysis的功能类似，但划分主体不同，该代码对所有开发者进行统计求分类阈值
import os
from churn_data_analysis.draw_time_sequence_chart import dbHandle
import datetime
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from churn_data_analysis.draw_return_visit_curve import getRepoUserList,getRepoUserRoleDict
from churn_data_analysis.developer_collaboration_network import *
from churn_data_analysis.draw_activity_curve import getUserActivity
from churn_data_analysis.churn_rate_analysis import drawBoxplot
import churn_data_analysis.churner_classification_analysis as cca

matplotlib.rcParams['font.sans-serif'] = ['KaiTi']
matplotlib.rcParams['axes.unicode_minus'] = False
fmt_MySQL = '%Y-%m-%d'


# 获取仓库全部历史时间的某一类开发者数据的分布情况，并绘制剔除部分极大值后的分布图
# mode: 0--平均活跃度、1--累计commit数量、2--累计pull数量、3--累计merged_pr数量、
#       4--平均节点加权度、5--平均介数中心性、6--留存时间、7--承担的角色
# user_filename: 仓库对应的用户id数据文件名
# user_data_filename: 仓库对应的用户活跃度等数据文件名
# fig_name: 图像保存的文件名,若为空字符串则不保存
# threshold:0~100,对应百分位数作为阈值
# with_threshold: 图像是否添加阈值线，默认添加
# 返回值：对应数值列表和阈值
def getUserDataDistribution(repo_id,user_filename,user_data_filename,mode=0,step=28,threshold=None,
                               with_threshold=True,fig_name=''):
    if threshold == None:
        if mode >= 1 and mode <=3:
            threshold = 75
        else:
            threshold = 80

    user_time = dict()  # 用户留存时间
    user_metric_value = dict()  # 各种数量之和或者角色
    user_latest_value = []  # 开发者最新数据（流失时数据或最后一天数据）

    churn_id_lists = []
    retain_id_lists = []
    type_count = 8
    with open(user_filename,'r',encoding='utf-8')as f:
        f.readline()
        for line in f.readlines():
            if line.split(',')[5].strip(' ')!='':
                churn_id_lists.append(line.split(',')[5].strip(' ').split(' '))
            else:
                churn_id_lists.append([])
            if line.split(',')[3].strip(' ')!='':
                retain_id_lists.append(line.split(',')[3].strip(' ').split(' '))
            else:
                retain_id_lists.append([])
    retain_user_list = retain_id_lists[-1]  # 最后的留存人员列表

    with open(user_data_filename,'r',encoding='utf-8')as f:
        f.readline()
        i = 0
        for line in f.readlines():
            churn_user_list = churn_id_lists[int(i/type_count)]
            if i % type_count == 0:  # 时间
                tmp_list = line.split(',')[1].strip(' ').split(' ')
                for item in tmp_list:
                    user_time[item.split(':')[0]]=int(item.split(':')[1])
                if mode == 6:
                    for user_id in churn_user_list:
                        user_latest_value.append(user_time[user_id])
                    if int(i/type_count) == len(churn_id_lists)-1:
                        for user_id in retain_user_list:
                            user_latest_value.append(user_time[user_id])
            elif mode == 7 and i % type_count == 1:  # 角色
                tmp_list = line.split(',')[1].strip(' ').split(' ')
                for item in tmp_list:
                    user_id_str = item.split(':')[0]
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
                    user_metric_value[user_id_str] = value
                for user_id in churn_user_list:
                    user_latest_value.append(user_metric_value[user_id])
                if int(i / type_count) == len(churn_id_lists) - 1:
                    for user_id in retain_user_list:
                        user_latest_value.append(user_metric_value[user_id])
            elif (mode == 0 and i % type_count == 2) or (   # 活跃度
                    mode == 4 and i % type_count == 6) or (  # weighted degree
                    mode == 5 and i % type_count == 7):     # betweeness
                tmp_list = line.split(',')[1].strip(' ').split(' ')
                for item in tmp_list:
                    user_id_str = item.split(':')[0]
                    value = float(item.split(':')[1])
                    if user_id_str in user_metric_value.keys():
                        user_metric_value[user_id_str]+=value
                    else:
                        user_metric_value[user_id_str] = value
                for user_id in churn_user_list:
                    user_time_step = float(user_time[user_id]*7)/ step
                    user_latest_value.append(float(user_metric_value[user_id])/user_time_step)
                    user_metric_value[user_id] = 0.0  # 流失后数据清零
                if int(i / type_count) == len(churn_id_lists) - 1:
                    for user_id in retain_user_list:
                        user_time_step = float(user_time[user_id] * 7) / step
                        user_latest_value.append(float(user_metric_value[user_id]) / user_time_step)
            elif (mode == 1 and i % type_count == 3) or (  # commit
                    mode == 2 and i % type_count == 4) or (  # pull
                    mode == 3 and i % type_count == 5):     # merged pull
                tmp_list = line.split(',')[1].strip(' ').split(' ')
                for item in tmp_list:
                    user_id_str = item.split(':')[0]
                    value = float(item.split(':')[1])
                    if user_id_str in user_metric_value.keys():
                        user_metric_value[user_id_str] += value
                    else:
                        user_metric_value[user_id_str] = value
                for user_id in churn_user_list:
                    user_latest_value.append(float(user_metric_value[user_id]))
                    user_metric_value[user_id] = 0  # 流失后数据清零
                if int(i / type_count) == len(churn_id_lists) - 1:
                    for user_id in retain_user_list:
                        user_latest_value.append(float(user_metric_value[user_id]))
            i += 1
    data_list = user_latest_value.copy()
    data_list = sorted(data_list)
    data_array = np.array(data_list)
    if mode != 7:
        threshold_value = np.percentile(data_array,threshold)
        if mode >= 1 and mode <=3:  # 对于commit、PR和merged PR,阈值应比对应百分位数大
            threshold_value += 1
    else:
        count0 = 0
        count1 = 0
        for value in user_latest_value:
            if value == 0:
                count0 += 1
            elif value == 1:
                count1 += 1
        if count0 >= count1:
            threshold_value = 1
        else:
            threshold_value = 2

    if mode == 6: # 时间
        drop_line = np.percentile(data_array,90)*2.5
    else:
        drop_line = np.percentile(data_array,90)*5
    new_data_list = []  # 用于绘制图像
    for data in data_list:
        if data <= drop_line:
            new_data_list.append(data)

    mode_name = [
        '活跃度',
        'commit累计数量',
        'PR累计数量',
        'Merged PR累计数量',
        '节点加权度',
        '介数中心性',
        '时间',
        '角色'
    ]
    if mode != 7:
        plt.hist(new_data_list, bins=100)
        if with_threshold==True:
            line_label = '第'+str(threshold)+'百分位数: '+"{0:.4f}".format(threshold_value)
            if mode >=1 and mode<=3:
                line_label = "阈值: "+"{0:.4f}".format(threshold_value)
            plt.axvline(threshold_value,ymin=0,ymax=0.98,linestyle='--',color='orangered',
                        label=line_label)
            plt.legend(loc="upper right")
        plt.title(str(repo_id) + ' 所有开发者' + mode_name[mode] + '分布直方图')
        if fig_name != '':
            plt.savefig(fig_name)
        plt.show()
    else:
        role_list = [
            'NONE',
            'CONTRIBUTOR',
            'COLLABORATOR',
            'MEMBER',
            'OWNER'
        ]
        num_dict = dict()
        for role in role_list:
            num_dict[role] = 0
        for key in data_list:
            num_dict[role_list[int(key)]] += 1
        x = []
        y = []
        for key in num_dict.keys():
            x.append(key)
            y.append(num_dict[key])
        plt.bar(x, y)
        plt.title(str(repo_id) + ' 所有开发者' + mode_name[mode] + '分布图')
        if fig_name != '':
            plt.savefig(fig_name)
        plt.show()

    return data_list,threshold_value


# 获取每个仓库开发者的不同数据的分布图，并计算阈值
# user_dir: 存储每周用户id数据的文件夹
# user_data_dir: 存储每周用户各类数据的文件夹
# histogram_dir: 存储各类数据分布图的文件夹
# threshold_dir: 存储阈值数据文件的文件夹
# step: 与其他各类用户数据一致，默认28
def saveUserDataDistributionForRepos(user_dir,user_data_dir,histogram_dir,threshold_dir,step=28):
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select id,repo_id from churn_search_repos_final')
    results = cursor.fetchall()
    filenames = os.listdir(user_dir)
    id_user_filename = dict()
    for filename in filenames:
        id_user_filename[int(filename.split('_')[0])] = filename
    filenames = os.listdir(user_data_dir)
    id_user_data_filename = dict()
    for filename in filenames:
        id_user_data_filename[int(filename.split('_')[0])] = filename

    threshold_filename = threshold_dir + '/' + 'repo_user_threshold.csv'
    with open(threshold_filename,'w',encoding='utf-8')as f:
        f.write('id,repo_id,activity avg,commit sum,pull sum,merged pull sum,degree avg,betweeness avg,time,role,\n')
    f.close()
    sub_dir_names = os.listdir(histogram_dir)

    mode_threshold = dict()

    for result in results:
        id = result[0]
        repo_id = result[1]
        user_filename = user_dir + '/' + id_user_filename[id]
        user_data_filename = user_data_dir + '/' + id_user_data_filename[id]
        for sub_dir in sub_dir_names:
            save_filename = histogram_dir + '/' + sub_dir + '/' + id_user_data_filename[id].replace('.csv','.png')
            mode = int(sub_dir.split('_')[0])
            threshold_value = getUserDataDistribution(repo_id, user_filename, user_data_filename, mode, step,
                                                         fig_name=save_filename)[1]
            mode_threshold[mode] = threshold_value
            print('id:', id, '\tmode:', mode, '\tdir name:', sub_dir, '\tthreshold:',threshold_value)
        with open(threshold_filename,'a',encoding='utf-8')as f:
            content = str(id)+','+str(repo_id)+','
            for mode in range(len(mode_threshold.keys())):
                content += str(mode_threshold[mode])+','
            content += ',\n'
            f.write(content)
        f.close()


# 获取流失开发者中重要开发者的分布
# 计算方式：score = (activity>=threshold) + (count_merged_pr>=1) + (degree>=threshold) + (time >=threshold) + (role!=NONE)
# score大于1的为终于开发者
# user_filename: 仓库对应的用户id数据文件名
# user_data_filename: 仓库对应的用户活跃度等数据文件名
# fig_name: 不同score人数图像文件名，若为空字符串则不存储
# threshold_list:依次为活跃度、merged PR、degree、time、role的阈值
def getImpUserDistribution(repo_id, user_filename, user_data_filename, fig_name='',
                              threshold_list=None, step=28):
    if threshold_list is None:
        threshold_list = [0, 0, 0, 0, 0]
    user_time = dict()
    user_activity_sum = dict()
    user_pull_merged_sum = dict()
    user_degree_sum = dict()
    user_role = dict()
    user_latest_max_score = dict() # 统计每个流失开发人员/留存人员最大的分数（可能有多次流失）
    user_latest_score_list = []  # 统计每个流失人员流失时/留存人员最后的分数
    churn_id_lists = []
    retain_id_lists = []
    type_count = 8
    with open(user_filename, 'r', encoding='utf-8')as f:
        f.readline()
        for line in f.readlines():
            if line.split(',')[5].strip(' ') != '':
                churn_id_lists.append(line.split(',')[5].strip(' ').split(' '))
            else:
                churn_id_lists.append([])
            if line.split(',')[3].strip(' ') != '':
                retain_id_lists.append(line.split(',')[3].strip(' ').split(' '))
            else:
                retain_id_lists.append([])
    retain_user_list = retain_id_lists[-1]  # 最后的留存人员列表
    # print(retain_user_list)

    with open(user_data_filename, 'r', encoding='utf-8')as f:
        f.readline()
        i = 0
        for line in f.readlines():
            churn_user_list = churn_id_lists[int(i / type_count)]
            if i % type_count == 0:  # 时间
                tmp_list = line.split(',')[1].strip(' ').split(' ')
                for item in tmp_list:
                    user_time[item.split(':')[0]] = int(item.split(':')[1])
            elif i % type_count == 1:  # 角色
                tmp_list = line.split(',')[1].strip(' ').split(' ')
                for item in tmp_list:
                    user_id_str = item.split(':')[0]
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
                    user_role[user_id_str] = value
            elif i % type_count == 2:  # 活跃度
                tmp_list = line.split(',')[1].strip(' ').split(' ')
                for item in tmp_list:
                    user_id_str = item.split(':')[0]
                    value = float(item.split(':')[1])
                    if user_id_str in user_activity_sum.keys():
                        user_activity_sum[user_id_str] += value
                    else:
                        user_activity_sum[user_id_str] = value
            elif i % type_count == 5:  # pull merged
                tmp_list = line.split(',')[1].strip(' ').split(' ')
                for item in tmp_list:
                    user_id_str = item.split(':')[0]
                    value = float(item.split(':')[1])
                    if user_id_str in user_pull_merged_sum.keys():
                        user_pull_merged_sum[user_id_str] += value
                    else:
                        user_pull_merged_sum[user_id_str] = value
            elif i % type_count == 6:  # weighted degree
                tmp_list = line.split(',')[1].strip(' ').split(' ')
                for item in tmp_list:
                    user_id_str = item.split(':')[0]
                    value = int(item.split(':')[1])
                    if user_id_str in user_degree_sum.keys():
                        user_degree_sum[user_id_str] += value
                    else:
                        user_degree_sum[user_id_str] = value
            elif i % type_count == 7:
                for user_id in churn_user_list:
                    user_time_step = float(user_time[user_id] * 7) / step
                    activity_avg = float(user_activity_sum[user_id])/user_time_step
                    degree_avg = float(user_degree_sum[user_id])/user_time_step
                    values = []
                    values.append(activity_avg)
                    values.append(user_pull_merged_sum[user_id])
                    values.append(degree_avg)
                    values.append(user_time[user_id])
                    values.append(user_role[user_id])
                    # 流失后以下用户累计数据清零
                    user_activity_sum[user_id] = 0.0
                    user_pull_merged_sum[user_id] = 0
                    user_degree_sum[user_id] = 0
                    score = 0
                    for j in range(len(values)):
                        if values[j] >= threshold_list[j]:
                            score += 1
                    user_latest_score_list.append(score)
                    if user_id in user_latest_max_score.keys():
                        if score > user_latest_max_score[user_id]:
                            user_latest_max_score[user_id] = score
                    else:
                        user_latest_max_score[user_id] = score
                if int(i/type_count)==len(churn_id_lists)-1:
                    for user_id in retain_user_list:
                        user_time_step = float(user_time[user_id] * 7) / step
                        activity_avg = float(user_activity_sum[user_id]) / user_time_step
                        degree_avg = float(user_degree_sum[user_id]) / user_time_step
                        values = []
                        values.append(activity_avg)
                        values.append(user_pull_merged_sum[user_id])
                        values.append(degree_avg)
                        values.append(user_time[user_id])
                        values.append(user_role[user_id])
                        score = 0
                        for j in range(len(values)):
                            if values[j] >= threshold_list[j]:
                                score += 1
                        user_latest_score_list.append(score)
                        if user_id in user_latest_max_score.keys():
                            if score > user_latest_max_score[user_id]:
                                user_latest_max_score[user_id] = score
                        else:
                            user_latest_max_score[user_id] = score
            i += 1
    data_list = user_latest_score_list.copy()
    x_list = [0, 1, 2, 3, 4, 5]
    score_count = dict()
    for i in x_list:
        score_count[i] = 0
    for score in data_list:
        score_count[score] += 1
    y_list = []
    for i in x_list:
        y_list.append(score_count[i])
    plt.bar(x_list,y_list)
    plt.title(str(repo_id) + ' 流失开发者综合评分分布图')
    if fig_name != '':
        plt.savefig(fig_name)
    plt.show()
    imp_rate = 1.0 - float(score_count[0])/len(data_list)

    return user_latest_max_score,score_count,imp_rate


# repo_id, user_filename, user_data_filename, fig_name='',
#                               threshold_list=None, step=28
# 为每个仓库获取并存储不同score的开发者分布图和数据
# user_dir: 存储每周用户id数据的文件夹
# user_data_dir: 存储每周用户各类数据的文件夹
# score_fig_dir: 存储不同score人数分布图的文件夹
# score_dir: 用于存储各个仓库不同score流失人数的文件夹
# threshold_filename: 各个仓库不同数据阈值文件
# step: 与其他各类用户数据一致，默认28
def saveImpUserDistributionForRepos(user_dir,user_data_dir,score_fig_dir,score_dir,threshold_filename,step=28):
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select id,repo_id from churn_search_repos_final')
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

    score_count_filename = score_dir + '/repo_user_score_count.csv'
    with open(score_count_filename,'w',encoding='utf-8')as f:
        f.write('id,repo_id,0,1,2,3,4,5,imp_rate(%),\n')
    f.close()

    for result in results:
        id = result[0]
        repo_id = result[1]
        user_filename = user_dir + '/' + id_user_filename[id]
        user_data_filename = user_data_dir + '/' + id_user_data_filename[id]
        threshold_list = id_threshold_lists[id]
        fig_name = score_fig_dir + '/'+ id_user_data_filename[id].replace('.csv','.png')
        churner_max_score, score_count, imp_rate = getImpUserDistribution(repo_id, user_filename, user_data_filename,
                                                                             fig_name, threshold_list, 28)
        with open(score_count_filename,'a',encoding='utf-8')as f:
            content = str(id)+','+str(repo_id)+','
            for score in range(6):
                content += str(score_count[score]) + ','
            content += "{0:.3f}".format(100.0*imp_rate)+',\n'
            f.write(content)
        f.close()


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

    dir_name = r'E:\bysj_project\repo_user_data_by_period\data_28'
    # 获取并存储每个仓库用户每step数据
    # saveUserDataByPeriod(dir_name,churn_limit_lists,28)

    tmp_id_list = [27]
    user_dir = 'E:/bysj_project/repo_users_by_period/data_28'
    user_data_dir = 'E:/bysj_project/repo_user_data_by_period/data_28'
    filenames = os.listdir(user_data_dir)
    user_data_filenames = dict()
    for filename in filenames:
        user_data_filenames[int(filename.split('_')[0])]=filename

    mode = 0
    threshold_lists =[
        # [1.714, 1, 1.2, 15, 1],   # 10
        # [3.819, 2, 2.85, 27, 2],  # 11
        [3.077, 1, 4.5, 19, 1]    # 27
    ]

    threshold_lists_user = [
        # [1.714, 1, 1.2, 15, 1],  # 10
        # [4.625, 2, 3.22, 29, 2],  # 11
        [3.077, 1, 4.67, 19, 1]    # 27
    ]

    histogram_dir = 'E:/bysj_project/repo_churner_classification/repo_user_histograms'
    threshold_dir = 'E:/bysj_project/repo_churner_classification'
    # saveUserDataDistributionForRepos(user_dir,user_data_dir,histogram_dir,threshold_dir,28)

    score_fig_dir = 'E:/bysj_project/repo_churner_classification/repo_user_score/repo_user_score_histogram'
    score_dir = 'E:/bysj_project/repo_churner_classification/repo_user_score'
    threshold_filename = threshold_dir + '/' + 'repo_user_threshold.csv'
    saveImpUserDistributionForRepos(user_dir,user_data_dir,score_fig_dir,score_dir,threshold_filename,28)


    # for i in range(len(tmp_id_list)):
    #     id = tmp_id_list[i]
    #     user_filename = user_dir+'/'+user_data_filenames[id]
    #     user_data_filename = user_data_dir + '/' + user_data_filenames[id]
    #     dbObject = dbHandle()
    #     cursor = dbObject.cursor()
    #     cursor.execute('select repo_id from churn_search_repos_final where id = '+str(id))
    #     result = cursor.fetchone()
    #     repo_id = result[0]
    #
    #     # data_list,threshold_value = cca.getChurnerDataDistribution(repo_id,user_filename,user_data_filename,mode=mode)
    #     # print(len(data_list),threshold_value)
    #     # data_list, threshold_value = getUserDataDistribution(repo_id, user_filename, user_data_filename, mode=mode)
    #     # print(len(data_list),threshold_value)
    #
    #     threshold_list = threshold_lists[i]
    #     ret = cca.getImpChurnerDistribution(repo_id, user_filename, user_data_filename, '', threshold_list, 28)
    #     print(ret)
    #     threshold_list = threshold_lists_user[i]
    #     ret=getImpUserDistribution(repo_id,user_filename,user_data_filename,'',threshold_list,28)
    #     print(ret)


