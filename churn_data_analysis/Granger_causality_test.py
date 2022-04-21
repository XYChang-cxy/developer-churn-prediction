import os
from churn_data_analysis.draw_time_sequence_chart import dbHandle
import datetime
import matplotlib
import matplotlib.pyplot as plt
from churn_data_analysis.net_churn_rate_analysis import getNetChurnRateData

matplotlib.rcParams['font.sans-serif'] = ['KaiTi']
matplotlib.rcParams['axes.unicode_minus'] = False
fmt_MySQL = '%Y-%m-%d'


# 保存用于格兰杰因果关系检验的数据
# time_sequence_dir: 保存时序数据文件的文件夹
# user_dir: 保存用于计算流失率的用户数据的文件夹
# save_dir: 保存生成数据的文件夹
# churn_limit_lists: 各个仓库的流失期限数据
def saveGrangerDataForRepos(time_sequence_dir,user_dir,save_dir,churn_limit_lists,step=28):
    filenames = os.listdir(time_sequence_dir)
    time_sequence_filenames=dict()
    for filename in filenames:
        id = int(filename.split('_')[0])
        time_sequence_filenames[id]=filename

    filenames = os.listdir(user_dir)
    user_filenames = dict()
    for filename in filenames:
        id = int(filename.split('_')[0])
        user_filenames[id]=filename

    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select id,repo_id from churn_search_repos_final where id = 2')
    results = cursor.fetchall()

    for result in results:
        id = result[0]
        repo_id = result[1]
        churn_limit_list = churn_limit_lists[id-1]
        churn_rate_list = getNetChurnRateData(repo_id,user_dir+'/'+user_filenames[id],churn_limit_list,step)[1]
        with open(time_sequence_dir+'/'+time_sequence_filenames[id],'r',encoding='utf-8')as f:
            first_line = f.readline()
            content_list = f.readlines()
        with open(save_dir+'/'+user_filenames[id],'w',encoding='utf-8')as f:
            first_line = first_line.strip('\n')+'churn_rate,\n'
            f.write(first_line)
            for i in range(len(content_list)):
                f.write(content_list[i].strip('\n')+str(churn_rate_list[i])+',\n')


if __name__ == '__main__':
    time_sequence_dir = r'E:\bysj_project\time_sequence_28\time_sequence_data'
    user_dir = r'E:\bysj_project\repo_users_by_period\data_28'
    save_dir = r'E:\bysj_project\granger_causality_test\data_28'
    churn_limit_lists = []
    for i in range(30):
        churn_limit_lists.append([])
    with open('repo_churn_limits.csv', 'r', encoding='utf-8')as f:
        f.readline()
        for line in f.readlines():
            items = line.split(',')
            id = int(items[0])
            new_list = []
            new_list.append(items[1])
            new_list.append(items[3])
            churn_limit_lists[id - 1].append(new_list)
    saveGrangerDataForRepos(time_sequence_dir,user_dir,save_dir,churn_limit_lists,28)


