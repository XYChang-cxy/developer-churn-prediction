import matplotlib
import matplotlib.pyplot as plt
import churn_data_analysis.settings as settings
import pymysql
import datetime
import numpy as np
from scipy.interpolate import make_interp_spline
from kneed import KneeLocator

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


def compareRole(role1,role2):
    if role1 == role2:
        return 0
    elif role1 == 'OWNER':
        return 1
    elif role1 == 'MEMBER' and role2 != 'OWNER':
        return 1
    elif role1 == 'COLLABORATOR' and (role2 == 'CONTRIBUTOR' or role2 == 'NONE'):
        return 1
    elif role1 == 'CONTRIBUTOR' and role2 == 'NONE':
        return 1
    else:
        return -1


# 获取社区一段时间内的开发者角色字典，不含仅fork和star的用户
# repo_id:仓库id
# startDay:筛选时间段的起始日期（包含）
# endDay:筛选时间段的终止日期（不含）
# exceptList:排除的用户id
def getRepoUserRoleDict(repo_id,startDay,endDay,exceptList=None):
    if exceptList is None:
        exceptList = []
    userList = []
    userDict = dict()
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute(
        'select distinct user_id,author_association from repo_issue ' \
        'where repo_id = '+str(repo_id)+' and create_time between \"'+str(startDay)\
        +'\" and \"'+str(endDay)+'\"'
    )
    results = cursor.fetchall()
    for result in results:
        if result[0] not in userList and result[0] not in exceptList:
            userList.append(result[0])
            userDict[result[0]]=result[1]
        elif compareRole(result[1],userDict[result[0]]) > 0:
            userDict[result[0]]=result[1]

    cursor.execute(
        'select distinct user_id,author_association from repo_issue_comment ' \
        'where repo_id = ' + str(repo_id) + ' and create_time between \"' + str(startDay) \
        + '\" and \"' + str(endDay) + '\"'
    )
    results = cursor.fetchall()
    for result in results:
        if result[0] not in userList and result[0] not in exceptList:
            userList.append(result[0])
            userDict[result[0]] = result[1]
        elif compareRole(result[1], userDict[result[0]]) > 0:
            userDict[result[0]] = result[1]

    cursor.execute(
        'select distinct user_id,author_association from repo_pull ' \
        'where repo_id = ' + str(repo_id) + ' and create_time between \"' + str(startDay) \
        + '\" and \"' + str(endDay) + '\"'
    )
    for result in results:
        if result[0] not in userList and result[0] not in exceptList:
            userList.append(result[0])
            userDict[result[0]] = result[1]
        elif compareRole(result[1], userDict[result[0]]) > 0:
            userDict[result[0]] = result[1]

    cursor.execute(
        'select distinct user_id,author_association from repo_review ' \
        'where repo_id = ' + str(repo_id) + ' and submit_time between \"' + str(startDay) \
        + '\" and \"' + str(endDay) + '\"'
    )
    results = cursor.fetchall()
    for result in results:
        if result[0] not in userList and result[0] not in exceptList:
            userList.append(result[0])
            userDict[result[0]] = result[1]
        elif compareRole(result[1], userDict[result[0]]) > 0:
            userDict[result[0]] = result[1]

    cursor.execute(
        'select distinct user_id,author_association from repo_review_comment ' \
        'where repo_id = ' + str(repo_id) + ' and create_time between \"' + str(startDay) \
        + '\" and \"' + str(endDay) + '\"'
    )
    results = cursor.fetchall()
    for result in results:
        if result[0] not in userList and result[0] not in exceptList:
            userList.append(result[0])
            userDict[result[0]] = result[1]
        elif compareRole(result[1], userDict[result[0]]) > 0:
            userDict[result[0]] = result[1]

    cursor.execute(
        'select distinct user_id,author_association from repo_commit_comment ' \
        'where repo_id = ' + str(repo_id) + ' and comment_time between \"' + str(startDay) \
        + '\" and \"' + str(endDay) + '\"'
    )
    results = cursor.fetchall()
    for result in results:
        if result[0] not in userList and result[0] not in exceptList:
            userList.append(result[0])
            userDict[result[0]] = result[1]
        elif compareRole(result[1], userDict[result[0]]) > 0:
            userDict[result[0]] = result[1]

    cursor.execute(
        'select distinct user_id from repo_commit ' \
        'where repo_id = ' + str(repo_id) + ' and commit_time between \"' + str(startDay) \
        + '\" and \"' + str(endDay) + '\"'
    )
    results = cursor.fetchall()
    for result in results:
        if result[0] not in userList and result[0] not in exceptList:
            userList.append(result[0])
            userDict[result[0]] = 'NONE'

    return userList,userDict


# 滑动平均，曲线平滑处理
# 参考链接：https://blog.csdn.net/weixin_42782150/article/details/107176500
def moving_average(interval, windowsize):
    window = np.ones(int(windowsize)) / float(windowsize)
    ret = np.convolve(interval, window, 'same')
    return ret


# 绘制社区流失开发者在不同流失期限下的回访率曲线
# repo_id:仓库id
# startDay:筛选时间段的起始日期（包含）
# endDay:筛选时间段的终止日期（不含）
# max_weeks:横坐标流失期限的最大值
# figname: 保存的图片名，如果为空字符串则不保存
# data_filename: 保存的数据问件名，如果为空字符串则不保存
# exceptList:排除的用户id
# 返回值：dict类型，{user_id:未活动周数}
def drawReturnVisitRateCurve(repo_id, startDay, endDay, max_weeks=52, figname = '', data_filename = '', exceptList = None):
    user_inactive_weeks = dict() #用户连续未活动周数，动态变化
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
        for user_id in active_user_list:    # 将新的用户不断添加到user_inactive_weeks中
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
    kneeLocator = KneeLocator(weeks, rates, curve='convex', direction='decreasing', online=False)
    plt.axvline(x=kneeLocator.elbow,ymin=0.05,ymax=0.95, color='blue',linestyle='--',
                label ='elbow = '+str(kneeLocator.elbow))
    rate_10_week = len(weeks)
    for i in range(len(weeks)):
        if rates[i]<=10:
            rate_10_week = i+1
            break
    plt.axvline(x=rate_10_week, ymin=0.05, ymax=0.95, color='orangered', linestyle='--',
                label='10% rate = ' + str(rate_10_week))
    plt.legend(loc="upper right")
    plt.xlabel('流失期限（周）')
    plt.ylabel('用户回访率（%）')
    plt.title('社区（repo_id = ' + str(repo_id) + '）' + startDay + '~' + endDay + '期间用户回访率曲线')
    if figname!='':
        plt.savefig(figname)
    plt.show()
    if data_filename!='':
        with open(data_filename,'w',encoding='utf-8')as f:
            line = ''
            for rate in rates:
                line+=str(rate)+','
            f.write(line+'\n')
            f.write(str(kneeLocator.elbow)+','+str(kneeLocator.elbow_y)+',\n')
            f.write(str(rate_10_week)+','+str(rates[rate_10_week-1])+',\n')

    return user_inactive_weeks


# 为每个仓库的全部历史绘制用户回访率曲线并求肘部
# dir_name: 保存图像和曲线数据的文件夹的名称
def drawCurvesForAllRepos(dir_name):
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    order = 'select id,repo_name,repo_id,created_at from churn_search_repos_final'
    cursor.execute(order)
    results = cursor.fetchall()
    for result in results:
        figname = dir_name + '/return_visit_rate_curves/'+str(result[0])+'_'+result[1].replace('/','_')+'.png'
        data_filename = dir_name + '/return_visit_rate_data/' + str(result[0]) + '_' + result[1].replace('/', '_') + '.csv'
        startDay = result[3][0:10]
        endDay = '2022-01-01'
        repo_id = result[2]
        print()
        print(result[1]+':',startDay+' -- '+endDay)
        drawReturnVisitRateCurve(repo_id,startDay,endDay,figname=figname,data_filename=data_filename)


# 为30个仓库的所有划分时间段绘制回访率曲线
# filename:划分时间段的文件
# dir_name: 输出图像和数据文件的保存路径
def drawCurvesForAllRepoPeriods(filename,dir_name):
    id_periods = dict()
    with open(filename,'r',encoding='utf-8')as f:
        for line in f.readlines():
            items = line.strip(',\n').split(',')
            id = int(items[0])
            period_list = []
            for i in range(1,len(items)):
                period_list.append(items[i])
            id_periods[id] = period_list
    # print(id_periods)
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    order = 'select id,repo_name,repo_id,created_at from churn_search_repos_final'
    cursor.execute(order)
    results = cursor.fetchall()
    for result in results:
        repo_id = result[2]
        for i in range(len(id_periods[result[0]])):
            figname = dir_name + '/return_visit_rate_curves_period/' + str(result[0]) + '_' \
                      + result[1].replace('/','_') + '-'+str(i)+'.png'
            data_filename = dir_name + '/return_visit_rate_data_period/' + str(result[0]) + '_' \
                            + result[1].replace('/','_') + '-'+str(i)+ '.csv'
            periods = id_periods[result[0]][i].split('--')
            startDay = periods[0]
            endDay = periods[1]
            start_day=datetime.datetime.strptime(startDay,fmt_MySQL)
            end_day=datetime.datetime.strptime(endDay,fmt_MySQL)
            if (end_day-start_day).days < 180:
                continue
            print()
            print(result[1] + ':', startDay + ' -- ' + endDay)
            drawReturnVisitRateCurve(repo_id, startDay, endDay, figname=figname, data_filename=data_filename)


if __name__ == '__main__':
    startDay = '2009-05-05'
    endDay = '2016-09-25'
    repo_id = 192904
    # drawReturnVisitRateCurve(repo_id,startDay,endDay)
    drawCurvesForAllRepos('E:/bysj_project/return_visit_rate')
    drawCurvesForAllRepoPeriods('repo_periods_1.csv','E:/bysj_project/return_visit_rate_period')

    '''weeks = []
    for i in range(52):
        weeks.append(i+1)
    # rates = [
    #     50.85616438356164, 39.03318903318903, 31.76954732510288,
    #     25.952813067150636, 21.839080459770116, 18.655967903711133,
    #     16.5979381443299, 15.100316789862724, 13.390928725701944,
    #     12.472406181015453, 11.883408071748878, 11.211778029445073,
    #     10.0, 9.11214953271028, 8.500590318772137,
    #     7.77511961722488, 7.117008443908324, 7.03030303030303,
    #     6.471306471306471, 5.933250927070457, 5.700123915737299,
    #     5.472636815920398, 5.2434456928838955, 4.556962025316456,
    #     4.076433121019108, 3.9794608472400514, 3.6175710594315245,
    #     3.6363636363636362, 3.4076015727391873, 3.2851511169513796,
    #     3.3112582781456954, 3.095558546433378, 2.985074626865672,
    #     2.861035422343324, 2.73972602739726, 2.4827586206896552,
    #     2.5, 2.5174825174825175, 2.5280898876404496,
    #     2.397743300423131, 2.4113475177304964, 2.4355300859598854,
    #     2.4566473988439306, 2.463768115942029, 2.4853801169590644,
    #     2.4926686217008798, 2.5185185185185186, 2.5297619047619047,
    #     2.39880059970015, 2.4132730015082955, 2.4279210925644916,
    #     2.2865853658536586]
    rates = [53.945818610129564, 44.80234260614934, 38.44856661045531, 33.210332103321036, 29.8804780876494,
             27.044025157232703, 24.395604395604394, 23.30316742081448, 21.49532710280374, 19.559902200489,
             19.19191919191919, 18.06282722513089, 15.616438356164384, 15.363128491620111, 14.655172413793103,
             13.994169096209912, 12.835820895522389, 11.890243902439025, 11.764705882352942, 11.39240506329114,
             11.182108626198083, 10.784313725490197, 10.033444816053512, 10.204081632653061, 10.0, 9.89399293286219,
             9.489051094890511, 9.433962264150944, 8.494208494208495, 7.5396825396825395, 6.938775510204081,
             5.9071729957805905, 5.579399141630901, 5.676855895196507, 5.803571428571429, 5.909090909090909,
             5.990783410138249, 6.046511627906977, 6.103286384976526, 6.467661691542289, 6.770833333333333,
             6.989247311827957, 7.18232044198895, 6.857142857142857, 6.358381502890174, 6.508875739644971,
             6.134969325153374, 6.25, 5.732484076433121, 4.57516339869281, 4.72972972972973, 4.225352112676056]

    plt.plot(weeks, rates, label='用户回访率', linewidth=1, color='g', marker='.', markerfacecolor='w')
    kneeLocator = KneeLocator(weeks, rates, curve='convex', direction='decreasing', online=False)
    plt.axvline(x=kneeLocator.elbow,ymin=0.05,ymax=0.95, color='blue', linestyle='--',
                label='elbow = ' + str(kneeLocator.elbow))
    rate_10_week = len(weeks) - 1
    for i in range(len(weeks)):
        if rates[i] <= 10:
            rate_10_week = i+1
            break
    plt.axvline(x=rate_10_week, ymin=0.05, ymax=0.95, color='orangered', linestyle='--',
                label='10% rate = ' + str(rate_10_week))
    plt.legend(loc="upper right")
    plt.xlabel('流失期限（周）')
    plt.ylabel('用户回访率（%）')
    plt.title('社区（repo_id = ' + str(repo_id) + '）' + startDay + '~' + endDay + '期间用户回访率曲线')
    plt.show()'''
