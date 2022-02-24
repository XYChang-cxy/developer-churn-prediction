import matplotlib
import matplotlib.pyplot as plt
import churn_data_analysis.settings as settings
import pymysql
import datetime

matplotlib.rcParams['font.sans-serif'] = ['KaiTi']
matplotlib.rcParams['axes.unicode_minus'] = False

fmt_MySQL = '%Y-%m-%d'

def dbHandle():
    conn = pymysql.connect(
        host=settings.MYSQL_HOST,
        db=settings.MYSQL_DBNAME,
        user=settings.MYSQL_USER,
        passwd=settings.MYSQL_PASSWD,
        charset='utf8',
        use_unicode=True
    )
    return conn

# 获取社区一段时间内的开发者id列表，不考虑fork和star的用户
# repo_id:仓库id
# startDay:筛选时间段的起始日期（包含）
# endDay:筛选时间段的终止日期（不含）
# exceptList:排除的用户id
def getRepoUserList(repo_id,startDay,endDay,exceptList=None):
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
    return userList


# 绘制社区流失开发者在不同流失期限下的回访率曲线
# repo_id:仓库id
# startDay:筛选时间段的起始日期（包含）
# endDay:筛选时间段的终止日期（不含）
# max_weeks:横坐标流失期限的最大值
# if_draw:是否绘制回访率曲线
# exceptList:排除的用户id
# 返回值：dict类型，{user_id:未活动周数}
def drawReturnVisitRateCurve(repo_id, startDay, endDay, max_weeks=52, if_draw = True, exceptList = None):
    user_inactive_weeks = dict() #用户连续为活动周数，动态变化
    timedelta = datetime.datetime.strptime(endDay, fmt_MySQL)-datetime.datetime.strptime(startDay, fmt_MySQL)
    period_weeks = int(timedelta.days/7)
    churn_counts = [] #不同流失期限下的流失用户数
    return_counts = [] #不同流失期限下的回访用户数
    for i in range(max_weeks+1):
        churn_counts.append(0)
        return_counts.append(0)
    start_day = startDay
    end_day = (datetime.datetime.strptime(start_day, fmt_MySQL) + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    print(start_day, end_day)
    for i in range(period_weeks):
        active_user_list = getRepoUserList(repo_id,startDay=start_day,endDay=end_day,exceptList=exceptList)
        for user_id in user_inactive_weeks.keys():
            if user_inactive_weeks[user_id] > 0 and user_id in active_user_list:  # 上周未活动但本周有活动
                for j in range(1,user_inactive_weeks[user_id]+1):  # 对应不同流失期限下的用户回访数增加
                    if j > max_weeks:
                        print('j>max_weeks')
                        break
                    return_counts[j]+=1
                user_inactive_weeks[user_id] = 0    #用户回访后为活动周数置零
            elif user_id not in active_user_list:   #该用户本周没有活动
                if user_inactive_weeks[user_id] < max_weeks:
                    user_inactive_weeks[user_id]+=1
                    # 注意流失数的增加和回归数的增加情形不完全相同
                    churn_counts[user_inactive_weeks[user_id]]+=1
        for user_id in active_user_list:    # 将新的用户不断添加道user_inactive_weeks中
            if user_id not in user_inactive_weeks.keys():
                user_inactive_weeks.update({user_id:0}) #新加入社区的用户
        start_day = end_day
        end_day = (datetime.datetime.strptime(start_day, fmt_MySQL) + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
        if end_day > endDay:
            end_day = endDay
        print(start_day,end_day)
    weeks = []
    rates = []
    for i in range(1, max_weeks + 1):
        weeks.append(i)
        if churn_counts[i] == 0:
            rates.append(0.0)
        else:
            rates.append(100.0 * float(return_counts[i]) / churn_counts[i])
    print(rates)#############
    plt.plot(weeks, rates, label='用户回访率', linewidth=1, color='g', marker='.', markerfacecolor='w')
    plt.legend(loc="upper right")
    plt.xlabel('流失期限（周）')
    plt.ylabel('用户回访率（%）')
    plt.title('社区（repo_id = ' + str(repo_id) + '）'+startDay+'~'+endDay+'期间用户回访率曲线')
    plt.show()

    return user_inactive_weeks

if __name__ == '__main__':
    startDay = '2017-12-01'
    endDay = '2022-01-01'
    repo_id = 7276954
    drawReturnVisitRateCurve(repo_id,startDay,endDay)