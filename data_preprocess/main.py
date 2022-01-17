from influxdb import InfluxDBClient
import matplotlib
import matplotlib.pyplot as plt
import csv
from data_preprocess.request_header import *
import time
import re
import datetime
from data_preprocess.DeveloperCollaborationNetwork import *
import networkx as nx
from networkx.algorithms.centrality import betweenness_centrality

client = InfluxDBClient('localhost', 8086, 'moose', 'moose', 'moose_churn')


def main():
    oss_id = 8649239
    churn_period = 40  # 单位：周
    period = 570 # 单位：周
    max_week = 81
    low_activity_threshold = 1000
    offset_days = 0

    op_type = int(input('input the operation stage: '))

    if op_type==1:
        # stage1--获取churn_users、loyal_users和undecided_users,并保存三种用户的未活动周数（存在txt文件中）
        user_zero_count_0 = drawReturnVisitRateCurve(oss_id, period=period, max_limit=max_week, churn_period=churn_period)
        user_zero_count_50 = drawReturnVisitRateCurve(oss_id, period=period, max_limit=max_week, churn_period=churn_period,
                                                      low_threshold=low_activity_threshold, draw=False, offset_days=offset_days)
        churn_users = dict()
        undecided_users = dict()
        loyal_users = dict()
        # activity>1000且未活动周数小于6 或 未活动周数小于2的为忠诚用户
        for key in user_zero_count_50.keys():
            if user_zero_count_50[key] < 6:
                loyal_users.update({key: user_zero_count_50[key]})
        for key in user_zero_count_0.keys():
            if user_zero_count_0[key] < 2 and key not in loyal_users.keys():
                loyal_users.update({key: user_zero_count_0[key]})

        for key in user_zero_count_0.keys():
            if user_zero_count_0[key] >= churn_period:
                churn_users.update(({key: user_zero_count_0[key]}))
            elif key not in loyal_users.keys():
                undecided_users.update(({key: user_zero_count_0[key]}))
        print(len(churn_users), len(undecided_users), len(loyal_users))
        print(churn_users)
        print(undecided_users)
        print(loyal_users)
        with open("churn_users.txt", "w") as f:
            for key in churn_users.keys():
                f.write(str(key) + ',' + str(churn_users[key]) + '\n')
        with open("loyal_users.txt", "w") as f:
            for key in loyal_users.keys():
                f.write(str(key) + ',' + str(loyal_users[key]) + '\n')
        with open("undecided_users.txt", "w") as f:
            for key in undecided_users.keys():
                f.write(str(key) + ',' + str(undecided_users[key]) + '\n')
        return

    # 读取user_weeks数据，是后续操作必须的前置操作
    churn_user_weeks = dict()
    #churn_user_weeks_revised = dict()
    loyal_user_weeks = dict()
    try:
        with open("churn_users.txt", "r") as f:
            for line in f.readlines():
                line = line.strip('\n')  # 去掉列表中每一个元素的换行符
                churn_user_weeks.update({int(line.split(',')[0]): int(line.split(',')[1])})
                # churn_user_weeks_revised.update({int(line.split(',')[0]):int(line.split(',')[1])%churn_period})
        with open("loyal_users.txt", "r") as f:
            for line in f.readlines():
                line = line.strip('\n')
                loyal_user_weeks.update({int(line.split(',')[0]): int(line.split(',')[1])})
    except Exception as ex:
        print('please do stage 1 first!')
        return

    if op_type == 2:
        # stage2--获取流失用户和忠诚用户各种（12月）数据并保存
        print(0)
        getDataAndSave(churn_user_weeks, "churn_issues.csv", "moose_issue", oss_id, churn_period)
        print(1)
        getDataAndSave(churn_user_weeks, "churn_issue_comments.csv", "moose_issue_comment", oss_id, churn_period)
        print(2)
        getDataAndSave(churn_user_weeks, "churn_pulls.csv", "moose_pull", oss_id, churn_period)
        print(3)
        getDataAndSave(churn_user_weeks, "churn_reviews.csv", "moose_review", oss_id, churn_period)
        print(4)
        getDataAndSave(churn_user_weeks, "churn_review_comments.csv", "moose_review_comment", oss_id, churn_period)
        print(5)
        getDataAndSave(churn_user_weeks, "churn_merged_pulls.csv", "moose_pull", oss_id, churn_period,
                       add_order=' and merged_time != \'\'')
        print(6)
        getDataAndSave(churn_user_weeks, "churn_commits.csv", "moose_commit", oss_id, churn_period)
        print(7)
        getDataAndSave(churn_user_weeks, "churn_commit_comments.csv", "moose_comment", oss_id, churn_period)
        print(8)
        getDataAndSave(churn_user_weeks, "churn_stars.csv", "moose_star", oss_id, churn_period)
        print(9)
        getDataAndSave(churn_user_weeks, "churn_forks.csv", "moose_fork", oss_id, churn_period)
        print(10)

        getDataAndSave(loyal_user_weeks, "loyal_issues.csv", "moose_issue", oss_id, churn_period)
        print(11)
        getDataAndSave(loyal_user_weeks, "loyal_issue_comments.csv", "moose_issue_comment", oss_id, churn_period)
        print(12)
        getDataAndSave(loyal_user_weeks, "loyal_pulls.csv", "moose_pull", oss_id, churn_period)
        print(13)
        getDataAndSave(loyal_user_weeks, "loyal_reviews.csv", "moose_review", oss_id, churn_period)
        print(14)
        getDataAndSave(loyal_user_weeks, "loyal_review_comments.csv", "moose_review_comment", oss_id, churn_period)
        print(15)
        getDataAndSave(loyal_user_weeks, "loyal_merged_pulls.csv", "moose_pull", oss_id, churn_period,
                       add_order=' and merged_time != \'\'')
        print(16)
        getDataAndSave(loyal_user_weeks, "loyal_commits.csv", "moose_commit", oss_id, churn_period)
        print(17)
        getDataAndSave(loyal_user_weeks, "loyal_commit_comments.csv", "moose_comment", oss_id, churn_period)
        print(18)
        getDataAndSave(loyal_user_weeks, "loyal_stars.csv", "moose_star", oss_id, churn_period)
        print(19)
        getDataAndSave(loyal_user_weeks, "loyal_forks.csv", "moose_fork", oss_id, churn_period)
        print(20)
        return


    if op_type == 3:
        # stage3--获取用户的个人信息并保存
        getUserInfoAndSave(churn_user_weeks, getRepoUserNames(oss_id, period), "churn_user_info.csv", isGitee=True)
        getUserInfoAndSave(loyal_user_weeks, getRepoUserNames(oss_id, period), "loyal_user_info.csv", isGitee=True)
        # return

    '''
    # # 测试DCN的生成
    # DCN,DCN0,index_user,user_index = getDeveloperCollaborationNetwork(client,oss_id,31,2)
    # user_degree = getDCNWeightedDegrees(user_index, DCN0)
    # user_weighted_degree = getDCNWeightedDegrees(user_index, DCN)
    # for list in DCN:
    #     for item in list:
    #         print(item,end='\t')
    #     print('')
    # print(user_degree)
    # print(user_weighted_degree)

    # # 测试getBetweeness和betweenness_centrality
    # network=[[0,0,0,1,0,0,0,0,0],
    #          [0,0,1,1,0,0,0,0,0],
    #          [0,1,0,1,0,1,0,0,0],
    #          [1,1,1,0,1,0,0,0,0],
    #          [0,0,0,1,0,1,1,0,0],
    #          [0,0,1,0,1,0,1,0,0],
    #          [0,0,0,0,1,1,0,1,1],
    #          [0,0,0,0,0,0,1,0,0],
    #          [0,0,0,0,0,0,1,0,0]]
    # N = nx.Graph()
    # N.add_nodes_from(range(0,9))
    # N.add_edges_from([(0,3),(1,2),(1,3),(2,3),(2,5),(3,4),(4,5),(4,6),(5,6),(6,7),(6,8)])
    # print(getBetweeness(network))
    # print(betweenness_centrality(N))

    # G = nx.Graph()
    # G.add_nodes_from(user_index.keys())
    # for i in range(len(DCN)):
    #     for j in range(i + 1, len(DCN)):
    #         if DCN[i][j]>0:
    #             G.add_edge(index_user[i], index_user[j])
    # 
    # # print(getBetweeness(DCN))
    # print(betweenness_centrality(G))'''

    if op_type == 3:#4
        # stage4--获取DCN有关的数据
        print('0%')
        # getDCNDegreeAndSave(loyal_user_weeks, "loyal_dcn_degrees.csv", oss_id, churn_period, 2)
        # print('12.5%')
        # getDCNWeightedDegreeAndSave(loyal_user_weeks, "loyal_dcn_weighted_degree.csv", oss_id, churn_period, 2)
        print('25%')
        getDCNDegreeAndSave(churn_user_weeks, "churn_dcn_degrees.csv", oss_id, churn_period, 1)
        print('37.5%')
        getDCNWeightedDegreeAndSave(churn_user_weeks, "churn_dcn_weighted_degree.csv", oss_id, churn_period, 1)
        print('50%')
        getDCNBetweenessAndSave(loyal_user_weeks, "loyal_dcn_betweeness_normalized.csv", oss_id, churn_period, 1, True)
        print('62.5%')
        getDCNBetweenessAndSave(loyal_user_weeks, "loyal_dcn_betweeness.csv", oss_id, churn_period, 1, False)
        print('75%')
        getDCNBetweenessAndSave(churn_user_weeks, "churn_dcn_betweeness_normalized.csv", oss_id, churn_period, 1, True)
        print('87.5%')
        getDCNBetweenessAndSave(churn_user_weeks, "churn_dcn_betweeness.csv", oss_id, churn_period, 1, False)
        print('100%')
        return


# 功能：获取DCN的度数并保存在filename文件中，offset_days为日期偏移量，表示数据库有效数据在offset_days前
# user_weeks：用户和未活动周数的对应dict
# filename：保存的文件名
# oss_id：社区id
# churn_period：流失期限
# offset_days：日期偏移量，表示数据库在offset_days天前的数据是有效的
def getDCNDegreeAndSave(user_weeks,filename,oss_id,churn_period,offset_days=0):
    with open(filename,"w",newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(["user_id","1","2","3","4","5","6","7","8","9","10","11","12"])
        for key in user_weeks.keys():
            # startDay = (int(user_weeks[key]) - int(user_weeks[key]) % churn_period) * 7 + 120 + offset_days###############
            startDay = int(user_weeks[key]) * 7 + 120 + offset_days
            endDay = startDay - 10
            line = []
            line.append(key)
            print('degree:',key)
            for i in range(12):
                print(startDay,endDay)
                DCN, DCN0, index_user, user_index = getDeveloperCollaborationNetwork(client, oss_id, startDay, endDay)
                user_degree = getDCNWeightedDegrees(user_index, DCN0)
                if key in user_degree.keys():
                    degree = user_degree[key]
                else:
                    degree = 0
                line.append(degree)
                startDay = endDay
                endDay -= 10
            writer.writerow(line)


# 功能：获取DCN的节点加权度并保存在filename文件中，offset_days为日期偏移量，表示数据库有效数据在offset_days前
# user_weeks：用户和未活动周数的对应dict
# filename：保存的文件名
# oss_id：社区id
# churn_period：流失期限
# offset_days：日期偏移量，表示数据库在offset_days天前的数据是有效的
def getDCNWeightedDegreeAndSave(user_weeks,filename,oss_id,churn_period,offset_days=0):
    with open(filename,"w",newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(["user_id","1","2","3","4","5","6","7","8","9","10","11","12"])
        for key in user_weeks.keys():
            # startDay = (int(user_weeks[key]) - int(user_weeks[key]) % churn_period) * 7 + 120 + offset_days
            startDay = int(user_weeks[key]) * 7 + 120 + offset_days
            endDay = startDay - 10
            line = []
            line.append(key)
            print('weighted degree:',key)
            for i in range(12):
                print(startDay,endDay)
                DCN, DCN0, index_user, user_index = getDeveloperCollaborationNetwork(client, oss_id, startDay, endDay)
                user_weighted_degree = getDCNWeightedDegrees(user_index, DCN)
                if key in user_weighted_degree.keys():
                    weighted_degree = user_weighted_degree[key]
                else:
                    weighted_degree = 0
                line.append(weighted_degree)
                startDay = endDay
                endDay -= 10
            writer.writerow(line)


# 获取DCN的介数中心性，offset_days为日期偏移量，表示数据库有效数据在offset_days前
def getDCNBetweenessAndSave(user_weeks,filename,oss_id,churn_period,offset_days=0,normalized=True):
    with open(filename,"w",newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(["user_id","1","2","3","4","5","6","7","8","9","10","11","12"])
        for key in user_weeks.keys():
            # startDay = (int(user_weeks[key]) - int(user_weeks[key]) % churn_period) * 7 + 120 + offset_days
            startDay = int(user_weeks[key]) * 7 + 120 + offset_days
            endDay = startDay - 10
            line = []
            line.append(key)
            print('betweeness:',key)
            for i in range(12):
                print(startDay,endDay)
                DCN, DCN0, index_user, user_index = getDeveloperCollaborationNetwork(client, oss_id, startDay, endDay)
                G = nx.Graph()
                G.add_nodes_from(user_index.keys())
                for i in range(len(DCN)):
                    for j in range(i + 1, len(DCN)):
                        if DCN[i][j]>0:
                            G.add_edge(index_user[i], index_user[j])
                user_betweeness = betweenness_centrality(G, normalized=normalized)
                if key in user_betweeness.keys():
                    betweeness = user_betweeness[key]
                else:
                    betweeness = 0
                line.append(betweeness)
                startDay = endDay
                endDay -= 10
            writer.writerow(line)


# 功能：获取各种数据（12个月）并保存
# user_weeks：用户id和未活动周数对应dict
# filename：保存的文件名
# measurement：查询的表格
# oss_id：社区id
# churn_period：流失期限
# offset_days：日期偏移量，数据库中有效数据在offset_days天前
# add_order：查询时增加的查询条件
def getDataAndSave(user_weeks,filename,measurement,oss_id,churn_period,offset_days = 0, add_order=''):
    with open(filename,"w",newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(["user_id","1","2","3","4","5","6","7","8","9","10","11","12"])
        for key in user_weeks.keys():
            # startDay = (int(user_weeks[key])-int(user_weeks[key])%churn_period)*7+120 + offset_days
            startDay = int(user_weeks[key]) * 7 + 120 + offset_days
            endDay = startDay-10
            line = []
            line.append(key)
            print(key)########
            for i in range(12):
                print(startDay,endDay)
                results = client.query('select count(*) from '+measurement+
                                       ' where time > now() - ' + str(startDay) + 'd and time <= now() - ' + str(endDay) + \
                                       'd and user_id = ' + str(key) + ' and oss_id = \'' + str(oss_id) + '\'' + add_order).get_points()
                count = 0
                for result in results:
                    count = result['count_user_id']
                line.append(count)
                startDay = endDay
                endDay -=10
            writer.writerow(line)


# 功能：获得仓库相关的所有用户的id和login的对应关系
# oss_id：社区id
# period：统计用户的起始时间
# 时间区间：[-period,0]
# 返回值：dict类型数据id_name {user_id:user_name}
def getRepoUserNames(oss_id,period):
    id_name = dict()
    results = client.query('select user_id,user_name from moose_issue_comment '
                           'where time > now() - ' + str(period) +
                           'd and oss_id = \'' + str(oss_id) + '\'').get_points()
    for result in results:
        if result['user_id'] not in id_name.keys():
            id_name.update({result['user_id']:result['user_name']})
    results = client.query('select user_id,user_name from moose_issue '
                           'where time > now() - ' + str(period) +
                           'd and oss_id = \'' + str(oss_id) + '\'').get_points()
    for result in results:
        if result['user_id'] not in id_name.keys():
            id_name.update({result['user_id']: result['user_name']})
    results = client.query('select user_id,user_name from moose_pull '
                           'where time > now() - ' + str(period) +
                           'd and oss_id = \'' + str(oss_id) + '\'').get_points()
    for result in results:
        if result['user_id'] not in id_name.keys():
            id_name.update({result['user_id']: result['user_name']})
    results = client.query('select user_id,user_name from moose_review_comment '
                           'where time > now() - ' + str(period) +
                           'd and oss_id = \'' + str(oss_id) + '\'').get_points()
    for result in results:
        if result['user_id'] not in id_name.keys():
            id_name.update({result['user_id']: result['user_name']})
    results = client.query('select user_id,user_name from moose_review '
                           'where time > now() - ' + str(period) +
                           'd and oss_id = \'' + str(oss_id) + '\'').get_points()
    for result in results:
        if result['user_id'] not in id_name.keys():
            id_name.update({result['user_id']: result['user_name']})
    results = client.query('select user_id,user_name from moose_commit '
                           'where time > now() - ' + str(period) +
                           'd and oss_id = \'' + str(oss_id) + '\'').get_points()
    for result in results:
        if result['user_id'] not in id_name.keys():
            id_name.update({result['user_id']: result['user_name']})
    results = client.query('select user_id,user_name from moose_comment '
                           'where time > now() - ' + str(period) +
                           'd and oss_id = \'' + str(oss_id) + '\'').get_points()
    for result in results:
        if result['user_id'] not in id_name.keys():
            id_name.update({result['user_id']: result['user_name']})
    return id_name


# 功能：获取用户的信息并保存,包括用户的follower数，following数，公开仓库数，账号寿命，被star数，被fork数和被watch数
# user_weeks：dict()类型，key为所有需要求详细信息的用户
# id_names：用户id和name的对应dict
# filename：保存的文件名
# isGitee：是否是gitee的仓库
def getUserInfoAndSave(user_weeks,id_names,filename,isGitee):
    with open(filename,"w",newline="") as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(["user_id","follower_count","following_count","repo_count","lifespan","starred","forked","watched"])
        for user_id in user_weeks.keys():
            if isGitee==True:
                userInfo = get_html_json('https://gitee.com/api/v5/users/'+str(id_names[user_id]),getGiteeHeader())[0]
            else:
                userInfo = get_html_json('https://api.github.com/users/'+str(id_names[user_id]),getHeader())[0]
            try:
                followers = int(userInfo['followers'])
                following = int(userInfo['following'])
                pub_repo = int(userInfo['public_repos'])
                create_time = datetime.datetime.strptime(userInfo['created_at'][0:10],'%Y-%m-%d')
            except BaseException as e:
                print(100,str(id_names[user_id]),'isGitee =',isGitee)
                followers = 0
                following = 0
                pub_repo = 0
                create_time = datetime.datetime.strptime(time.strftime('%Y-%m-%d', time.localtime(time.time())),'%Y-%m-%d')
            local_time = datetime.datetime.strptime(time.strftime('%Y-%m-%d', time.localtime(time.time())),'%Y-%m-%d')
            delta = local_time-create_time
            lifespan = int(delta.days)
            stars,forks,watches = getStarForkCount(id_names[user_id],isGitee)
            writer.writerow([user_id,followers,following,pub_repo,lifespan,stars,forks,watches])
            print(user_id,id_names[user_id],'\n')


# 功能：获取用户的所有仓库的累计star fork watch数量
# user_login：用户名login
# isGitee：是否是gitee的仓库
# 返回值：三个整数stars,forks,watches
def getStarForkCount(user_login,isGitee):
    if isGitee == True:
        user_repo= get_html_json('https://gitee.com/api/v5/users/'+str(user_login)+'/repos?per_page=100',getGiteeHeader())
    else:
        user_repo = get_html_json('https://api.github.com/users/'+str(user_login)+'/repos?per_page=100',getHeader())
    user_repo_info = user_repo[0]
    response_header = user_repo[1]
    page = 1
    print(user_login,'page:',page)
    stars = 0
    forks = 0
    watches = 0
    for repo in user_repo_info:
        try:
            star = int(repo['stargazers_count'])
            fork = int(repo['forks_count'])
            watch = int(repo['watchers_count'])
        except BaseException as e:
            print(101)
            star = 0
            fork = 0
            watch = 0
        stars +=star
        forks += fork
        watches += watch
    while True:
        if isGitee == True:
            listLink_next_url = re.findall(r'(?<=<).[^<]*(?=>; rel=\'next)', str(response_header))
            if len(listLink_next_url)>0 and listLink_next_url[0].find('created_at') != -1:
                listLink_next_url[0] = listLink_next_url[0].replace('created_at', 'created')
        else:
            listLink_next_url = re.findall(r'(?<=<).[^<]*(?=>; rel=\"next)', str(response_header))
        if len(listLink_next_url)==0 :
            break
        if isGitee == True:
            user_repo = get_html_json(listLink_next_url[0],getGiteeHeader())
        else:
            user_repo = get_html_json(listLink_next_url[0],getHeader())
        if user_repo == None or len(user_repo)==0 or len(user_repo[0])==0:
            break
        user_repo_info = user_repo[0]
        response_header = user_repo[1]
        page+=1
        print(user_login,'page:',page)
        for repo in user_repo_info:
            try:
                star = int(repo['stargazers_count'])
                fork = int(repo['forks_count'])
                watch = int(repo['watchers_count'])
            except BaseException as e:
                print(101)
                star = 0
                fork = 0
                watch = 0
            stars += star
            forks += fork
            watches += watch
    print(user_login,stars,forks,watches)
    return stars,forks,watches


# 功能：画oss_id社区一段时间内，在不同流失期限（单位：周；最大为max_limit周）下的用户回访率曲线和流失用户未活动周数分布直方图
#      返回各个用户和对应的未活动周数
#      增加了排除该时间段内总活跃度低于某一阈值的用户的功能
# oss_id：社区id
# max_limit：最大流失期限（单位：周），绘制的用户回访率曲线横坐标的最大值（最小值为1）
# churn_period：流失期限，用于绘制流失用户未活动周数分布直方图
# period：时间跨度，获取数据对应的时间区间长度
# low_threshold：活跃度阈值，改时间段内总活跃度低于该阈值的用户不会被统计，默认为0
# draw：是否绘制回访率曲线和流失用户未活动周数分布直方图，默认为true
# offset_days：有效数据偏移量，表明数据库有效数据的最后时间距离当前时间的偏差,默认为0
# 获取数据的时间区间为[-startDay,-endDay]，startDay=period+offset_days，endDay=offset_days
# 返回值：dict类型，{user_id:未活动周数}
def drawReturnVisitRateCurve(oss_id,period,max_limit,churn_period,low_threshold=0,draw=True,offset_days=0):
    user_zero_count = dict() #用户连续未活动周数
    m = int(period/7)
    churn_counts = []
    return_counts = []
    for i in range(max_limit+1):
        churn_counts.append(0)
        return_counts.append(0)
    except_list = getLowActivityDevelopers(oss_id,period,low_threshold,offset_days)##########画回访率曲线时排除活跃度低于low_threshold的用户
    for i in range(m, 0,-1):
        active_user_list = getDeveloperVisitList(i*7+offset_days,(i-1)*7+offset_days,oss_id,except_list)#获取用户列表
        for user_id in user_zero_count.keys():
            if user_zero_count[user_id]>0 and user_id in active_user_list:#上周未活动但本周有活动
                for j in range(1,user_zero_count[user_id]+1):
                    if j>max_limit:#############
                        print("j>max_limit:",j)
                        break
                    return_counts[j]+=1 #流失期限为j周时,属于流失回归，相应期限的回归数加1
                user_zero_count[user_id] = 0 #回归后和初次进入该社区一样，将user_zero_count置零
            elif user_id not in active_user_list:#社区该用户本周没有活动
                if user_zero_count[user_id]<max_limit:##########
                    user_zero_count[user_id]+=1
                    churn_counts[user_zero_count[user_id]]+=1 #注意流失数的增加和回归数的增加情形不完全相同
        for user_id in active_user_list:
            if user_id not in user_zero_count.keys():
                user_zero_count.update({user_id:0}) #新加入社区的用户
        print(-i*7)
    if draw == True:
        weeks = []
        rates = []
        for i in range (1,max_limit+1):
            weeks.append(i)
            if churn_counts[i]==0:
                rates.append(0.0)
            else:
                rates.append(100.0*float(return_counts[i])/churn_counts[i])
        # print(rates)
        matplotlib.rcParams['font.sans-serif'] = ['KaiTi']
        matplotlib.rcParams['axes.unicode_minus'] = False
        plt.plot(weeks, rates, label='用户回访率', linewidth=1, color='g',marker = '.',markerfacecolor='w')
        plt.legend(loc="upper right")
        plt.xlabel('流失期限（周）')
        plt.ylabel('用户回访率（%）')
        plt.title('社区（oss_id = ' + str(oss_id) + '）'+str(period)+'天累计活跃度高于'+str(low_threshold)+'的用户回访率曲线')
        plt.show()

        # 绘制社区流失用户未活动周数分布
        histogram_x = []
        for key in user_zero_count.keys():
            if user_zero_count[key] >= churn_period:  #########流失期限 45
                histogram_x.append(user_zero_count[key])
        plt.hist(x=histogram_x, bins=20, color='steelblue', edgecolor='black')
        plt.xlabel('未活动周数')
        plt.ylabel('频数')
        plt.title('社区流失用户未活动时间分布(oss_id = ' + str(oss_id) + ')')
        plt.show()

    return user_zero_count


# 功能：获取某一段时期内一个社区有特定行为的用户列表，排除star和fork的，包含issue、issue_comment、pull、review、review_comment、commit、cmmit_comment
# oss_id：社区id
# startDay：获取数据时间区间的起始日期为startDay前
# endDay：获取数据时间区间的终止日期为endDay前
# 时间区间为[-startDay,-endDay]
# except_list：排除的用户列表，在该列表中的用户不会被包含在返回的用户列表中
# 返回值：list类型
def getDeveloperVisitList(startDay, endDay, oss_id, except_list = None):
    if except_list is None:
        except_list = []
    ret_list = []
    results = client.query('select distinct user_id from moose_issue_comment '
                           'where time > now() - ' + str(startDay) + 'd and time <= now() - ' + str(endDay) + \
                           'd and oss_id = \'' + str(oss_id) + '\'').get_points()
    for result in results:
        if result['distinct'] not in ret_list:
            ret_list.append(result['distinct'])
    results = client.query('select distinct user_id from moose_issue '
                           'where time > now() - ' + str(startDay) + 'd and time <= now() - ' + str(endDay) + \
                           'd and oss_id = \'' + str(oss_id) + '\'').get_points()
    for result in results:
        if result['distinct'] not in ret_list:
            ret_list.append(result['distinct'])
    results = client.query('select distinct user_id from moose_pull '
                           'where time > now() - ' + str(startDay) + 'd and time <= now() - ' + str(endDay) + \
                           'd and oss_id = \'' + str(oss_id) + '\'').get_points()
    for result in results:
        if result['distinct'] not in ret_list:
            ret_list.append(result['distinct'])
    results = client.query('select distinct user_id from moose_review_comment '
                           'where time > now() - ' + str(startDay) + 'd and time <= now() - ' + str(endDay) + \
                           'd and oss_id = \'' + str(oss_id) + '\'').get_points()
    for result in results:
        if result['distinct'] not in ret_list:
            ret_list.append(result['distinct'])
    results = client.query('select distinct user_id from moose_review '
                           'where time > now() - ' + str(startDay) + 'd and time <= now() - ' + str(endDay) + \
                           'd and oss_id = \'' + str(oss_id) + '\'').get_points()
    for result in results:
        if result['distinct'] not in ret_list:
            ret_list.append(result['distinct'])
    results = client.query('select distinct user_id from moose_commit '
                           'where time > now() - ' + str(startDay) + 'd and time <= now() - ' + str(endDay) + \
                           'd and oss_id = \'' + str(oss_id) + '\'').get_points()
    for result in results:
        if result['distinct'] not in ret_list:
            ret_list.append(result['distinct'])
    results = client.query('select distinct user_id from moose_comment '
                           'where time > now() - ' + str(startDay) + 'd and time <= now() - ' + str(endDay) + \
                           'd and oss_id = \'' + str(oss_id) + '\'').get_points()
    for result in results:
        if result['distinct'] not in ret_list:
            ret_list.append(result['distinct'])
    #return ret_list
    ret_list_2=[]
    for ret in ret_list:
        if ret not in except_list:
            ret_list_2.append(ret)
    return ret_list_2


# 功能：获取社区某一时间段内活跃度低于threshold的用户的id列表
# oss_id：社区id
# threshold：阈值
# period：时间跨度，获取数据对应的时间区间长度
# offset_days：有效数据偏移量，表明数据库有效数据的最后时间距离当前时间的偏差,默认为0
# 获取数据的时间区间为[-startDay,-endDay]，startDay=period+offset_days，endDay=offset_days
# 返回值：list类型数据low_activity_users
def getLowActivityDevelopers(oss_id,period,threshold,offset_days=0):
    issueCommentCounts = getIssueCommentCount('1', oss_id, period,offset_days)
    openIssueCounts = getOpenIssueCount('1', oss_id, period,offset_days)
    openPullCounts = getOpenPullCount('1', oss_id, period,offset_days)
    reviewCommentCounts = getReviewCommentCount('1', oss_id, period,offset_days)
    pullMergedCounts = getPullMergedCount('1', oss_id, period,offset_days)  # 有待改进
    starCounts = getStarCount('1', oss_id, period,offset_days)
    forkCounts = getForkCount('1', oss_id, period,offset_days)
    id_list = []  # 收集与该oss相关的所有用户
    for key in issueCommentCounts.keys():
        if key not in id_list:
            id_list.append(key)
    for key in openIssueCounts.keys():
        if key not in id_list:
            id_list.append(key)
    for key in openPullCounts.keys():
        if key not in id_list:
            id_list.append(key)
    for key in reviewCommentCounts.keys():
        if key not in id_list:
            id_list.append(key)
    for key in pullMergedCounts.keys():
        if key not in id_list:
            id_list.append(key)
    for key in starCounts.keys():
        if key not in id_list:
            id_list.append(key)
    for key in forkCounts.keys():
        if key not in id_list:
            id_list.append(key)
    low_activity_users = []
    for id in id_list:
        if id in issueCommentCounts.keys():
            issueCommentCount = issueCommentCounts[id]
        else:
            issueCommentCount = 0
        if id in openIssueCounts.keys():
            openIssueCount = openIssueCounts[id]
        else:
            openIssueCount = 0
        if id in openPullCounts:
            openPullCount = openPullCounts[id]
        else:
            openPullCount = 0
        if id in reviewCommentCounts.keys():
            reviewCommentCount = reviewCommentCounts[id]
        else:
            reviewCommentCount = 0
        if id in pullMergedCounts.keys():
            pullMergedCount = pullMergedCounts[id]
        else:
            pullMergedCount = 0
        if id in starCounts.keys():
            starCount = starCounts[id]
        else:
            starCount = 0
        if id in forkCounts.keys():
            forkCount = forkCounts[id]
        else:
            forkCount = 0
        activity = issueCommentCount + 2 * openIssueCount + 3 * openPullCount + 4 * reviewCommentCount + 2 * pullMergedCount + starCount + 2 * forkCount  ##########
        if activity < threshold:
            low_activity_users.append(id)
    return low_activity_users


# 功能：获取一定时间段内某一用户或某一社区提交的issue comment数
# type：0--获取某一用户的数据；1--获取某一社区的数据；2--获取某一用户在某一社区的数据
# id：与type对应，0/2--user_id；1--oss_id
# period：时间跨度，获取数据对应的时间区间长度
# offset_days：有效数据偏移量，表明数据库有效数据的最后时间距离当前时间的偏差,默认为0
# 获取数据的时间区间为[-startDay,-endDay]，startDay=period+offset_days，endDay=offset_days
# 返回值：dict类型数据counts，{id:issue_comment_count}
def getIssueCommentCount(type,id,period,offset_days=0):
    if type == '0' or type == '2':
        order = 'select * from moose_issue_comment where time > now() - ' + str(period+offset_days) + 'd' \
                ' and time <= now() - '+str(offset_days)+'d and user_id = ' + str(id)
        results = client.query(order).get_points()
        counts = dict()
        for result in results:
            if result['oss_id'] in counts.keys():
                counts[result['oss_id']]+=1
            else:
                counts.update({result['oss_id']:1})
        # print(order)
        # for key in counts.keys():
        #     print('oss_id = ',key,', issue comment count = ',counts[key])
    else:
        order = 'select * from moose_issue_comment where time > now() - ' + str(period+offset_days) + 'd' \
                ' and time <= now() - '+str(offset_days)+'d and oss_id = \'' + str(id)+'\''
        results = client.query(order).get_points()
        counts = dict()
        for result in results:
            if result['user_id'] in counts.keys():
                counts[result['user_id']] += 1
            else:
                counts.update({result['user_id']: 1})
        # print(order)
        # for key in counts.keys():
        #     print('user_id = ', key, ', issue comment count = ', counts[key])
    return counts


# 功能：获取一定时间段内某一用户或某一社区的issue数
# type：0--获取某一用户的数据；1--获取某一社区的数据；2--获取某一用户在某一社区的数据
# id：与type对应，0/2--user_id；1--oss_id
# period：时间跨度，获取数据对应的时间区间长度
# offset_days：有效数据偏移量，表明数据库有效数据的最后时间距离当前时间的偏差,默认为0
# 获取数据的时间区间为[-startDay,-endDay]，startDay=period+offset_days，endDay=offset_days
# 返回值：dict类型数据counts，{id:issue_count}
def getOpenIssueCount(type,id,period,offset_days=0):
    if type == '0' or type == '2':
        order = 'select * from moose_issue where time > now() - ' + str(period+offset_days) + 'd' \
                ' and time <= now() - '+str(offset_days)+'d and user_id = ' + str(id)
        results = client.query(order).get_points()
        counts = dict()
        for result in results:
            if result['oss_id'] in counts.keys():
                counts[result['oss_id']]+=1
            else:
                counts.update({result['oss_id']:1})
        # print(order)
        # for key in counts.keys():
        #     print('oss_id = ',key,', open issue count = ',counts[key])
    else:
        order = 'select * from moose_issue where time > now() - ' + str(period+offset_days) + 'd' \
                ' and time <= now() - '+str(offset_days)+'d and oss_id = \'' + str(id)+'\''
        results = client.query(order).get_points()
        counts = dict()
        for result in results:
            if result['user_id'] in counts.keys():
                counts[result['user_id']] += 1
            else:
                counts.update({result['user_id']: 1})
        # print(order)
        # for key in counts.keys():
        #     print('user_id = ', key, ', open issue count = ', counts[key])
    return counts


# 功能：获取一定时间段内某一用户或某一社区的pr数
# type：0--获取某一用户的数据；1--获取某一社区的数据；2--获取某一用户在某一社区的数据
# id：与type对应，0/2--user_id；1--oss_id
# period：时间跨度，获取数据对应的时间区间长度
# offset_days：有效数据偏移量，表明数据库有效数据的最后时间距离当前时间的偏差,默认为0
# 获取数据的时间区间为[-startDay,-endDay]，startDay=period+offset_days，endDay=offset_days
# 返回值：dict类型数据counts，{id:pull_count}
def getOpenPullCount(type,id,period,offset_days=0):
    if type == '0' or type == '2':
        order = 'select * from moose_pull where time > now() - ' + str(period+offset_days) + 'd' \
                ' and time <= now() - '+str(offset_days)+'d and user_id = ' + str(id)
        results = client.query(order).get_points()
        counts = dict()
        for result in results:
            if result['oss_id'] in counts.keys():
                counts[result['oss_id']]+=1
            else:
                counts.update({result['oss_id']:1})
        # print(order)
        # for key in counts.keys():
        #     print('oss_id = ',key,', open pull request count = ',counts[key])
    else:
        order = 'select * from moose_pull where time > now() - ' + str(period+offset_days) + 'd' \
                ' and time <= now() - '+str(offset_days)+'d and oss_id = \'' + str(id)+'\''
        results = client.query(order).get_points()
        counts = dict()
        for result in results:
            if result['user_id'] in counts.keys():
                counts[result['user_id']] += 1
            else:
                counts.update({result['user_id']: 1})
        # print(order)
        # for key in counts.keys():
        #     print('user_id = ', key, ', open pull request count = ', counts[key])
    return counts


# 功能：获取一定时间段内某一用户或某一社区的review comment数
# type：0--获取某一用户的数据；1--获取某一社区的数据；2--获取某一用户在某一社区的数据
# id：与type对应，0/2--user_id；1--oss_id
# period：时间跨度，获取数据对应的时间区间长度
# offset_days：有效数据偏移量，表明数据库有效数据的最后时间距离当前时间的偏差,默认为0
# 获取数据的时间区间为[-startDay,-endDay]，startDay=period+offset_days，endDay=offset_days
# 返回值：dict类型数据counts，{id:review_comment_count}
def getReviewCommentCount(type,id,period,offset_days=0):
    if type == '0' or type == '2':
        order = 'select * from moose_review_comment where time > now() - ' + str(period+offset_days) + 'd' \
                ' and time <= now() - '+str(offset_days)+'d and user_id = ' + str(id)
        results = client.query(order).get_points()
        counts = dict()
        for result in results:
            if result['oss_id'] in counts.keys():
                counts[result['oss_id']]+=1
            else:
                counts.update({result['oss_id']:1})
        # print(order)
        # for key in counts.keys():
        #     print('oss_id = ',key,', pull request review comment count = ',counts[key])
    else:
        order = 'select * from moose_review_comment where time > now() - ' + str(period+offset_days) + 'd' \
                ' and time <= now() - '+str(offset_days)+'d and oss_id = \'' + str(id)+'\''
        results = client.query(order).get_points()
        counts = dict()
        for result in results:
            if result['user_id'] in counts.keys():
                counts[result['user_id']] += 1
            else:
                counts.update({result['user_id']: 1})
        # print(order)
        # for key in counts.keys():
        #     print('user_id = ', key, ', pull request review comment count = ', counts[key])
    return counts


# 功能：获取一定时间段内某一用户或某一社区合并的pr数
# type：0--获取某一用户的数据；1--获取某一社区的数据；2--获取某一用户在某一社区的数据
# id：与type对应，0/2--user_id；1--oss_id
# period：时间跨度，获取数据对应的时间区间长度
# offset_days：有效数据偏移量，表明数据库有效数据的最后时间距离当前时间的偏差,默认为0
# 获取数据的时间区间为[-startDay,-endDay]，startDay=period+offset_days，endDay=offset_days
# 返回值：dict类型数据counts，{id:pull_merged_count}
def getPullMergedCount(type,id,period,offset_days=0):
    if type == '0' or type == '2':
        order = 'select * from moose_pull where time > now() - ' + str(period+offset_days) + 'd' \
                ' and time <= now() - '+str(offset_days)+'d and merged_time != \'\' and user_id = ' + str(id)
        results = client.query(order).get_points()
        counts = dict()
        for result in results:
            if result['oss_id'] in counts.keys():
                counts[result['oss_id']]+=1
            else:
                counts.update({result['oss_id']:1})
        # print(order)
        # for key in counts.keys():
        #     print('oss_id = ',key,', pull request merged count = ',counts[key])
    else:
        order = 'select * from moose_pull where time > now() - ' + str(period+offset_days) + 'd' \
                ' and time <= now() - '+str(offset_days)+'d and merged_time != \'\' and oss_id = \'' + str(id)+'\''
        results = client.query(order).get_points()
        counts = dict()
        for result in results:
            if result['user_id'] in counts.keys():
                counts[result['user_id']] += 1
            else:
                counts.update({result['user_id']: 1})
        # print(order)
        # for key in counts.keys():
        #     print('user_id = ', key, ', pull request merged count = ', counts[key])
    return counts


# 功能：获取一定时间段内某一用户或某一社区的star数
# type：0--获取某一用户的数据；1--获取某一社区的数据；2--获取某一用户在某一社区的数据
# id：与type对应，0/2--user_id；1--oss_id
# period：时间跨度，获取数据对应的时间区间长度
# offset_days：有效数据偏移量，表明数据库有效数据的最后时间距离当前时间的偏差,默认为0
# 获取数据的时间区间为[-startDay,-endDay]，startDay=period+offset_days，endDay=offset_days
# 返回值：dict类型数据counts，{id:star_count}
def getStarCount(type,id,period,offset_days=0):
    if type == '0' or type == '2':
        # 注意：在input_type=‘1’时，其他的counts数据中user_id都是整数类型，而starCounts中的user_id是字符串类型
        order = 'select * from moose_star where time > now() - ' + str(period+offset_days) + 'd' \
                ' and time <= now() - '+str(offset_days)+'d and user_id = \'' + str(id)+'\''
        results = client.query(order).get_points()
        counts = dict()
        for result in results:
            counts.update({result['oss_id']:1})
        # print(order)
        # for key in counts.keys():
        #     print('oss_id = ',key,', star count = ',counts[key])
    else:
        order = 'select * from moose_star where time > now() - ' + str(period+offset_days) + 'd' \
                ' and time <= now() - '+str(offset_days)+'d and oss_id = \'' + str(id)+'\''
        results = client.query(order).get_points()
        counts = dict()
        for result in results:
            counts.update({int(result['user_id']): 1}) #注意这里为了统一user_id类型为int，要转换类型
        # print(order)
        # for key in counts.keys():
        #     print('user_id = ', key, ', star count = ', counts[key])
    return counts


# 功能：获取一定时间段内某一用户或某一社区的fork数
# type：0--获取某一用户的数据；1--获取某一社区的数据；2--获取某一用户在某一社区的数据
# id：与type对应，0/2--user_id；1--oss_id
# period：时间跨度，获取数据对应的时间区间长度
# offset_days：有效数据偏移量，表明数据库有效数据的最后时间距离当前时间的偏差,默认为0
# 获取数据的时间区间为[-startDay,-endDay]，startDay=period+offset_days，endDay=offset_days
# 返回值：dict类型数据counts，{id:fork_count}
def getForkCount(type,id,period,offset_days=0):
    if type == '0' or type == '2':
        order = 'select * from moose_fork where time > now() - ' + str(period+offset_days) + 'd' \
                ' and time <= now() - '+str(offset_days)+'d and user_id = ' + str(id)
        results = client.query(order).get_points()
        counts = dict()
        for result in results:
            counts.update({result['oss_id']:1})
        # print(order)
        # for key in counts.keys():
        #     print('oss_id = ',key,', fork count = ',counts[key])
    else:
        order = 'select * from moose_fork where time > now() - ' + str(period+offset_days) + 'd' \
                ' and time <= now() - '+str(offset_days)+'d and oss_id = \'' + str(id)+'\''
        results = client.query(order).get_points()
        counts = dict()
        for result in results:
            counts.update({result['user_id']: 1})
        # print(order)
        # for key in counts.keys():
        #     print('user_id = ', key, ', fork count = ', counts[key])
    return counts


if __name__ == '__main__':
    main()