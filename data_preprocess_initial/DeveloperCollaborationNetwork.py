

#获取某一社区在某一时间段内的开发者协作网络
def getDeveloperCollaborationNetwork(client,oss_id,startDay,endDay):
    user_index=dict()
    i=0
    results = client.query('select user_id from moose_issue_comment '
                           'where time > now() - ' + str(startDay) + 'd and time <= now() - ' + str(endDay) + \
                           'd and oss_id = \'' + str(oss_id) + '\'').get_points()
    for result in results:
        if result['user_id'] not in user_index.keys():
            user_index.update({result['user_id']:i})
            i += 1
    results = client.query('select user_id from moose_review '
                           'where time > now() - ' + str(startDay) + 'd and time <= now() - ' + str(endDay) + \
                           'd and oss_id = \'' + str(oss_id) + '\'').get_points()
    for result in results:
        if result['user_id'] not in user_index.keys():
            user_index.update({result['user_id']: i})
            i += 1
    results = client.query('select user_id from moose_review_comment '
                           'where time > now() - ' + str(startDay) + 'd and time <= now() - ' + str(endDay) + \
                           'd and oss_id = \'' + str(oss_id) + '\'').get_points()
    for result in results:
        if result['user_id'] not in user_index.keys():
            user_index.update({result['user_id']: i})
            i += 1
    DCN = []
    for j in range (i):
        DCN.append([])
        for k in range (i):
            DCN[j].append(0)

    issue_comment_users = dict()
    review_users = dict()
    review_comment_users = dict()
    results = client.query('select issue_number,user_id from moose_issue_comment '
                           'where time > now() - ' + str(startDay) + 'd and time <= now() - ' + str(endDay) + \
                           'd and oss_id = \'' + str(oss_id) + '\'').get_points()
    for result in results:
        if result['issue_number'] in issue_comment_users.keys():
            users = issue_comment_users[result['issue_number']]
        else:
            users = []
        users.append(result['user_id'])
        issue_comment_users.update({result['issue_number']:users})
    results = client.query('select pull_id,user_id from moose_review '
                           'where time > now() - ' + str(startDay) + 'd and time <= now() - ' + str(endDay) + \
                           'd and oss_id = \'' + str(oss_id) + '\'').get_points()
    for result in results:
        if result['pull_id'] in review_users.keys():
            users = review_users[result['pull_id']]
        else:
            users = []
        users.append(result['user_id'])
        review_users.update({result['pull_id']:users})
    results = client.query('select pull_id,user_id from moose_review_comment '
                           'where time > now() - ' + str(startDay) + 'd and time <= now() - ' + str(endDay) + \
                           'd and oss_id = \'' + str(oss_id) + '\'').get_points()
    for result in results:
        if result['pull_id'] in review_comment_users.keys():
            users = review_comment_users[result['pull_id']]
        else:
            users = []
        users.append(result['user_id'])
        review_comment_users.update({result['pull_id']: users})
    for key in issue_comment_users.keys():
        for user1 in issue_comment_users[key]:
            for user2 in issue_comment_users[key]:
                DCN[user_index[user1]][user_index[user2]] +=1
    for key in review_users.keys():
        for user1 in review_users[key]:
            for user2 in review_users[key]:
                DCN[user_index[user1]][user_index[user2]] +=1
    for key in review_comment_users.keys():
        for user1 in review_comment_users[key]:
            for user2 in review_comment_users[key]:
                DCN[user_index[user1]][user_index[user2]] +=1
    for j in range(len(user_index)):
        DCN[j][j] = 0
    DCN0 = []
    for j in range(i):
        DCN0.append([])
        for k in range(i):
            if DCN[j][k]>0:
                DCN0[j].append(1)
            else:
                DCN0[j].append(0)
    index_user = dict()
    for key in user_index.keys():
        index_user.update({user_index[key]:key})

    return DCN,DCN0,index_user,user_index


#获取DCN的节点的度数
def getDCNDegrees(user_index, DCN):
    user_degree = dict()
    for user in user_index.keys():
        wd = 0
        for d in DCN[user_index[user]]:
            if d > 0:
                wd += 1
        user_degree.update({user:wd})
    return user_degree


#获取DCN的节点加权度
def getDCNWeightedDegrees(user_index, DCN):
    user_degree = dict()
    for user in user_index.keys():
        wd = 0
        for d in DCN[user_index[user]]:
            wd+=d
        user_degree.update({user:wd})
    return user_degree


# 介数中心性：参考https://blog.csdn.net/qq_35531985/article/details/105373753
# 时间复杂性太大，结点数不能超过40
# 可以使用networkx.algorithms.centrality.betweenness_centrality，该算法时间复杂度很低
# https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.betweenness_centrality.html

# 获取DCN所有节点的介数中心性,normalized=True时会将betweeness乘 2/(n-1)(n-2)来进行正则化
def getBetweeness(DCN,normalized=True):
    shortest_paths = getAllShortestPaths(DCN)
    betweeness = dict()
    for i in range(len(DCN)):
        bi = 0
        for key in shortest_paths.keys():
            sigma_i = 0
            nodes = key.split(',')
            s = int(nodes[0])
            t = int(nodes[1])
            if i==s or i==t or s==t:
                continue
            for path in shortest_paths[key]:
                if i in path:
                    sigma_i+=1
            if sigma_i == 0:
                delta = 0.0
            else:
                delta = float(sigma_i)/float(len(shortest_paths[key]))
            bi += delta
            print(i,delta)
        if normalized==True:
            C=(len(DCN)-1)*(len(DCN)-2)/2
            betweeness.update({i: bi/C})
        else:
            betweeness.update({i: bi})
    return betweeness


#获取DCN中从start到end的所有path
def getAllPaths(DCN, start, end, path=None):
    if path is None:
        path = []
    path=path+[start]
    if start==end:
        return [path]
    paths=[]
    for i in range(len(DCN[start])):
        if DCN[start][i]>0 and i not in path:
            newpaths = getAllPaths(DCN,i,end,path)
            for newpath in newpaths:
                paths.append(newpath)
    return paths

def getAllShortestPaths(DCN):
    shortest_paths=dict()
    for i in range(len(DCN)):
        for j in range(i,len(DCN)):
            paths=getAllPaths(DCN,i,j)
            s_paths = []
            print(i,j)
            if len(paths)>=1:
                s_len = len(paths[0])
                for k in range(1,len(paths)):
                    if len(paths[k]) < s_len:
                        s_len = len(paths[k])
                for k in range(len(paths)):
                    if len(paths[k])==s_len:
                        s_paths.append(paths[k])
            shortest_paths.update({str(i)+','+str(j):s_paths})
    return shortest_paths


