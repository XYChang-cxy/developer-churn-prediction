import matplotlib
import matplotlib.pyplot as plt
from churn_data_analysis import settings
import pymysql
import datetime
import numpy as np
from churn_data_analysis import draw_return_visit_curve
from churn_data_analysis.draw_return_visit_curve import dbHandle
import os

matplotlib.rcParams['font.sans-serif'] = ['KaiTi']
matplotlib.rcParams['axes.unicode_minus'] = False

fmt_day = '%Y-%m-%d'
fmt_mysql = '%Y-%m-%d %H:%M:%S'


# 往数据库表格repo_pure_issue_response中插入数据
def insertIssueResponseData():
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select min(create_time),max(create_time) from repo_issue')
    results = cursor.fetchall()
    startTime = (results[0][0]-datetime.timedelta(days=30)).strftime(fmt_day)
    endTime = (results[0][1]+datetime.timedelta(days=30)).strftime(fmt_day)
    # print(startTime,endTime)
    time_step = 100

    cursor.execute('select id,repo_id from churn_search_repos_final where id = 29')
    id_repo_id = dict()
    results = cursor.fetchall()
    for result in results:
        id_repo_id[result[0]]=result[1]

    for id in id_repo_id.keys():
        if id == 23 or id == 26 or id == 29:
            time_step = 30
        else:
            time_step = 100
        repo_id = id_repo_id[id]
        start_time = startTime
        end_time = (datetime.datetime.strptime(start_time, fmt_day) + datetime.timedelta(days=time_step)).strftime(
            fmt_day)
        print('id:', id, 'repo_id:', id_repo_id[id])
        while (start_time < endTime):
            print('\tid:', id,start_time, '--', end_time)
            order = 'select platform,issue_number,create_time,close_time,issue_state,user_id from repo_issue r1 ' \
                    'where r1.repo_id = ' + str(repo_id) + ' and ' \
                    'r1.create_time between \"' + start_time + '\" and \"' + end_time + '\" and not exists ' \
                    '(select id from repo_pull r2 where r2.repo_id = r1.repo_id and r1.issue_number = r2.pull_number)'
            # print(order)
            cursor.execute(order)
            results = cursor.fetchall()
            for result in results:
                platform = result[0]
                issue_number = result[1]
                create_time = result[2].strftime(fmt_mysql)
                close_time = result[3].strftime(fmt_mysql)
                issue_state = result[4]
                user_id = result[5]
                order = 'select create_time,is_core_issue_comment from repo_issue_comment where repo_id = ' + str(
                    repo_id) + ' and ' \
                    'issue_number = ' + str(issue_number)
                cursor.execute(order)
                tmp_ret = cursor.fetchall()
                comment_count = len(tmp_ret)
                core_comment_count = 0
                first_comment_time = '2022-12-31 00:00:00'
                first_core_comment_time = '2022-12-31 00:00:00'
                for ret in tmp_ret:
                    if ret[0].strftime(fmt_mysql) < first_comment_time:
                        first_comment_time = ret[0].strftime(fmt_mysql)
                    if int(ret[1]) == 1:
                        core_comment_count += 1
                        if ret[0].strftime(fmt_mysql) < first_core_comment_time:
                            first_core_comment_time = ret[0].strftime(fmt_mysql)
                if core_comment_count == 0:
                    first_core_comment_time = '1000-01-01 00:00:00'
                if comment_count == 0:
                    first_comment_time = '1000-01-01 00:00:00'

                cursor.execute('select id from repo_pure_issue_response where repo_id = ' + str(repo_id) + ' and '
                               'issue_number = ' + str(issue_number))
                tmp_ret = cursor.fetchone()
                if tmp_ret:
                    print('\t\tupdate:', issue_number)
                    order = 'update repo_pure_issue_response set platform = %s, create_time = %s, close_time = %s, ' \
                            'issue_state = %s, user_id = %s, first_comment_time = %s, first_core_comment_time = %s, ' \
                            'comment_count = %s, core_comment_count = %s where repo_id = %s and issue_number = %s'
                    try:
                        cursor.execute(order, (
                            platform, create_time, close_time, issue_state, user_id, first_comment_time,
                            first_core_comment_time, comment_count, core_comment_count, repo_id, issue_number))
                        cursor.connection.commit()
                    except BaseException as e:
                        print(e)
                        dbObject.rollback()
                else:
                    print('\t\tinsert:', issue_number)
                    order = 'insert into repo_pure_issue_response(repo_id, platform, issue_number, create_time, ' \
                            'close_time, issue_state, user_id, first_comment_time,first_core_comment_time, ' \
                            'comment_count, core_comment_count) ' \
                            'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                    try:
                        cursor.execute(order, (
                            repo_id, platform, issue_number, create_time, close_time, issue_state, user_id,
                            first_comment_time, first_core_comment_time, comment_count, core_comment_count))
                        cursor.connection.commit()
                    except BaseException as e:
                        print(e)
                        dbObject.rollback()
            start_time = end_time
            end_time = (datetime.datetime.strptime(start_time, fmt_day) + datetime.timedelta(days=time_step)).strftime(
                fmt_day)
            if end_time > endTime:
                end_time = endTime


# 往数据库表格repo_pull_response中插入数据
def insertPullResponseData():
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select min(create_time),max(create_time) from repo_pull')
    results = cursor.fetchall()
    startTime = (results[0][0]-datetime.timedelta(days=30)).strftime(fmt_day)
    endTime = (results[0][1]+datetime.timedelta(days=30)).strftime(fmt_day)
    # print(startTime,endTime)
    time_step = 100

    cursor.execute('select id,repo_id from churn_search_repos_final where id=29')
    id_repo_id = dict()
    results = cursor.fetchall()
    for result in results:
        id_repo_id[result[0]] = result[1]

    for id in id_repo_id.keys():
        if id == 23 or id == 26 or id == 29:
            time_step = 30
        else:
            time_step = 100
        repo_id = id_repo_id[id]
        start_time = startTime
        end_time = (datetime.datetime.strptime(start_time, fmt_day) + datetime.timedelta(days=time_step)).strftime(
            fmt_day)
        print('id:', id, 'repo_id:', id_repo_id[id])

        while (start_time < endTime):
            print('\tid:', id,start_time, '--', end_time)
            order = 'select platform,pull_number,create_time,close_time,merge_time,pull_state,user_id,pull_id ' \
                    'from repo_pull where repo_id = ' + str(repo_id) + ' and ' \
                    'create_time between \"' + start_time + '\" and \"' + end_time + '\"'
            # print(order)
            cursor.execute(order)
            results = cursor.fetchall()
            for result in results:
                platform = result[0]
                pull_number = result[1]
                create_time = result[2].strftime(fmt_mysql)
                close_time = result[3].strftime(fmt_mysql)
                merge_time = result[4].strftime(fmt_mysql)
                pull_state = result[5]
                if pull_state == 'closed' and merge_time > '1500-01-01 00:00:00':
                    pull_state = 'merged'
                user_id = result[6]
                pull_id = result[7]

                order = 'select create_time,is_core_issue_comment from repo_issue_comment where repo_id = ' + str(
                    repo_id) + ' and issue_number = ' + str(pull_number)
                cursor.execute(order)
                tmp_ret = cursor.fetchall()
                comment_count = len(tmp_ret)
                core_comment_count = 0
                first_comment_time = '2022-12-31 00:00:00'
                first_core_comment_time = '2022-12-31 00:00:00'
                for ret in tmp_ret:
                    if ret[0].strftime(fmt_mysql) < first_comment_time:
                        first_comment_time = ret[0].strftime(fmt_mysql)
                    if int(ret[1]) == 1:
                        core_comment_count += 1
                        if ret[0].strftime(fmt_mysql) < first_core_comment_time:
                            first_core_comment_time = ret[0].strftime(fmt_mysql)
                if core_comment_count == 0:
                    first_core_comment_time = '1000-01-01 00:00:00'
                if comment_count == 0:
                    first_comment_time = '1000-01-01 00:00:00'

                order = 'select submit_time,author_association from repo_review where repo_id = '+str(
                    repo_id) + ' and pull_id = ' + str(pull_id)
                cursor.execute(order)
                tmp_ret = cursor.fetchall()
                review_count = len(tmp_ret)
                core_review_count = 0
                first_review_time = '2022-12-31 00:00:00'
                first_core_review_time = '2022-12-31 00:00:00'
                for ret in tmp_ret:
                    if ret[0].strftime(fmt_mysql) < first_review_time:
                        first_review_time = ret[0].strftime(fmt_mysql)
                    if ret[1]!='NONE' and ret[1]!='CONTRIBUTOR':
                        core_review_count += 1
                        if ret[0].strftime(fmt_mysql) < first_core_review_time:
                            first_core_review_time = ret[0].strftime(fmt_mysql)
                if core_review_count == 0:
                    first_core_review_time = '1000-01-01 00:00:00'
                if review_count == 0:
                    first_review_time = '1000-01-01 00:00:00'

                order = 'select create_time,author_association from repo_review_comment where repo_id = ' + str(
                    repo_id) + ' and pull_id = ' + str(pull_id)
                cursor.execute(order)
                tmp_ret = cursor.fetchall()
                review_comment_count = len(tmp_ret)
                core_review_comment_count = 0
                first_review_comment_time = '2022-12-31 00:00:00'
                first_core_review_comment_time = '2022-12-31 00:00:00'
                for ret in tmp_ret:
                    if ret[0].strftime(fmt_mysql) < first_review_comment_time:
                        first_review_comment_time = ret[0].strftime(fmt_mysql)
                    if ret[1] != 'NONE' and ret[1] != 'CONTRIBUTOR':
                        core_review_comment_count += 1
                        if ret[0].strftime(fmt_mysql) < first_core_review_comment_time:
                            first_core_review_comment_time = ret[0].strftime(fmt_mysql)
                if core_review_comment_count == 0:
                    first_core_review_comment_time = '1000-01-01 00:00:00'
                if review_comment_count == 0:
                    first_review_comment_time = '1000-01-01 00:00:00'

                cursor.execute('select id from repo_pull_response where repo_id = ' + str(repo_id) + ' and '
                               'pull_number = ' + str(pull_number))
                tmp_ret = cursor.fetchone()
                if tmp_ret:
                    print('\t\tupdate:', pull_number)
                    order = 'update repo_pull_response set platform = %s, create_time = %s, close_time = %s, ' \
                            'merge_time = %s, pull_state = %s, user_id = %s, first_comment_time = %s, ' \
                            'first_core_comment_time = %s, first_review_time = %s, first_core_review_time = %s, ' \
                            'first_review_comment_time = %s, first_core_review_comment_time = %s, ' \
                            'comment_count = %s, core_comment_count = %s, review_count = %s, core_review_count = %s, ' \
                            'review_comment_count = %s, core_review_comment_count = %s ' \
                            'where repo_id = %s and pull_number = %s'
                    try:
                        cursor.execute(order, (
                            platform, create_time, close_time, merge_time, pull_state, user_id, first_comment_time,
                            first_core_comment_time, first_review_time, first_core_review_time,
                            first_review_comment_time, first_core_review_comment_time, comment_count,
                            core_comment_count, review_count, core_review_count, review_comment_count,
                            core_review_comment_count, repo_id, pull_number))
                        cursor.connection.commit()
                    except BaseException as e:
                        print(e)
                        dbObject.rollback()
                else:
                    print('\t\tinsert:', pull_number)
                    order = 'insert into repo_pull_response(repo_id, platform, pull_number, create_time, close_time, ' \
                            'merge_time, pull_state, user_id, first_comment_time,first_core_comment_time, ' \
                            'first_review_time, first_core_review_time, first_review_comment_time, ' \
                            'first_core_review_comment_time, comment_count, core_comment_count, review_count, ' \
                            'core_review_count, review_comment_count, core_review_comment_count) ' \
                            'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                    try:
                        cursor.execute(order, (
                            repo_id, platform, pull_number, create_time, close_time, merge_time, pull_state, user_id,
                            first_comment_time, first_core_comment_time, first_review_time, first_core_review_time,
                            first_review_comment_time, first_core_review_comment_time, comment_count,
                            core_comment_count, review_count, core_review_count, review_comment_count,
                            core_review_comment_count))
                        cursor.connection.commit()
                    except BaseException as e:
                        print(e)
                        dbObject.rollback()
            start_time = end_time
            end_time = (datetime.datetime.strptime(start_time, fmt_day) + datetime.timedelta(days=time_step)).strftime(
                fmt_day)
            if end_time > endTime:
                end_time = endTime


'''# 绘制某一仓库纯issue、PR、issue+PR的响应时间的时序曲线,根据每step内创建的issue/PR进行统计
# core: 0--所有响应；1--core响应
# repo_id: 仓库id
# startDay: 起始日期
# endDay: 结束日期
# step: 计算数量的步长，默认每7天计算一次数量并求平均
# fig_name: 保存的图片名，如果为空字符串则不保存
# data_filename: 保存的数据问件名，如果为空字符串则不保存
def drawResponseTimeCurveByIssue(repo_id,startDay,endDay,step=7,core=0,fig_name='',data_filename=''):
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    timedelta = datetime.datetime.strptime(endDay, fmt_day) - datetime.datetime.strptime(startDay, fmt_day)
    time_count = int(timedelta.days / step)
    time_list = []
    issue_response_mean = []
    issue_response_median = []
    pull_response_mean = []
    pull_response_median = []
    issue_pull_response_mean = []
    issue_pull_response_median = []

    for i in range(time_count):
        time_list.append(step * i)
        start_day = (datetime.datetime.strptime(startDay, fmt_day) + datetime.timedelta(days=i * step)).strftime(
            fmt_day)
        end_day = (datetime.datetime.strptime(start_day, fmt_day) + datetime.timedelta(days=step)).strftime(
            fmt_day)

        if core == 0:
            order = 'select create_time,comment_count,first_comment_time from repo_pure_issue_response ' \
                    'where repo_id = '+str(repo_id) + ' and create_time between \"'+start_day +' \" and ' \
                    '\"'+end_day +'\"'
        else:
            order = 'select create_time,core_comment_count,first_core_comment_time from repo_pure_issue_response ' \
                    'where repo_id = '+str(repo_id) + ' and create_time between \"'+start_day +' \" and ' \
                    '\"'+end_day +'\"'
        cursor.execute(order)
        results = cursor.fetchall()
        response_list_1 = []
        response_list_3 = []
        for result in results:
            if result[1] == 0:
                continue
            day_count = (result[2]-result[0]).days
            if day_count > 100:
                print(result[0])################
            response_list_1.append(day_count)
            response_list_3.append(day_count)
        if len(response_list_1)==0:
            print('not response for issues during:',start_day,'--',end_day)
            issue_response_mean.append(-1)
            issue_response_median.append(-1)
        else:
            response_array_1 = np.array(response_list_1)
            issue_response_mean.append(np.mean(response_array_1))
            issue_response_median.append(np.median(response_array_1))

        if core == 0:
            order = 'select create_time,comment_count,review_count,review_comment_count, ' \
                    'first_comment_time,first_review_time,first_review_comment_time from repo_pull_response ' \
                    'where repo_id = ' + str(repo_id) + ' and create_time between \"' + start_day + ' \" and ' \
                    '\"' + end_day + '\"'
        else:
            order = 'select create_time,core_comment_count,core_review_count,core_review_comment_count, ' \
                    'first_core_comment_time,first_core_review_time,first_core_review_comment_time from repo_pull_response ' \
                    'where repo_id = ' + str(repo_id) + ' and create_time between \"' + start_day + ' \" and ' \
                    '\"' + end_day + '\"'
        cursor.execute(order)
        results = cursor.fetchall()
        response_list_2 = []
        for result in results:
            day_counts = []
            for k in range(1,4):
                if result[k]!=0:
                    day_counts.append((result[k+3]-result[0]).days)
            if len(day_counts)>0:
                response_list_2.append(min(day_counts))
                response_list_3.append(min(day_counts))
        if len(response_list_2)==0:
            print('not response for pulls during:',start_day,'--',end_day)
            pull_response_mean.append(-1)
            pull_response_median.append(-1)
        else:
            response_array_2 = np.array(response_list_2)
            pull_response_mean.append(np.mean(response_array_2))
            pull_response_median.append(np.median(response_array_2))

        if len(response_list_3)==0:
            print('not response for issues and pulls during:',start_day,'--',end_day)
            issue_pull_response_mean.append(-1)
            issue_pull_response_median.append(-1)
        else:
            response_array_3 = np.array(response_list_3)
            issue_pull_response_mean.append(np.mean(response_array_3))
            issue_pull_response_median.append(np.median(response_array_3))

    if data_filename!='':
        with open(data_filename,'w',encoding='utf-8')as f:
            f.write('time,issue_mean,pull_mean,issue_pull_mean,issue_median,pull_median,issue_pull_median,\n')
            for i in range(len(time_list)):
                line = str(time_list[i])+','
                line += str(issue_response_mean[i]) + ','
                line += str(pull_response_mean[i]) + ','
                line += str(issue_pull_response_mean[i]) + ','
                line += str(issue_response_median[i]) + ','
                line += str(pull_response_median[i]) + ','
                line += str(issue_pull_response_median[i]) + ','
                f.write(line+'\n')

    colors = ['red','darkred','green','darkgreen','blue','darkblue']
    plt.figure(figsize=(10, 5))
    plt.plot(time_list, issue_response_mean, linewidth=1.5, marker='.', markerfacecolor='w',
             color=colors[0], label='issue mean')
    plt.plot(time_list, issue_response_median, linewidth=1.5, marker='.', markerfacecolor='w',
             color=colors[1], label='issue median',alpha=0.7)
    plt.plot(time_list, pull_response_mean, linewidth=1.5, marker='.', markerfacecolor='w',
             color=colors[2], label='pull mean')
    plt.plot(time_list, pull_response_median, linewidth=1.5, marker='.', markerfacecolor='w',
             color=colors[3], label='pull median',alpha=0.7)
    plt.plot(time_list, issue_pull_response_mean, linewidth=1.5, marker='.', markerfacecolor='w',
             color=colors[4], label='issue & pull mean')
    plt.plot(time_list, issue_pull_response_median, linewidth=1.5, marker='.', markerfacecolor='w',
             color=colors[5], label='issue & pull median',alpha=0.7)
    plt.legend(loc='upper left')
    if core==0:
        plt.title('社区（repo_id=' + str(repo_id) + '）' + startDay + '~' + endDay + '期间issue和PR第一次响应时间的'
                  '均值/中位数随时间变化曲线')
    else:
        plt.title('社区（repo_id=' + str(repo_id) + '）' + startDay + '~' + endDay + '期间issue和PR第一次被社区内部人员响应'
                                                                                 '时间的均值/中位数随时间变化曲线')
    if fig_name!='':
        plt.savefig(fig_name)
    plt.show()'''


# 绘制某一仓库纯issue、PR、issue+PR的响应时间的时序曲线，根据每step内的comment（review）进行统计
# core: 0--所有响应；1--core响应
# repo_id: 仓库id
# startDay: 起始日期
# endDay: 结束日期
# step: 计算数量的步长，默认每7天计算一次数量并求平均
# fig_name: 保存的图片名，如果为空字符串则不保存
# data_filename: 保存的数据问件名，如果为空字符串则不保存
# except_threshold:大于0时，大等于该阈值的response time被剔除；默认为-1，不剔除任何数据
# none_response_mode: 如果某一step内没有首次响应时如何处理：0--设为-1;1--设为上一step的值
def drawResponseTimeCurveByComment(repo_id,startDay,endDay,step=7,core=0,fig_name='',data_filename='',
                                   except_threshold=-1, none_response_mode=1):
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    timedelta = datetime.datetime.strptime(endDay, fmt_day) - datetime.datetime.strptime(startDay, fmt_day)
    time_count = int(timedelta.days / step)
    time_list = []
    issue_response_lists = [] #每step内的（第一次）响应时长（列表）的列表
    pull_response_lists = []
    issue_pull_response_lists = []
    for i in range(time_count):
        issue_response_lists.append([])
        pull_response_lists.append([])
        issue_pull_response_lists.append([])

    issue_response_mean = []
    issue_response_median = []
    pull_response_mean = []
    pull_response_median = []
    issue_pull_response_mean = []
    issue_pull_response_median = []

    except_count_issue = 0
    except_count_pull = 0
    all_count_issue = 0
    all_count_pull = 0

    for i in range(time_count):
        start_day = (datetime.datetime.strptime(startDay, fmt_day) + datetime.timedelta(days=i * step)).strftime(
            fmt_day)
        end_day = (datetime.datetime.strptime(start_day, fmt_day) + datetime.timedelta(days=step)).strftime(
            fmt_day)

        if core == 0:
            order = 'select create_time,comment_count,first_comment_time from repo_pure_issue_response ' \
                    'where repo_id = '+str(repo_id) + ' and create_time between \"'+start_day +' \" and ' \
                    '\"'+end_day +'\"'
        else:
            order = 'select create_time,core_comment_count,first_core_comment_time from repo_pure_issue_response ' \
                    'where repo_id = '+str(repo_id) + ' and create_time between \"'+start_day +' \" and ' \
                    '\"'+end_day +'\"'
        cursor.execute(order)
        results = cursor.fetchall()
        for result in results:
            if result[1] == 0:
                continue
            # 计算first_comment_time在哪一个step内
            delta_days = (result[2]- datetime.datetime.strptime(startDay,fmt_day)).days
            step_index = int(delta_days/step)
            if step_index < time_count:
                day_count = (result[2] - result[0]).days + float((result[2] - result[0]).seconds)/86400    # 精确时间，单位为天
                if except_threshold < 0 or day_count < except_threshold:
                    issue_response_lists[step_index].append(day_count)
                    issue_pull_response_lists[step_index].append(day_count)
                else:
                    except_count_issue += 1
        all_count_issue += len(results)

        if core == 0:
            order = 'select create_time,comment_count,review_count,review_comment_count, ' \
                    'first_comment_time,first_review_time,first_review_comment_time from repo_pull_response ' \
                    'where repo_id = ' + str(repo_id) + ' and create_time between \"' + start_day + ' \" and ' \
                    '\"' + end_day + '\"'
        else:
            order = 'select create_time,core_comment_count,core_review_count,core_review_comment_count, ' \
                    'first_core_comment_time,first_core_review_time,first_core_review_comment_time from repo_pull_response ' \
                    'where repo_id = ' + str(repo_id) + ' and create_time between \"' + start_day + ' \" and ' \
                    '\"' + end_day + '\"'
        cursor.execute(order)
        results = cursor.fetchall()
        for result in results:
            if result[1]==0 and result[2]==0 and result[3]==0:
                continue
            day_count = -1
            tmp_index = -1
            for k in range(1,4):
                if result[k]!=0:
                    tmp_count = (result[k+3]-result[0]).days + float((result[k+3]-result[0]).seconds)/86400
                    if day_count < 0:
                        day_count = tmp_count
                        tmp_index = k+3
                    elif tmp_count < day_count:
                        day_count = tmp_count
                        tmp_index = k+3
            delta_days = (result[tmp_index]- datetime.datetime.strptime(startDay,fmt_day)).days
            step_index = int(delta_days / step)
            if step_index < time_count:
                if except_threshold < 0 or day_count < except_threshold:
                    pull_response_lists[step_index].append(day_count)
                    issue_pull_response_lists[step_index].append(day_count)
                else:
                    except_count_pull += 1
        all_count_pull += len(results)

    for i in range(time_count):
        start_day = (datetime.datetime.strptime(startDay, fmt_day) + datetime.timedelta(days=i * step)).strftime(
            fmt_day)
        end_day = (datetime.datetime.strptime(start_day, fmt_day) + datetime.timedelta(days=step)).strftime(
            fmt_day)
        time_list.append(step * i)
        if len(issue_response_lists[i]) == 0:
            print('1.not response for issues during:',start_day,'--',end_day)
            if none_response_mode == 0 or len(issue_response_mean)==0:
                issue_response_mean.append(-1)
                issue_response_median.append(-1)
            else:
                issue_response_mean.append(issue_response_mean[-1])
                issue_response_median.append(issue_response_median[-1])
        else:
            tmp_array = np.array(issue_response_lists[i])
            issue_response_mean.append(np.mean(tmp_array))
            issue_response_median.append(np.median(tmp_array))

        if len(pull_response_lists[i]) == 0:
            print('2.not response for pulls during:',start_day,'--',end_day)
            if none_response_mode == 0 or len(pull_response_mean)==0:
                pull_response_mean.append(-1)
                pull_response_median.append(-1)
            else:
                pull_response_mean.append(pull_response_mean[-1])
                pull_response_median.append(pull_response_median[-1])
        else:
            tmp_array = np.array(pull_response_lists[i])
            pull_response_mean.append(np.mean(tmp_array))
            pull_response_median.append(np.median(tmp_array))

        if len(issue_pull_response_lists[i]) == 0:
            print('3.not response for issues and pulls during:',start_day,'--',end_day)
            if none_response_mode == 0 or len(issue_pull_response_mean)==0:
                issue_pull_response_mean.append(-1)
                issue_pull_response_median.append(-1)
            else:
                issue_pull_response_mean.append(issue_pull_response_mean[-1])
                issue_pull_response_median.append(issue_pull_response_median[-1])
        else:
            tmp_array = np.array(issue_pull_response_lists[i])
            issue_pull_response_mean.append(np.mean(tmp_array))
            issue_pull_response_median.append(np.median(tmp_array))

    if all_count_issue == 0:
        print(str(except_count_issue) + '/' + str(all_count_issue) + ': 0%')
    else:
        print(str(except_count_issue) + '/' + str(all_count_issue) + ': ',
              "{0:.2f}".format(100.0 * except_count_issue / all_count_issue) + '%')
    if all_count_pull == 0:
        print(str(except_count_pull) + '/' + str(all_count_pull) + ': 0%')
    else:
        print(str(except_count_pull) + '/' + str(all_count_pull) + ': ',
              "{0:.2f}".format(100.0 * except_count_pull / all_count_pull) + '%')

    if data_filename!='':
        with open(data_filename,'w',encoding='utf-8')as f:
            f.write('time,issue_mean,pull_mean,issue_pull_mean,issue_median,pull_median,issue_pull_median,\n')
            for i in range(len(time_list)):
                line = str(time_list[i])+','
                line += str(issue_response_mean[i]) + ','
                line += str(pull_response_mean[i]) + ','
                line += str(issue_pull_response_mean[i]) + ','
                line += str(issue_response_median[i]) + ','
                line += str(pull_response_median[i]) + ','
                line += str(issue_pull_response_median[i]) + ','
                f.write(line+'\n')

    colors = ['red','darkred','green','darkgreen','blue','darkblue']
    plt.figure(figsize=(10, 5))
    plt.plot(time_list, issue_response_mean, linewidth=1.5, marker='.', markerfacecolor='w',
             color=colors[0], label='issue mean')
    plt.plot(time_list, issue_response_median, linewidth=1.5, marker='.', markerfacecolor='w',
             color=colors[1], label='issue median',alpha=0.7)
    plt.plot(time_list, pull_response_mean, linewidth=1.5, marker='.', markerfacecolor='w',
             color=colors[2], label='pull mean')
    plt.plot(time_list, pull_response_median, linewidth=1.5, marker='.', markerfacecolor='w',
             color=colors[3], label='pull median',alpha=0.7)
    plt.plot(time_list, issue_pull_response_mean, linewidth=1.5, marker='.', markerfacecolor='w',
             color=colors[4], label='issue & pull mean')
    plt.plot(time_list, issue_pull_response_median, linewidth=1.5, marker='.', markerfacecolor='w',
             color=colors[5], label='issue & pull median',alpha=0.7)
    plt.legend(loc='upper left')
    if core==0:
        plt.title('社区（repo_id=' + str(repo_id) + '）' + startDay + '~' + endDay + '期间issue和PR第一次响应时间随时间变化曲线')
    else:
        plt.title('社区（repo_id=' + str(repo_id) + '）' + startDay + '~' + endDay + '期间issue和PR第一次被社区内部人员响应'
                                                                                 '时间随时间变化曲线')
    if fig_name!='':
        plt.savefig(fig_name)
    plt.show()


# 绘制某一仓库平均每条纯issue、PR、issue(+PR)的响应频率的时序曲线，根据每step内的comment（review）进行统计
# core: 0--所有响应；1--core响应
# repo_id: 仓库id
# startDay: 起始日期
# endDay: 结束日期
# step: 计算数量的步长，默认每7天计算一次数量并求平均
# fig_name: 保存的图片名，如果为空字符串则不保存
# data_filename: 保存的数据问件名，如果为空字符串则不保存
def drawResponseRateCurveByComment(repo_id,startDay,endDay,step=7,core=0,fig_name='',data_filename=''):
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    timedelta = datetime.datetime.strptime(endDay, fmt_day) - datetime.datetime.strptime(startDay, fmt_day)
    time_count = int(timedelta.days / step)
    time_list = []
    # 分子
    issue_comment_counts = []
    pull_response_counts = []
    issue_pull_response_counts = []
    # 分母
    issue_counts = []
    pull_counts = []
    issue_pull_counts = []

    for i in range(time_count):
        print(str(i+1)+'/'+str(time_count))
        start_day = (datetime.datetime.strptime(startDay, fmt_day) + datetime.timedelta(days=i * step)).strftime(
            fmt_day)
        end_day = (datetime.datetime.strptime(start_day, fmt_day) + datetime.timedelta(days=step)).strftime(
            fmt_day)

        time_list.append(step * i)

        if core == 0:
            order = 'select issue_number from repo_issue_comment r1 ' \
                    'where repo_id = '+str(repo_id) + ' and create_time between \"'+start_day +' \" and ' \
                    '\"'+end_day +'\" and not exists (select id from repo_pull r2 where r1.repo_id = r2.repo_id ' \
                    'and r1.issue_number = r2.pull_number)'
        else:
            order = 'select issue_number from repo_issue_comment r1 ' \
                    'where repo_id = '+str(repo_id) + ' and is_core_issue_comment = 1 and create_time ' \
                    'between \"'+start_day +' \" and \"'+end_day +'\" and not exists ' \
                    '(select id from repo_pull r2 where r1.repo_id = r2.repo_id ' \
                    'and r1.issue_number = r2.pull_number)'
        cursor.execute(order)
        results = cursor.fetchall()
        issue_list = []
        for result in results:
            if result[0] not in issue_list:
                issue_list.append(result[0])
        issue_counts.append(len(issue_list))
        issue_comment_counts.append(len(results))

        if core == 0:
            order = 'select issue_number from repo_issue_comment r1 ' \
                    'where repo_id = '+str(repo_id) + ' and create_time between \"'+start_day +' \" and ' \
                    '\"'+end_day +'\" and exists (select id from repo_pull r2 where r1.repo_id = r2.repo_id ' \
                    'and r1.issue_number = r2.pull_number)'
        else:
            order = 'select issue_number from repo_issue_comment r1 ' \
                    'where repo_id = '+str(repo_id) + ' and is_core_issue_comment = 1 and create_time ' \
                    'between \"'+start_day +' \" and \"'+end_day +'\" and exists ' \
                    '(select id from repo_pull r2 where r1.repo_id = r2.repo_id ' \
                    'and r1.issue_number = r2.pull_number)'
        cursor.execute(order)
        results = cursor.fetchall()
        pull_list = []
        pull_id_list = []
        for result in results:
            if result[0] not in pull_list:
                pull_list.append(result[0])
                cursor.execute('select pull_id from repo_pull where repo_id = '+str(repo_id)+
                               ' and pull_number = '+str(result[0]))
                ret = cursor.fetchone()
                if ret:
                    pull_id_list.append(ret[0])
        response_count = len(results)
        issue_pull_counts.append(len(issue_list)+len(pull_list))################
        issue_pull_response_counts.append(issue_comment_counts[-1]+response_count)###############

        if core == 0:
            order = 'select pull_id from repo_review ' \
                    'where repo_id = '+str(repo_id) + ' and submit_time between \"'+start_day +' \" and ' \
                    '\"'+end_day +'\"'
        else:
            order = 'select pull_id from repo_review ' \
                    'where repo_id = '+str(repo_id) + ' and author_association!= \"NONE\" and ' \
                    'author_association!=\"CONTRIBUTOR\" and submit_time between ' \
                    '\"'+start_day +' \" and \"'+end_day +'\"'
        cursor.execute(order)
        results = cursor.fetchall()
        for result in results:
            if result[0] not in pull_id_list:
                pull_id_list.append(result[0])
        response_count += len(results)

        if core == 0:
            order = 'select pull_id from repo_review_comment ' \
                    'where repo_id = '+str(repo_id) + ' and create_time between \"'+start_day +' \" and ' \
                    '\"'+end_day +'\"'
        else:
            order = 'select pull_id from repo_review_comment ' \
                    'where repo_id = '+str(repo_id) + ' and author_association!= \"NONE\" and ' \
                    'author_association!=\"CONTRIBUTOR\" and create_time between ' \
                    '\"'+start_day +' \" and \"'+end_day +'\"'
        cursor.execute(order)
        results = cursor.fetchall()
        for result in results:
            if result[0] not in pull_id_list:
                pull_id_list.append(result[0])
        response_count += len(results)
        pull_counts.append(len(pull_id_list))
        pull_response_counts.append(response_count)

    issue_comment_rate = []
    pull_response_rate = []
    issue_pull_comment_rate = []
    for i in range(time_count):
        if issue_counts[i]==0:
            issue_comment_rate.append(0.0)
        else:
            issue_comment_rate.append(float(issue_comment_counts[i])/issue_counts[i])
        if pull_counts[i]==0:
            pull_response_rate.append(0.0)
        else:
            pull_response_rate.append(float(pull_response_counts[i])/pull_counts[i])
        if issue_pull_counts[i]==0:
            issue_pull_comment_rate.append(0.0)
        else:
            issue_pull_comment_rate.append(float(issue_pull_response_counts[i])/issue_pull_counts[i])

    if data_filename!='':
        with open(data_filename,'w',encoding='utf-8')as f:
            f.write('time,rate_issue,rate_pull,rate_issue_pull,\n')
            for i in range(len(time_list)):
                line = str(time_list[i])+','
                line += str(issue_comment_rate[i]) + ','
                line += str(pull_response_rate[i]) + ','
                line += str(issue_pull_comment_rate[i]) + ','
                f.write(line+'\n')

    colors = ['red','green','blue']
    plt.figure(figsize=(10, 5))
    plt.plot(time_list, issue_comment_rate, linewidth=1.5, marker='.', markerfacecolor='w',
             color=colors[0], label='issue response')
    plt.plot(time_list, pull_response_rate, linewidth=1.5, marker='.', markerfacecolor='w',
             color=colors[1], label='pull response',alpha=0.7)
    plt.plot(time_list, issue_pull_comment_rate, linewidth=1.5, marker='.', markerfacecolor='w',
             color=colors[2], label='issue & pull comment')
    plt.legend(loc='upper left')
    if core==0:
        plt.title('社区（repo_id=' + str(repo_id) + '）' + startDay + '~' + endDay + '期间平均每条issue和PR响应频率(/'
                  +str(step)+'天)变化曲线')
    else:
        plt.title('社区（repo_id=' + str(repo_id) + '）' + startDay + '~' + endDay + '期间平均每条issue和PR被社区内部'
                  '人员响应频率(/'+str(step)+'天)变化曲线')
    if fig_name!='':
        plt.savefig(fig_name)
    plt.show()


# 绘制某一仓库open状态的issue、PR、issue+PR的时序曲线
# repo_id: 仓库id
# startDay: 起始日期
# endDay: 结束日期
# step: 计算数量的步长，默认每7天计算一次数量并求平均
# fig_name: 保存的图片名，如果为空字符串则不保存
# data_filename: 保存的数据问件名，如果为空字符串则不保存
def drawOpenIssuePRCurve(repo_id,startDay,endDay,step=7,fig_name='',data_filename=''):
    dbObject = draw_return_visit_curve.dbHandle()
    cursor = dbObject.cursor()
    timedelta = datetime.datetime.strptime(endDay, fmt_day) - datetime.datetime.strptime(startDay, fmt_day)
    time_count = int(timedelta.days / step)

    time_list = []
    open_issue_counts = []
    open_pull_counts = []
    open_issue_pull_counts = []

    for i in range(time_count):
        print(str(i + 1) + '/' + str(time_count))
        start_day = (datetime.datetime.strptime(startDay, fmt_day) + datetime.timedelta(days=i * step)).strftime(
            fmt_day)
        end_day = (datetime.datetime.strptime(start_day, fmt_day) + datetime.timedelta(days=step)).strftime(
            fmt_day)
        time_list.append(step * i)

        cursor.execute('select count(*) from repo_issue where repo_id = '+str(repo_id)+ ' and create_time < \"'
                       + end_day + '\" and close_time > \"'+ end_day + '\"')
        result1 = cursor.fetchone()
        open_issue_pull_counts.append(result1[0])

        cursor.execute('select count(*) from repo_pull where repo_id = ' + str(repo_id) + ' and create_time < \"'
                       + end_day + '\" and close_time > \"'+ end_day + '\"')
        result2 = cursor.fetchone()
        open_pull_counts.append(result2[0])
        open_issue_counts.append(result1[0]-result2[0])

    if data_filename!='':
        with open(data_filename,'w',encoding='utf-8')as f:
            f.write('time,open_issue,open_pull,open_issue_pull,\n')
            for i in range(len(time_list)):
                line = str(time_list[i])+','
                line += str(open_issue_counts[i]) + ','
                line += str(open_pull_counts[i]) + ','
                line += str(open_issue_pull_counts[i]) + ','
                f.write(line+'\n')

    colors = ['red','green','blue']
    plt.figure(figsize=(10, 5))
    plt.plot(time_list, open_issue_counts, linewidth=1.5, marker='.', markerfacecolor='w',
             color=colors[0], label='issue response')
    plt.plot(time_list, open_pull_counts, linewidth=1.5, marker='.', markerfacecolor='w',
             color=colors[1], label='pull response',alpha=0.7)
    plt.plot(time_list, open_issue_pull_counts, linewidth=1.5, marker='.', markerfacecolor='w',
             color=colors[2], label='issue & pull comment')
    plt.legend(loc='upper left')
    plt.title('社区（repo_id=' + str(repo_id) + '）' + startDay + '~' + endDay + '期间open状态的issue和PR数量变化曲线(step='
              + str(step) +')')
    if fig_name!='':
        plt.savefig(fig_name)
    plt.show()


# 绘制某一仓库open状态的issue、PR、issue+PR的平均寿命/寿命中位数时序曲线
# repo_id: 仓库id
# startDay: 起始日期
# endDay: 结束日期
# step: 计算数量的步长，默认每7天计算一次数量并求平均
# fig_name: 保存的图片名，如果为空字符串则不保存
# data_filename: 保存的数据问件名，如果为空字符串则不保存
# except_threshold: 大于0时，大等于该阈值的age被剔除；默认为-1，不剔除任何数据
def drawOpenIssuePRAgeCurve(repo_id,startDay,endDay,step=7,fig_name='',data_filename='',except_threshold=-1):
    dbObject = draw_return_visit_curve.dbHandle()
    cursor = dbObject.cursor()
    timedelta = datetime.datetime.strptime(endDay, fmt_day) - datetime.datetime.strptime(startDay, fmt_day)
    time_count = int(timedelta.days / step)

    time_list = []
    issue_age_mean = []
    issue_age_median = []
    pull_age_mean = []
    pull_age_median = []
    issue_pull_age_mean = []
    issue_pull_age_median = []

    except_count_issue = 0
    except_count_pull = 0
    all_count_issue = 0
    all_count_pull = 0

    for i in range(time_count):
        print(str(i + 1) + '/' + str(time_count))
        start_day = (datetime.datetime.strptime(startDay, fmt_day) + datetime.timedelta(days=i * step)).strftime(
            fmt_day)
        end_day = (datetime.datetime.strptime(start_day, fmt_day) + datetime.timedelta(days=step)).strftime(
            fmt_day)
        time_list.append(step * i)

        cursor.execute('select create_time from repo_issue r1 where repo_id = ' + str(repo_id) + ' and create_time < \"'
                       + end_day + '\" and close_time > \"' + end_day + '\" and not exists (select id from repo_pull r2 '
                       'where r1.repo_id = r2.repo_id and r1.issue_number = r2.pull_number)')
        results = cursor.fetchall()
        age_list_1 = []
        age_list_3 = []
        for result in results:
            count = (datetime.datetime.strptime(end_day,fmt_day)-result[0]).days
            if except_threshold < 0 or count < except_threshold:
                age_list_1.append(count)
                age_list_3.append(count)
            else:
                except_count_issue += 1
        all_count_issue += len(results)

        cursor.execute('select create_time from repo_pull where repo_id = ' + str(repo_id) + ' and create_time < \"'
                       + end_day + '\" and close_time > \"' + end_day + '\"')
        results = cursor.fetchall()
        age_list_2 = []
        for result in results:
            count = (datetime.datetime.strptime(end_day, fmt_day) - result[0]).days
            if except_threshold < 0 or count < except_threshold:
                age_list_2.append(count)
                age_list_3.append(count)
            else:
                except_count_pull += 1
        all_count_pull += len(results)

        if len(age_list_1)==0:
            issue_age_mean.append(0)
            issue_age_median.append(0)
        else:
            tmp_array = np.array(age_list_1)
            # if np.mean(tmp_array)>200:
            #     print(i*step,end=': ')
            #     print(age_list_1)
            issue_age_mean.append(np.mean(tmp_array))
            issue_age_median.append(np.median(tmp_array))
        if len(age_list_2)==0:
            pull_age_mean.append(0)
            pull_age_median.append(0)
        else:
            tmp_array = np.array(age_list_2)
            pull_age_mean.append(np.mean(tmp_array))
            pull_age_median.append(np.median(tmp_array))
        if len(age_list_3)==0:
            issue_pull_age_mean.append(0)
            issue_pull_age_median.append(0)
        else:
            tmp_array = np.array(age_list_3)
            issue_pull_age_mean.append(np.mean(tmp_array))
            issue_pull_age_median.append(np.median(tmp_array))

    if all_count_issue == 0:
        print(str(except_count_issue) + '/' + str(all_count_issue) + ': 0%')
    else:
        print(str(except_count_issue) + '/' + str(all_count_issue) + ': ',
              "{0:.2f}".format(100.0 * except_count_issue / all_count_issue) + '%')
    if all_count_pull == 0:
        print(str(except_count_pull) + '/' + str(all_count_pull) + ': 0%')
    else:
        print(str(except_count_pull) + '/' + str(all_count_pull) + ': ',
              "{0:.2f}".format(100.0 * except_count_pull / all_count_pull) + '%')

    if data_filename!='':
        with open(data_filename,'w',encoding='utf-8')as f:
            f.write('time,issue_mean,pull_mean,issue_pull_mean,issue_median,pull_median,issue_pull_median,\n')
            for i in range(len(time_list)):
                line = str(time_list[i])+','
                line += str(issue_age_mean[i]) + ','
                line += str(pull_age_mean[i]) + ','
                line += str(issue_pull_age_mean[i]) + ','
                line += str(issue_age_median[i]) + ','
                line += str(pull_age_median[i]) + ','
                line += str(issue_pull_age_median[i]) + ','
                f.write(line+'\n')

    colors = ['red','darkred','green','darkgreen','blue','darkblue']
    plt.figure(figsize=(10, 5))
    plt.plot(time_list, issue_age_mean, linewidth=1.5, marker='.', markerfacecolor='w',
             color=colors[0], label='issue mean')
    plt.plot(time_list, issue_age_median, linewidth=1.5, marker='.', markerfacecolor='w',
             color=colors[1], label='issue median',alpha=0.7)
    plt.plot(time_list, pull_age_mean, linewidth=1.5, marker='.', markerfacecolor='w',
             color=colors[2], label='pull mean')
    plt.plot(time_list, pull_age_median, linewidth=1.5, marker='.', markerfacecolor='w',
             color=colors[3], label='pull median',alpha=0.7)
    plt.plot(time_list, issue_pull_age_mean, linewidth=1.5, marker='.', markerfacecolor='w',
             color=colors[4], label='issue & pull mean')
    plt.plot(time_list, issue_pull_age_median, linewidth=1.5, marker='.', markerfacecolor='w',
             color=colors[5], label='issue & pull median',alpha=0.7)
    plt.legend(loc='upper left')
    plt.title('社区（repo_id=' + str(repo_id) + '）' + startDay + '~' + endDay + '期间open状态的issue和PR的平均/中位数寿命随时间变化曲线')
    if fig_name!='':
        plt.savefig(fig_name)
    plt.show()


# # 获取仓库特定时间段内所有第一次响应时间的分布图
# def getResponseTimeDistribution(repo_id,startDay,endDay,step=7,fig_name='',data_filename=''):
#     dbObject = dbHandle()
#     cursor = dbObject.cursor()
#     cursor.execute('select create_time')


def drawNewMetricCurveForRepos():
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select id,repo_id,created_at from churn_search_repos_final '
                   'where id > 10 and id != 25 and id != 26 and id != 27 and id != 29')
    results = cursor.fetchall()

    response_time_curve_dir = r'E:\bysj_project\new_metrics\time_sequence_28\first_response_time_charts'
    response_time_data_dir = r'E:\bysj_project\new_metrics\time_sequence_28\first_response_time_data'
    core_response_time_curve_dir = r'E:\bysj_project\new_metrics\time_sequence_28\core_first_response_time_charts'
    core_response_time_data_dir = r'E:\bysj_project\new_metrics\time_sequence_28\core_first_response_time_data'
    response_rate_curve_dir = r'E:\bysj_project\new_metrics\time_sequence_28\response_rate_charts'
    response_rate_data_dir = r'E:\bysj_project\new_metrics\time_sequence_28\response_rate_data'
    core_response_rate_curve_dir = r'E:\bysj_project\new_metrics\time_sequence_28\core_response_rate_charts'
    core_response_rate_data_dir = r'E:\bysj_project\new_metrics\time_sequence_28\core_response_rate_data'
    open_count_curve_dir = r'E:\bysj_project\new_metrics\time_sequence_28\open_state_charts'
    open_count_data_dir = r'E:\bysj_project\new_metrics\time_sequence_28\open_state_data'
    open_age_curve_dir = r'E:\bysj_project\new_metrics\time_sequence_28\open_age_charts'
    open_age_data_dir = r'E:\bysj_project\new_metrics\time_sequence_28\open_age_data'

    filenames = os.listdir(r'E:\bysj_project\time_sequence_28\time_sequence_charts')
    id_filename = dict()
    for filename in filenames:
        id_filename[int(filename.split('_')[0])]=filename

    for result in results:
        id = result[0]
        repo_id =result[1]
        startDay = result[2][0:10]
        endDay = '2022-01-01'

        fig_name = id_filename[id]
        data_filename = id_filename[id].replace('.png','.csv')

        drawOpenIssuePRCurve(repo_id,startDay,endDay,28,open_count_curve_dir+'/'+fig_name,
                             open_count_data_dir+'/'+data_filename)

        drawResponseRateCurveByComment(repo_id,startDay,endDay,28,0,response_rate_curve_dir+'/'+fig_name,
                                       response_rate_data_dir+'/'+data_filename)
        drawResponseRateCurveByComment(repo_id,startDay,endDay,28,1,core_response_rate_curve_dir+'/'+fig_name,
                                       core_response_rate_data_dir+'/'+data_filename)

        drawResponseTimeCurveByComment(repo_id,startDay,endDay,28,0,response_time_curve_dir+'/'+fig_name,
                                       response_time_data_dir+'/'+data_filename)
        drawResponseTimeCurveByComment(repo_id, startDay, endDay, 28, 1, core_response_time_curve_dir + '/' + fig_name,
                                       core_response_time_data_dir + '/' + data_filename)
        drawOpenIssuePRAgeCurve(repo_id,startDay,endDay,28,open_age_curve_dir+'/'+fig_name,
                                open_age_data_dir+'/'+data_filename)

