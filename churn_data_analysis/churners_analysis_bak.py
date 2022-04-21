# 该文件代码用户分析仓库流失人员的组成比例，分类时根据活跃度、参与时间、合作程度、角色等角度考虑
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

matplotlib.rcParams['font.sans-serif'] = ['KaiTi']
matplotlib.rcParams['axes.unicode_minus'] = False
fmt_MySQL = '%Y-%m-%d'


# 获取开发者在某一仓库某一时间段内的commit、pr、merged_pr数量
def getUserPrCommitCount(user_id,repo_id,startDay,endDay):
    table_list = [
        'repo_commit',
        'repo_pull',
        'repo_pull_merged'
    ]
    time_list = [
        'commit_time',
        'create_time',
        'merge_time'
    ]
    count_list = [0,0,0]
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    for i in range(len(count_list)):
        cursor.execute(
            'select count(*) from ' + table_list[i] + ' where user_id = ' + str(user_id) + ' and repo_id = ' + str(
                repo_id)
            + ' and ' + time_list[i] + ' between \"' + str(startDay) \
            + '\" and \"' + str(endDay) + '\"')
        result = cursor.fetchone()
        count_list[i] = result[0]
    return count_list[0],count_list[1],count_list[2]


# 保存仓库每个时间段的累计贡献时间、当前角色、节点加权度、介数中心性、活跃度数据
# dir_name: 保存文件的路径名
# churn_limit_lists: 不同社区的流失期限数据列表，每个列表每行格式为：起始时间,流失期限
# step:统计步长，为7的倍数（若不是7的倍数则选择最近值）
def saveUserDataByPeriod(dir_name,churn_limit_lists,step=28):
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select id,repo_id,repo_name,created_at from churn_search_repos_final where id = 1')
    results = cursor.fetchall()

    if step < 7:
        step = 7
    elif step % 7 != 0:
        if step - int(step / 7) * 7 < int(step / 7) * 7 + 7 - step:
            step = int(step / 7) * 7
        else:
            step = int(step / 7) * 7 + 7

    for result in results:
        id = result[0]
        repo_id = result[1]
        repo_name = result[2]
        create_time = result[3][0:10]
        end_time = '2022-01-01'
        filename = dir_name+'/'+str(id)+'_'+repo_name.replace('/','-').replace(' ','_')+'-'+str(step)+'.csv'
        user_inactive_weeks = dict()    # 每周统计一次
        user_retain_weeks = dict()  # 从用户加入/回访社区开始到当前的周数,每周统计一次
        user_role=dict()    # 用户角色,每周统计一次
        user_weighted_degree = dict()   # 用户在合作网络中的节点加权度，即合作次数，每step统计一次
        user_betweeness = dict()   # 用户在合作网络中的介数中心性，每step统计一次
        user_acitivity = dict()  # 用户的活跃度，每step统计一次
        user_commit = dict()    # 用户commit数量，每step统计一次
        user_pull = dict()  # 用户PR数量，每step统计一次
        user_pull_merged = dict()   #用户merged PR数量，每step统计一次
        all_churn_user_list = []    # 累计流失用户
        churn_user_list = []  # 每个统计间隔内流失用户列表
        retain_user_list = []   # 留存用户列表

        timedelta = datetime.datetime.strptime(end_time, fmt_MySQL) - datetime.datetime.strptime(create_time, fmt_MySQL)
        period_weeks = int(timedelta.days / 7)  # 时间段总周数

        start_day = create_time
        end_day = (datetime.datetime.strptime(start_day, fmt_MySQL) + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
        print(str(id) + ' --', start_day, '-', end_day)

        churn_limit_list = churn_limit_lists[id - 1]

        with open(filename,'w',encoding='utf-8')as f:
            f.write('time and data,content,\n')

        for i in range(period_weeks):
            week_user_list,week_user_dict = getRepoUserRoleDict(repo_id, startDay=start_day, endDay=end_day)
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
                    if user_id in all_churn_user_list:  # 流失用户回归
                        all_churn_user_list.remove(user_id)
                elif user_id not in week_user_list:  # 本周没有活动
                    user_inactive_weeks[user_id] += 1
                    if user_inactive_weeks[user_id] >= churn_limit and user_id not in all_churn_user_list:# !!!之前的流失率计算代码有误
                        if user_inactive_weeks[user_id] > churn_limit:#########################################
                            print(repo_id,i,user_id,churn_limit,user_inactive_weeks[user_id])
                        churn_user_list.append(user_id)
                        all_churn_user_list.append(user_id)
                        if user_id in retain_user_list:
                            retain_user_list.remove(user_id)
            for user_id in week_user_list:
                if user_id not in retain_user_list:  # 回访用户/新用户
                    retain_user_list.append(user_id)
                    user_retain_weeks[user_id] = 0  # 后续统一加1
                if user_id not in user_inactive_weeks.keys():
                    user_inactive_weeks[user_id] = 0
            for user_id in week_user_dict.keys():   # 更新所有用户的角色
                user_role[user_id]=week_user_dict[user_id]
            for user_id in retain_user_list:
                user_retain_weeks[user_id] += 1  # 所有留存用户的贡献周数加一

            if (i + 1) * 7 % step == 0:
                endDay = end_day
                startDay = (datetime.datetime.strptime(endDay, fmt_MySQL) - datetime.timedelta(days=step)).strftime(
                    fmt_MySQL)
                for user_id in retain_user_list:
                    user_acitivity[user_id]=getUserActivity(user_id,repo_id,startDay,endDay,False)
                    commit_count,pull_count,merged_pull_count = getUserPrCommitCount(user_id,repo_id,startDay,endDay)
                    user_commit[user_id]=commit_count
                    user_pull[user_id]=pull_count
                    user_pull_merged[user_id]=merged_pull_count
                    user_weighted_degree[user_id] = 0   # 可能有的留存开发者不在当前协作网络内，所以先置零
                    user_betweeness[user_id] = 0.0    # 先置零
                for user_id in churn_user_list:#########################
                    user_acitivity[user_id] = getUserActivity(user_id, repo_id, startDay, endDay, False)
                    commit_count, pull_count, merged_pull_count = getUserPrCommitCount(user_id, repo_id, startDay,
                                                                                       endDay)
                    user_commit[user_id] = commit_count
                    user_pull[user_id] = pull_count
                    user_pull_merged[user_id] = merged_pull_count
                    user_weighted_degree[user_id] = 0  # 可能有的当前时间窗口内流失开发者不在当前协作网络内，所以先置零
                    user_betweeness[user_id] = 0.0  # 先置零
                DCN, DCN0, index_user, user_index = getDeveloperCollaborationNetwork(repo_id,startDay,endDay)
                degree = getDCNWeightedDegrees(user_index,DCN)
                for user_id in degree.keys():
                    user_weighted_degree[user_id]=degree[user_id]
                betweeness = getBetweeness(DCN,user_index,index_user)
                for user_id in betweeness.keys():
                    user_betweeness[user_id] = betweeness[user_id]
                with open(filename, 'a', encoding='utf-8')as f:
                    line_content = str((i+1)*7)+' time,'
                    for user_id in retain_user_list:
                        line_content+=str(user_id)+':'+str(user_retain_weeks[user_id])+' '
                    for user_id in churn_user_list:  #########################
                        line_content += str(user_id) + ':' + str(user_retain_weeks[user_id]) + ' '
                    f.write(line_content+',\n')

                    line_content = str((i+1)*7) + ' role,'
                    for user_id in retain_user_list:
                        line_content += str(user_id) + ':' + str(user_role[user_id]) + ' '
                    for user_id in churn_user_list:  #########################
                        line_content += str(user_id) + ':' + str(user_role[user_id]) + ' '
                    f.write(line_content + ',\n')

                    line_content = str((i+1)*7) + ' activity,'
                    for user_id in retain_user_list:
                        line_content += str(user_id) + ':' + "{0:.4f}".format(user_acitivity[user_id]) + ' '
                    for user_id in churn_user_list:  #########################
                        line_content += str(user_id) + ':' + "{0:.4f}".format(user_acitivity[user_id]) + ' '
                    f.write(line_content + ',\n')

                    line_content = str((i + 1) * 7) + ' commit,'
                    for user_id in retain_user_list:
                        line_content += str(user_id) + ':' + "{0:.4f}".format(user_commit[user_id]) + ' '
                    for user_id in churn_user_list:  #########################
                        line_content += str(user_id) + ':' + "{0:.4f}".format(user_commit[user_id]) + ' '
                    f.write(line_content + ',\n')

                    line_content = str((i + 1) * 7) + ' pull,'
                    for user_id in retain_user_list:
                        line_content += str(user_id) + ':' + "{0:.4f}".format(user_pull[user_id]) + ' '
                    for user_id in churn_user_list:  #########################
                        line_content += str(user_id) + ':' + "{0:.4f}".format(user_pull[user_id]) + ' '
                    f.write(line_content + ',\n')

                    line_content = str((i + 1) * 7) + ' merged_pull,'
                    for user_id in retain_user_list:
                        line_content += str(user_id) + ':' + "{0:.4f}".format(user_pull_merged[user_id]) + ' '
                    for user_id in churn_user_list:  #########################
                        line_content += str(user_id) + ':' + "{0:.4f}".format(user_pull_merged[user_id]) + ' '
                    f.write(line_content + ',\n')

                    line_content = str((i+1)*7) + ' degree,'
                    for user_id in retain_user_list:
                        line_content += str(user_id) + ':' + str(user_weighted_degree[user_id]) + ' '
                    for user_id in churn_user_list:  #########################
                        line_content += str(user_id) + ':' + str(user_weighted_degree[user_id]) + ' '
                    f.write(line_content + ',\n')

                    line_content = str((i+1)*7) + ' betweeness,'
                    for user_id in retain_user_list:
                        line_content += str(user_id) + ':' + "{0:.4f}".format(user_betweeness[user_id]) + ' '
                    for user_id in churn_user_list:  #########################
                        line_content += str(user_id) + ':' + "{0:.4f}".format(user_betweeness[user_id]) + ' '
                    f.write(line_content + ',\n')
                churn_user_list = []    #########################

            start_day = end_day
            end_day = (datetime.datetime.strptime(start_day, fmt_MySQL) + datetime.timedelta(days=7)).strftime(
                '%Y-%m-%d')
            if end_day > end_time:
                end_day = end_time
            print(start_day, end_day)


# 获取仓库全部历史时间的某一类流失人员数据的分布情况
# mode: 0--平均活跃度、1--累计commit数量、2--累计pull数量、3--累计merged_pr数量、
#       4--平均节点加权度、5--平均介数中心性、6--留存时间、7--承担的角色
# user_filename: 仓库对应的用户id数据文件名
# user_data_filename: 仓库对应的用户活跃度等数据文件名
# churn_limit_list: 仓库对应的流失期限
def getChurnerDataDistribution(repo_id,user_filename,user_data_filename,churn_limit_list,mode=0,step=28):
    user_time = dict()  # 用户留存时间
    # churner_active_time =dict()   ################ 流失人员有活动的时间，一般情况下等于留存时间-流失期限+1，对于在流失期限切换时间附近，该时间可能会变大。
    user_activity_sum = dict()
    user_commit_sum = dict()
    user_pull_sum = dict()
    user_pull_merged_sum = dict()
    user_degree_sum=dict()
    user_betweeness_sum =dict()
    user_role = dict()
    churner_time = []
    churner_role = []
    churner_acitivity_avg = []
    churner_commit_sum = []
    churner_pull_sum = []
    churner_pull_merged_sum = []
    churner_degree_avg = []
    churner_betweeness_avg = []
    churn_id_lists = []
    type_count = 8
    with open(user_filename,'r',encoding='utf-8')as f:
        f.readline()
        for line in f.readlines():
            if line.split(',')[5].strip(' ')!='':
                churn_id_lists.append(line.split(',')[5].strip(' ').split(' '))
            else:
                churn_id_lists.append([])
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select created_at from churn_search_repos_final where repo_id = '+str(repo_id))
    result = cursor.fetchone()
    create_time = result[0][0:10]

    with open(user_data_filename,'r',encoding='utf-8')as f:
        f.readline()
        i = 0
        for line in f.readlines():
            '''step_index = int(i/type_count)  # 当前step对应的序号，从0开始
            step_start_time = datetime.datetime.strptime(create_time,fmt_MySQL)+datetime.timedelta(days=step*step_index)
            step_end_time = step_start_time+datetime.timedelta(days=step)

            # 找到当前step对应的流失期限，如果流失期限分段点在当前step内，则取两个流失期限里较小的一个
            churn_limit = 53
            for j in range(len(churn_limit_list) - 1, -1, -1):
                period_start_time = datetime.datetime.strptime(churn_limit_list[j][0],fmt_MySQL)
                if j == len(churn_limit_list) - 1:
                    period_end_time = datetime.datetime.strptime('2022-01-01',fmt_MySQL)
                else:
                    period_end_time = datetime.datetime.strptime(churn_limit_list[j+1][0],fmt_MySQL)
                if period_start_time <= step_start_time:
                    if period_end_time >= step_end_time:
                        churn_limit = int(churn_limit_list[j][1])
                    else:
                        if int(churn_limit_list[j][1]) <= int(churn_limit_list[j+1][1]):
                            churn_limit = int(churn_limit_list[j][1])
                        else:
                            churn_limit = int(churn_limit_list[j+1][1])
                    break
            print('step_start_time:',step_start_time,'churn limit:',churn_limit)'''#########################

            churn_user_list = churn_id_lists[int(i/type_count)]
            if i % type_count == 0:  # 时间
                tmp_list = line.split(',')[1].strip(' ').split(' ')
                for item in tmp_list:
                    user_time[item.split(':')[0]]=int(item.split(':')[1])
                for user_id in churn_user_list:
                    churner_time.append(user_time[user_id])
                    # churner_active_time[user_id]=user_time[user_id] - churn_limit + 1##################
                    # print(user_id,churner_active_time[user_id])################
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
                    user_role[user_id_str] = value
                for user_id in churn_user_list:
                    churner_role.append(user_role[user_id])
            elif mode == 0 and i % type_count == 2:   # 活跃度
                tmp_list = line.split(',')[1].strip(' ').split(' ')
                for item in tmp_list:
                    user_id_str = item.split(':')[0]
                    value = float(item.split(':')[1])
                    if user_id_str in user_activity_sum.keys():
                        user_activity_sum[user_id_str]+=value
                    else:
                        user_activity_sum[user_id_str] = value
                for user_id in churn_user_list:
                    user_time_step = float(user_time[user_id]*7)/ step
                    # churner_time_step = float(churner_active_time[user_id]*7)/step
                    churner_acitivity_avg.append(float(user_activity_sum[user_id])/user_time_step)
                    # churner_acitivity_avg.append(float(user_activity_sum[user_id]) / churner_time_step)#########
                    user_activity_sum[user_id] = 0.0 # 流失后活跃度数据清零
            elif mode == 1 and i % type_count == 3:  # commit
                tmp_list = line.split(',')[1].strip(' ').split(' ')
                for item in tmp_list:
                    user_id_str = item.split(':')[0]
                    value = float(item.split(':')[1])
                    if user_id_str in user_commit_sum.keys():
                        user_commit_sum[user_id_str] += value
                    else:
                        user_commit_sum[user_id_str] = value
                for user_id in churn_user_list:
                    churner_commit_sum.append(
                        float(user_commit_sum[user_id]))
                    user_commit_sum[user_id] = 0
            elif mode == 2 and i % type_count == 4:  # pull
                tmp_list = line.split(',')[1].strip(' ').split(' ')
                for item in tmp_list:
                    user_id_str = item.split(':')[0]
                    value = float(item.split(':')[1])
                    if user_id_str in user_pull_sum.keys():
                        user_pull_sum[user_id_str] += value
                    else:
                        user_pull_sum[user_id_str] = value
                for user_id in churn_user_list:
                    churner_pull_sum.append(
                        float(user_pull_sum[user_id]))
                    user_pull_sum[user_id] = 0
            elif mode == 3 and i % type_count == 5:  # pull merged
                tmp_list = line.split(',')[1].strip(' ').split(' ')
                for item in tmp_list:
                    user_id_str = item.split(':')[0]
                    value = float(item.split(':')[1])
                    if user_id_str in user_pull_merged_sum.keys():
                        user_pull_merged_sum[user_id_str] += value
                    else:
                        user_pull_merged_sum[user_id_str] = value
                for user_id in churn_user_list:
                    churner_pull_merged_sum.append(
                        float(user_pull_merged_sum[user_id]) )
                    user_pull_merged_sum[user_id] = 0
            elif mode == 4 and i % type_count == 6:  # weighted degree
                tmp_list = line.split(',')[1].strip(' ').split(' ')
                for item in tmp_list:
                    user_id_str = item.split(':')[0]
                    value = int(item.split(':')[1])
                    if user_id_str in user_degree_sum.keys():
                        user_degree_sum[user_id_str] += value
                    else:
                        user_degree_sum[user_id_str] = value
                for user_id in churn_user_list:
                    user_time_step = float(user_time[user_id] * 7) / step
                    # churner_time_step = float(churner_active_time[user_id] * 7) / step
                    churner_degree_avg.append(float(user_degree_sum[user_id]) / user_time_step)
                    # churner_degree_avg.append(float(user_degree_sum[user_id]) / churner_time_step)  ###########
                    user_degree_sum[user_id] = 0  # 流失后加权度数据清零
            elif mode == 5 and i % type_count == 7:  # betweeness
                tmp_list = line.split(',')[1].strip(' ').split(' ')
                for item in tmp_list:
                    user_id_str = item.split(':')[0]
                    value = float(item.split(':')[1])
                    if user_id_str in user_betweeness_sum.keys():
                        user_betweeness_sum[user_id_str] += value
                    else:
                        user_betweeness_sum[user_id_str] = value
                for user_id in churn_user_list:
                    user_time_step = float(user_time[user_id] * 7) / step
                    # churner_time_step = float(churner_active_time[user_id] * 7) / step
                    churner_betweeness_avg.append(float(user_betweeness_sum[user_id]) / user_time_step)
                    # churner_betweeness_avg.append(float(user_betweeness_sum[user_id]) / churner_time_step)
                    user_betweeness_sum[user_id] = 0.0  # 流失后介数中心性数据清零
            i += 1

    if mode == 0:
        return churner_acitivity_avg
    elif mode == 1:
        return churner_commit_sum
    elif mode == 2:
        return churner_pull_sum
    elif mode == 3:
        return churner_pull_merged_sum
    elif mode == 4:
        return churner_degree_avg
    elif mode == 5:
        return churner_betweeness_avg
    elif mode == 6:
        return churner_time
    elif mode == 7:
        return churner_role
    return None


# 获取流失开发者中重要开发者的分布
# 计算方式：score = (activity>=threshold) + (count_merged_pr>=1) + (degree>=threshold) + (time >=threshold) + (role!=NONE)
# score大于1的为终于开发者
# user_filename: 仓库对应的用户id数据文件名
# user_data_filename: 仓库对应的用户活跃度等数据文件名
# threshold:依次为活跃度、merged PR、degree、time、role的阈值
def getImpChurnerDistribution(repo_id, user_filename, user_data_filename, threshold_list=None, step=28):
    if threshold_list is None:
        threshold_list = [0, 0, 0, 0, 0]
    user_time = dict()
    user_activity_sum = dict()
    user_pull_merged_sum = dict()
    user_degree_sum = dict()
    user_role = dict()
    churner_max_score = dict() # 统计每个流失开发人员最大的分数（可能有多次流失）
    churner_score_list = []  # 统计每个流失人员流失时的分数
    churn_id_lists = []
    type_count = 8
    with open(user_filename, 'r', encoding='utf-8')as f:
        f.readline()
        for line in f.readlines():
            if line.split(',')[5].strip(' ') != '':
                churn_id_lists.append(line.split(',')[5].strip(' ').split(' '))
            else:
                churn_id_lists.append([])
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
                    churner_score_list.append(score)
                    if user_id in churner_max_score.keys():
                        if score > churner_max_score[user_id]:
                            churner_max_score[user_id] = score
                    else:
                        churner_max_score[user_id] = score
            i += 1

    # print(len(churner_score_list),len(churner_max_score.keys()),len(churner_max_score.values()))
    return churner_score_list,churner_max_score


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
    # saveUserDataByPeriod(dir_name,churn_limit_lists,28)

    tmp_id_list = [2]
    user_dir = 'E:/bysj_project/repo_users_by_period/data_28'
    user_data_dir = 'E:/bysj_project/repo_user_data_by_period/data_28'
    filenames = os.listdir(user_data_dir)
    user_data_filenames = dict()
    for filename in filenames:
        user_data_filenames[int(filename.split('_')[0])]=filename

    mode_name =[
        '活跃度',
        'commit累计数量',
        'PR累计数量',
        'Merged PR累计数量',
        '节点加权度',
        '介数中心性',
        '时间',
        '角色'
    ]
    mode = 0

    threshold_lists =[
        [6.078, 2, 6.454, 15, 2],
        [3.333, 1, 5.292, 15, 1],
        [2.333, 1, 3.333, 15, 1],
        [3.294, 1, 5.000, 18, 1],
        [1.600, 1, 3.200, 15, 1]
    ]

    for i in range(len(tmp_id_list)):
        id = tmp_id_list[i]
        user_filename = user_dir+'/'+user_data_filenames[id]
        user_data_filename = user_data_dir + '/' + user_data_filenames[id]
        dbObject = dbHandle()
        cursor = dbObject.cursor()
        cursor.execute('select repo_id from churn_search_repos_final where id = '+str(id))
        result = cursor.fetchone()
        repo_id = result[0]

        data_list = getChurnerDataDistribution(repo_id,user_filename,user_data_filename,churn_limit_lists[id-1],mode=mode)
        if mode != 7:
            data_array = np.array(data_list)
            data_list = sorted(data_list)[0:-20]
            print(sorted(data_list))
            print('中位数:',np.median(data_array))
            print('平均值:',np.mean(data_array))
            print('Q3:',np.percentile(data_array,75))
            print('80%:',np.percentile(data_array,80))
            plt.hist(data_list,bins=100)
            plt.title(str(id)+'. '+str(repo_id)+' '+mode_name[mode]+'分布直方图')
            plt.show()

            lists = []
            lists.append(data_list)
            ylabels = [mode_name[mode]]
            # drawBoxplot(lists, ylabels, str(repo_id) + mode_name[mode] + '箱线图')
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
                num_dict[role]=0
            for key in data_list:
                num_dict[role_list[int(key)]]+=1
            x = []
            y = []
            for key in num_dict.keys():
                x.append(key)
                y.append(num_dict[key])
            plt.bar(x,y)
            plt.title(str(id) + '. ' + str(repo_id) + ' ' + mode_name[mode] + '分布图')
            plt.show()
        '''threshold_list = threshold_lists[i]
        churner_score_list,churner_max_score = getImpChurnerDistribution(repo_id,user_filename,user_data_filename,threshold_list,28)
        data_list = churner_score_list.copy()
        plt.hist(data_list, bins=15)
        plt.title(str(id) + '. ' + str(repo_id) + ' 流失开发者综合评分分布直方图')
        plt.show()
        imp_count = 0
        for score in data_list:
            if score > 0:
                imp_count += 1
        print('流失人员中重要开发者比例:'+str(imp_count)+'/'+str(len(data_list))+
              '('+"{0:.3f}".format(100*float(imp_count)/len(data_list))+ '%)')'''
