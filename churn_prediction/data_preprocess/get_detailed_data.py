# 该文件用于获取模型训练和验证的详细数据，并存储到文件中
from churn_prediction.data_preprocess.database_connect import *
from churn_prediction.get_churn_limit import getChurnLimitLists,getChurnLimitListForRepo
import datetime
import numpy as np
import pandas as pd
from churn_prediction.data_preprocess.developer_collaboration_network import *


# 获取数量相关指标的数据并存储
# id:仓库序号（1~30）
# user_period_file: 存储用户观察区间的文件
# period_length: 120或30,和user_period_file对应
# count_type: 数据类型，可选项包括：issue、issue comment、pull、pull merged、review、review comment、commit
def getCountDataAndSave(id,user_period_file,period_length,count_type,save_dir):
    time_names = {
        'issue':'create_time',
        'issue comment':'create_time',
        'pull':'create_time',
        'pull merged':'merge_time',
        'review':'submit_time',
        'review comment':'create_time',
        'commit':'commit_time'
    }
    if period_length == 120:
        step = 10
    elif period_length == 30:
        step = 5
    else:
        print('period length error!')
        return
    if count_type not in time_names.keys():
        print('Data type error:',count_type+' not exist!')
        return

    user_periods = []
    with open(user_period_file,'r',encoding='utf-8')as f:
        f.readline()
        for line in f.readlines():
            items = line.strip(',\n').split(',')
            user_periods.append([int(items[0]),items[1],items[2]])
    f.close()

    if user_period_file.find('/')!=-1:
        user_type = user_period_file.split('/')[-1].split('_')[1]
    else:
        user_type = user_period_file.split('\\')[-1].split('_')[1]
    filename = save_dir + '/' + user_type + '_' + count_type.replace(' ', '_') \
               + user_period_file[user_period_file.split('/')[-1].find('-'):]
    print(filename)

    table_name = 'repo_' + count_type.replace(' ', '_')
    time_name = time_names[count_type]

    with open(filename,'w',encoding='utf-8')as f:
        line = 'user_id,'
        for i in range(int(period_length/step)):
            line+=str(i)+','
        f.write(line+'\n')
    f.close()

    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select repo_id from churn_search_repos_final where id = '+str(id))
    repo_id = cursor.fetchone()[0]

    for user_period in user_periods:
        user_id = user_period[0]
        startDay = user_period[1]
        endDay = user_period[2]
        count_list = []
        for i in range(int(period_length/step)):
            start_day = (datetime.datetime.strptime(startDay,fmt_day)+datetime.timedelta(days=i*step)).strftime(fmt_day)
            end_day = (datetime.datetime.strptime(start_day,fmt_day)+datetime.timedelta(days=step)).strftime(fmt_day)
            cursor.execute('select count(*) from '+table_name+' where repo_id = '+str(repo_id)+' and '
                           'user_id = '+str(user_id)+' and '+time_name+' between \"'+start_day+'\" and \"'
                           + end_day+'\"')
            count = cursor.fetchone()[0]
            count_list.append(count)
        line = str(user_id)+','
        for count in count_list:
            line += str(count)+','
        with open(filename,'a',encoding='utf-8')as f:
            f.write(line+'\n')
        f.close()


# 获取开发者在协作网络中的介数中心性或节点加权度
# id:仓库序号（1~30）
# user_period_file: 存储用户观察区间的文件
# period_length: 120或30,和user_period_file对应
# data_type: 数据类型，可选项包括：betweeness、weighted degree
def getDCNDataAndSave(id,user_period_file,period_length,data_type,save_dir):
    if period_length == 120:
        step = 10
    elif period_length == 30:
        step = 5
    else:
        print('period length error!')
        return
    if data_type!='betweeness' and data_type!='weighted degree':
        print('Data type error: '+data_type+' not exist!')
        return

    user_periods = []
    with open(user_period_file, 'r', encoding='utf-8')as f:
        f.readline()
        for line in f.readlines():
            items = line.strip(',\n').split(',')
            user_periods.append([int(items[0]), items[1], items[2]])
    f.close()

    if user_period_file.find('/') != -1:
        user_type = user_period_file.split('/')[-1].split('_')[1]
    else:
        user_type = user_period_file.split('\\')[-1].split('_')[1]
    filename = save_dir + '/' + user_type + '_' + data_type.replace(' ','_') \
               + user_period_file[user_period_file.split('/')[-1].find('-'):]
    print(filename)
    with open(filename,'w',encoding='utf-8')as f:
        line = 'user_id,'
        for i in range(int(period_length/step)):
            line+=str(i)+','
        f.write(line+'\n')
    f.close()

    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select repo_id from churn_search_repos_final where id = '+str(id))
    repo_id = cursor.fetchone()[0]

    for index in range(len(user_periods)):
        print(index,'/',len(user_periods))
        user_period = user_periods[index]
        user_id = user_period[0]
        startDay = user_period[1]
        endDay = user_period[2]
        value_list = []
        for i in range(int(period_length / step)):
            start_day = (datetime.datetime.strptime(startDay, fmt_day) + datetime.timedelta(days=i * step)).strftime(
                fmt_day)
            end_day = (datetime.datetime.strptime(start_day, fmt_day) + datetime.timedelta(days=step)).strftime(fmt_day)
            DCN, DCN0, index_user, user_index = getDeveloperCollaborationNetwork(repo_id,start_day,end_day)
            if data_type == 'betweeness':
                value = getUserDCNWeightedDegrees(user_id,user_index,DCN)
            else:
                value = getUserBetweeness(user_id,DCN,user_index,index_user,True)
            value_list.append(value)
        line = str(user_id) + ','
        for value in value_list:
            line += str(value) + ','
        with open(filename, 'a', encoding='utf-8')as f:
            f.write(line + '\n')
        f.close()


# 获取开发者接受到的响应数据并存储
# id:仓库序号（1~30）
# user_period_file: 存储用户观察区间的文件
# period_length: 120或30,和user_period_file对应
# data_type: 数据类型，可选项包括：issue comment、review、review comment
def getReceivedDataAndSave(id,user_period_file,period_length,data_type,save_dir):
    if period_length == 120:
        step = 10
    elif period_length == 30:
        step = 5
    else:
        print('period length error!')
        return
    if data_type!='issue comment' and data_type!='review' and data_type!='review comment':
        print('Data type error: '+data_type+' not exist!')
        return
    user_periods = []
    with open(user_period_file, 'r', encoding='utf-8')as f:
        f.readline()
        for line in f.readlines():
            items = line.strip(',\n').split(',')
            user_periods.append([int(items[0]), items[1], items[2]])
    f.close()

    if user_period_file.find('/') != -1:
        user_type = user_period_file.split('/')[-1].split('_')[1]
    else:
        user_type = user_period_file.split('\\')[-1].split('_')[1]
    filename = save_dir + '/' + user_type + '_received_' + data_type.replace(' ','_') \
               + user_period_file[user_period_file.split('/')[-1].find('-'):]
    print(filename)
    with open(filename, 'w', encoding='utf-8')as f:
        line = 'user_id,'
        for i in range(int(period_length / step)):
            line += str(i) + ','
        f.write(line + '\n')
    f.close()

    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select repo_id from churn_search_repos_final where id = ' + str(id))
    repo_id = cursor.fetchone()[0]
    for index in range(len(user_periods)):
        print(index,'/',len(user_periods))
        user_period = user_periods[index]
        user_id = user_period[0]
        startDay = user_period[1]
        endDay = user_period[2]
        count_list = []
        for i in range(int(period_length / step)):
            start_day = (datetime.datetime.strptime(startDay, fmt_day) + datetime.timedelta(days=i * step)).strftime(
                fmt_day)
            end_day = (datetime.datetime.strptime(start_day, fmt_day) + datetime.timedelta(days=step)).strftime(fmt_day)
            if data_type == 'issue comment':
                cursor.execute('select issue_number from repo_issue where repo_id = ' + str(repo_id) + ' and '
                               'user_id = ' + str(user_id) + ' and create_time < \"'+ end_day + '\"')
                results = cursor.fetchall()
                issue_number_list = []
                for result in results:
                    issue_number_list.append(result[0])
                if len(issue_number_list)==0:
                    count_list.append(0)
                else:
                    cursor.execute('select issue_number from repo_issue_comment where repo_id = '
                                   +str(repo_id)+' and create_time between \"' + start_day + '\" and \"'
                                   + end_day + '\"')
                    results = cursor.fetchall()
                    count = 0
                    for result in results:
                        if result[0] in issue_number_list:
                            count += 1
                    count_list.append(count)
            else:
                cursor.execute('select pull_id from repo_pull where repo_id = ' + str(repo_id) + ' and '
                               'user_id = ' + str(user_id) + ' and create_time < \"'+ end_day + '\"')
                results = cursor.fetchall()
                pull_list = []
                for result in results:
                    pull_list.append(result[0])
                if len(pull_list)==0:
                    count_list.append(0)
                else:
                    table_name = 'repo_'+data_type.replace(' ','_')
                    if table_name=='repo_review':
                        time_name = 'submit_time'
                    else:
                        time_name = 'create_time'
                    cursor.execute('select pull_id from '+table_name+' where repo_id = '
                                   +str(repo_id)+' and '+time_name+' between \"' + start_day + '\" and \"'
                                   + end_day + '\"')
                    results = cursor.fetchall()
                    count = 0
                    for result in results:
                        if result[0] in pull_list:
                            count += 1
                    count_list.append(count)
        line = str(user_id) + ','
        for count in count_list:
            line += str(count) + ','
        with open(filename, 'a', encoding='utf-8')as f:
            f.write(line + '\n')
        f.close()



# if __name__ == '__main__':
#     # getCountDataAndSave(2,r'C:\Users\cxy\Desktop\test\repo_loyalers_period-120-0.0.csv',120,'commit',
#     #                     r'C:\Users\cxy\Desktop\test')
#     # getDCNDataAndSave(2, r'C:\Users\cxy\Desktop\test\repo_loyalers_period-120-0.0.csv', 120, 'betweeness',
#     #                     r'C:\Users\cxy\Desktop\test')
#     getReceivedDataAndSave(2, r'C:\Users\cxy\Desktop\test\repo_loyalers_period-120-0.0.csv', 120, 'review comment',
#                       r'C:\Users\cxy\Desktop\test')