from churn_data_analysis.draw_return_visit_curve import dbHandle
import datetime
time_fmt = '%Y-%m-%d'

# 获取社区一段时间内的开发者id列表，包含fork和star的用户
# repo_id:仓库id
# startDay:筛选时间段的起始日期（包含）
# endDay:筛选时间段的终止日期（不含）
# exceptList:排除的用户id
def getRepoAllUserList(repo_id,startDay,endDay,exceptList=None):
    if exceptList is None:
        exceptList = []
    userList = []
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute(
        'select distinct user_id from repo_issue ' \
        'where repo_id = '+str(repo_id)+' and create_time between \"'+str(startDay)\
        +'\" and \"'+str(endDay)+'\"'
    )
    results = cursor.fetchall()
    for result in results:
        if result[0] not in userList and result[0] not in exceptList:
            userList.append(result[0])
    cursor.execute(
        'select distinct user_id from repo_issue_comment ' \
        'where repo_id = ' + str(repo_id) + ' and create_time between \"' + str(startDay) \
        + '\" and \"' + str(endDay) + '\"'
    )
    results = cursor.fetchall()
    for result in results:
        if result[0] not in userList and result[0] not in exceptList:
            userList.append(result[0])
    cursor.execute(
        'select distinct user_id from repo_pull ' \
        'where repo_id = ' + str(repo_id) + ' and create_time between \"' + str(startDay) \
        + '\" and \"' + str(endDay) + '\"'
    )
    results = cursor.fetchall()
    for result in results:
        if result[0] not in userList and result[0] not in exceptList:
            userList.append(result[0])
    cursor.execute(
        'select distinct user_id from repo_review ' \
        'where repo_id = ' + str(repo_id) + ' and submit_time between \"' + str(startDay) \
        + '\" and \"' + str(endDay) + '\"'
    )
    results = cursor.fetchall()
    for result in results:
        if result[0] not in userList and result[0] not in exceptList:
            userList.append(result[0])
    cursor.execute(
        'select distinct user_id from repo_review_comment ' \
        'where repo_id = ' + str(repo_id) + ' and create_time between \"' + str(startDay) \
        + '\" and \"' + str(endDay) + '\"'
    )
    results = cursor.fetchall()
    for result in results:
        if result[0] not in userList and result[0] not in exceptList:
            userList.append(result[0])
    cursor.execute(
        'select distinct user_id from repo_commit ' \
        'where repo_id = ' + str(repo_id) + ' and commit_time between \"' + str(startDay) \
        + '\" and \"' + str(endDay) + '\"'
    )
    results = cursor.fetchall()
    for result in results:
        if result[0] not in userList and result[0] not in exceptList:
            userList.append(result[0])
    cursor.execute(
        'select distinct user_id from repo_commit_comment ' \
        'where repo_id = ' + str(repo_id) + ' and comment_time between \"' + str(startDay) \
        + '\" and \"' + str(endDay) + '\"'
    )
    results = cursor.fetchall()
    for result in results:
        if result[0] not in userList and result[0] not in exceptList:
            userList.append(result[0])
    cursor.execute(
        'select distinct user_id from repo_fork ' \
        'where repo_id = ' + str(repo_id) + ' and create_time between \"' + str(startDay) \
        + '\" and \"' + str(endDay) + '\"'
    )
    results = cursor.fetchall()
    for result in results:
        if result[0] not in userList and result[0] not in exceptList:
            userList.append(result[0])
    cursor.execute(
        'select distinct user_id from repo_star ' \
        'where repo_id = ' + str(repo_id) + ' and star_time between \"' + str(startDay) \
        + '\" and \"' + str(endDay) + '\"'
    )
    results = cursor.fetchall()
    for result in results:
        if result[0] not in userList and result[0] not in exceptList:
            userList.append(result[0])
    return userList


def getUserActivity(user_id,repo_id,startDay,endDay,with_commit=False):
    count_list = [0,0,0,0,0,0,0,0,0,0]
    table_list = [
        'repo_issue_comment',
        'repo_issue',
        'repo_pull',
        'repo_review_comment',
        'repo_pull_merged',
        'repo_star',
        'repo_fork',
        'repo_commit',  #
        'repo_commit_comment',  #
        'repo_review'   #
    ]
    time_list = [
        'create_time',
        'create_time',
        'create_time',
        'create_time',
        'merge_time',
        'star_time',
        'create_time',
        'commit_time',  #
        'comment_time', #
        'submit_time'   #
    ]
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    for i in range(len(count_list)):
        cursor.execute('select count(*) from '+table_list[i]+' where user_id = '+str(user_id)+' and repo_id = '+str(repo_id)
                   +' and '+ time_list[i]+' between \"' + str(startDay) \
                   + '\" and \"' + str(endDay) + '\"')
        result = cursor.fetchone()
        count_list[i] = result[0]
    userActivity = count_list[0] + 2 * count_list[1] + 3 * count_list[2] + 4 * count_list[3] + 2 * count_list[4] + \
                   count_list[5] + 2 * count_list[6]
    if with_commit == True:##########################?????????????????????
        userActivity += 3 * count_list[7] + 2 * count_list[8] + 2 * count_list[9]
    # print('\t',repo_id,user_id,userActivity)
    return userActivity


# 获取社区一段时间内的活跃度
# repo_id:仓库id
# startDay:筛选时间段的起始日期（包含）
# endDay:筛选时间段的终止日期（不含）
def getRepoActivity(repo_id,startDay,endDay,with_commit=False):
    start_time = datetime.datetime.strptime(startDay,time_fmt)
    end_time = datetime.datetime.strptime(endDay,time_fmt)
    timedelta = (end_time-start_time).days
    userList = getRepoAllUserList(repo_id,startDay,endDay)
    activitySum = 0
    for user_id in userList:
        activitySum += getUserActivity(user_id,repo_id,startDay,endDay,with_commit=with_commit)
    repoActivity = float(activitySum)/timedelta
    print('\t',repo_id,startDay+'--'+endDay,repoActivity)#########################
    return repoActivity


# 根据一定步长统计社区全部历史每个时间段的活跃度，并保存在文件中
def saveRepoActivity(repo_id,filename,step=7,with_commit=False):
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select created_at from churn_search_repos_final where repo_id = ' + str(repo_id))
    result = cursor.fetchone()
    create_time = result[0][0:10]
    end_time = '2022-01-01'
    timedelta = (datetime.datetime.strptime(end_time,time_fmt)-datetime.datetime.strptime(create_time,time_fmt)).days

    startTime = datetime.datetime.strptime(create_time,time_fmt)
    endTime = startTime + datetime.timedelta(days=step)
    step_count = int(timedelta/step)
    time_list = []
    activity_list = []
    with open(filename,'w',encoding='utf-8')as f:
        f.write('time_list,activity_list,\n')
    for i in range(step_count):
        startDay = startTime.strftime(time_fmt)
        endDay = endTime.strftime(time_fmt)
        repoActivity = getRepoActivity(repo_id, startDay, endDay,with_commit=with_commit)
        time_list.append(i * step)
        activity_list.append(repoActivity)
        with open(filename, 'a', encoding='utf-8')as f:
            f.write(str(i * step) + ',' + str(repoActivity) + ',\n')
        startTime = endTime
        endTime += datetime.timedelta(days=step)
        if endTime > datetime.datetime.strptime(end_time, time_fmt):
            endTime = datetime.datetime.strptime(end_time, time_fmt)
    print(time_list)
    print(activity_list)
    return time_list,activity_list


# 为所有仓库保存活跃度数据
# save_dir: 保存图像和曲线数据的文件夹的名称
# with_commit:活跃度数据是否考虑commit、commit comment和 review
def saveActivityForRepos(save_dir,step=7,with_commit=False):
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    order = 'select id,repo_name,repo_id from churn_search_repos_final'
    cursor.execute(order)
    results = cursor.fetchall()

    for result in results:
        filename = save_dir + '/repo_activity_'+str(step)+'/' + str(result[0]) + '_' + result[1].replace('/', '_') \
                  + '-activity.csv'
        repo_id = result[2]
        print(repo_id)
        saveRepoActivity(repo_id,filename,step,with_commit=with_commit)


if __name__ == '__main__':
    repo_id = '156401841'
    startDay = '2021-12-01'
    endDay = '2022-01-01'
    # getRepoActivity(repo_id,startDay,endDay)
    # saveRepoActivity(repo_id,'C:/Users/cxy/Desktop/test/test_activity.csv',7)

    # saveActivityForRepos('E:/bysj_project/repo_activity/without_commit', 7, False)
    saveActivityForRepos('E:/bysj_project/repo_activity/with_commit', 7, True)
    # saveActivityForRepos('E:/bysj_project/repo_activity/without_commit', 28, False)
    # saveActivityForRepos('E:/bysj_project/repo_activity/with_commit', 28, True)