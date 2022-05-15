# 改文件用于获取开发者的留存时间段（等于活动时间段+流失期限时间）
from churn_prediction.data_preprocess.get_user import *


def getFirstAndLast(repo_id,user_id,churn_limit):
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select created_at from churn_search_repos_final where repo_id = '+str(repo_id))
    create_time = cursor.fetchone()[0][0:10]
    end_time = '2022-01-01'
    time_delta = (datetime.datetime.strptime(end_time,fmt_day)-datetime.datetime.strptime(create_time,fmt_day)).days
    period_weeks = int(time_delta/7)
    flag=False
    left_list = []
    right_list = []

    for i in range(period_weeks):
        start_day = (datetime.datetime.strptime(create_time,fmt_day)+datetime.timedelta(days=i*7)).strftime(fmt_day)
        end_day = (datetime.datetime.strptime(start_day,fmt_day)+datetime.timedelta(days=7)).strftime(fmt_day)
        print(i,'/',period_weeks,start_day,end_day)
        list = getRepoUserList(repo_id, start_day, end_day)
        if user_id in list:
            churn_limit = 13
            if flag == False:
                flag=True
                print('left:',start_day)
                left_list.append(start_day)
        if flag and user_id not in list:
            churn_limit-=1
            if churn_limit <= 0:
                flag = False
                churn_limit = 13
                print('right:',end_day)
                right_list.append(end_day)
    if len(right_list)<len(left_list):
        right_list.append(end_time)
    ret=[]
    for i in range(len(left_list)):
        ret.append(left_list[i]+'--'+right_list[i])
    return ret


def testUserPeriod(repo_id,user_id,startDay,endDay):
    time_delta = (datetime.datetime.strptime(endDay, fmt_day) - datetime.datetime.strptime(startDay, fmt_day)).days
    period_weeks = int(time_delta / 7)
    true_count=0
    false_count=0
    for i in range(period_weeks):
        start_day = (datetime.datetime.strptime(startDay, fmt_day) + datetime.timedelta(days=i * 7)).strftime(
            fmt_day)
        end_day = (datetime.datetime.strptime(start_day, fmt_day) + datetime.timedelta(days=7)).strftime(fmt_day)
        print(i, '/', period_weeks, start_day, end_day)
        list = getRepoUserList(repo_id, start_day, end_day)
        if user_id in list:
            print('True',end=' ')
            false_count = 0
            true_count += 1
            print(true_count)
        else:
            print('False',end=' ')
            true_count = 0
            false_count += 1
            print(false_count)



if __name__ == '__main__':
    repo_id = 7276954
    user_id = 2223813
    # print(getFirstAndLast(repo_id,user_id,churn_limit=13))

    startDay='2014-07-11'
    endDay='2021-09-24'
    testUserPeriod(repo_id,user_id,startDay,endDay)
