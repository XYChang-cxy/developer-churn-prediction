from MOOSE_preprocess.main import *

def getUsers():
    oss_id = 8649239 #39469487
    churn_period = 40  # 单位：周
    offset = 0 #2021-10-11及以前的数据有效

    # 获取churn_users、loyal_users和undecided_users
    user_zero_count_0 = drawReturnVisitRateCurve(oss_id,570,81,churn_period=churn_period,low_threshold=0,offset_days=offset) #1827,261
    user_zero_count_50 = drawReturnVisitRateCurve(oss_id,570,81,churn_period=40,low_threshold=1000,draw=False,offset_days=offset)
    churn_users = dict()
    undecided_users = dict()
    loyal_users = dict()
    for key in user_zero_count_50.keys():
        if user_zero_count_50[key] < 6:
            loyal_users.update({key: user_zero_count_50[key]})
    for key in user_zero_count_0.keys():
        if user_zero_count_0[key] < 2 and key not in loyal_users.keys():
            loyal_users.update({key: user_zero_count_0[key]})

    for key in user_zero_count_0.keys():
        if user_zero_count_0[key] >=churn_period:
            churn_users.update(({key: user_zero_count_0[key]}))
        elif key not in loyal_users.keys():
            undecided_users.update(({key: user_zero_count_0[key]}))

    print(len(churn_users),len(undecided_users),len(loyal_users))


if __name__ =='__main__':
    getUsers()