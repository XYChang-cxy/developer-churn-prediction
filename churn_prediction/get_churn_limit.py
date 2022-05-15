# 该文件函数用于生成流失期限数据
churn_limit_filename=r'F:\MOOSE_cxy\developer_churn_prediction\churn_prediction\repo_churn_limits.csv'

def getChurnLimitListForRepo(id,startDay,endDay):
    churn_limit_list = []
    with open(churn_limit_filename, 'r', encoding='utf-8')as f:
        f.readline()
        for line in f.readlines():
            items = line.split(',')
            if int(items[0])!=id or items[2]<=startDay or items[1]>=endDay:
                continue
            new_list = []
            if startDay>=items[1]:
                new_list.append(startDay)
            elif startDay<=items[1]:
                new_list.append(items[1])
            new_list.append(int(items[3]))
            churn_limit_list.append(new_list.copy())
    f.close()
    return churn_limit_list


def getChurnLimitLists():
    churn_limit_lists = []
    for i in range(30):
        churn_limit_lists.append([])
    with open(churn_limit_filename, 'r', encoding='utf-8')as f:
        f.readline()
        for line in f.readlines():
            items = line.split(',')
            id = int(items[0])
            new_list = []
            new_list.append(items[1])
            new_list.append(int(items[3]))
            churn_limit_lists[id - 1].append(new_list.copy())
    return churn_limit_lists
