from churn_data_analysis.draw_time_sequence_chart import dbHandle
import datetime
import os
import matplotlib.pyplot as plt
import kneed
fmt_MySQL = '%Y-%m-%d'


# 根据划分点文件生成划分区间
# level:划分点过滤等级，level=0表示采用所有划分点，level=1表示采用带*/**的划分点，level=2表示采用带**的划分点
def dividePeriodByPoints(input_file,output_file,level=1):
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    order = 'select id,created_at from churn_search_repos_final'
    cursor.execute(order)
    results = cursor.fetchall()
    startDays=dict()
    for result in results:
        startDays[result[0]]=result[1]
    endDay = '2022-01-01'
    new_content = []
    with open(input_file,'r',encoding='utf-8')as f:
        for line in f.readlines():
            items = line.strip('\n').split(',')
            new_line = items[0]+','
            id = int(items[0])
            print(id)
            divide_points = []
            for i in range(1,len(items)-1):
                if items[i].find('**')!=-1:
                    divide_points.append(int(items[i].strip('**')))
                elif items[i].find('*')!=-1:
                    if level < 2:
                        divide_points.append(int(items[i].strip('*')))
                else:
                    if level == 0:
                        divide_points.append(int(items[i]))
            start_time = datetime.datetime.strptime(startDays[id][0:10],fmt_MySQL)
            left = startDays[id][0:10]
            for point in divide_points:
                right = start_time+datetime.timedelta(days=point*30)
                right = right.strftime(fmt_MySQL)
                new_line+=left+'--'+right+','
                left = right
            new_line+=left + '--' + endDay+',\n'
            new_content.append(new_line)
    filename = output_file.split('.')[0]+'_'+str(level)+'.'+output_file.split('.')[1]
    with open(filename,'w',encoding='utf-8')as f:
        for line in new_content:
            f.write(line)


# 根据绘制回访率曲线时记录的数据文件以及仓库时间段文件，生成不同时间段的流失期限并用文件保存
# data_dir: 回访率数据文件所在的文件夹路径
# period_filename: 仓库时间段文件
def getChurnLimits(data_dir,period_filename):
    filenames = os.listdir(data_dir)
    id_periods = dict()
    with open(period_filename,'r',encoding='utf-8') as f:
        for line in f.readlines():
            items = line.strip(',\n').split(',')
            id = int(items[0])
            period_list = []
            for i in range(1,len(items)):
                period_list.append(items[i])
            id_periods[id] = period_list
    file_content = []
    file_content.append('id,startDay,endDay,churn_period,return_rate,rate_10_period,\n')
    content_dict = dict()#用于根据id排序
    for i in range(30):
        content_dict[i+1]=[]
    for filename in filenames:
        id = int(filename.split('_')[0])
        period_id = int(filename.strip('.csv').split('-')[-1])
        startDay,endDay = id_periods[id][period_id].split('--')
        with open(data_dir+'/'+filename,'r',encoding='utf-8') as f:
            f.readline()
            line = f.readline()
            churn_period = line.split(',')[0]
            return_rate = line.split(',')[1]
            line=f.readline()
            rate_10_period = line.split(',')[0]
        f.close()
        content_dict[id].append(str(id)+','+startDay+','+endDay+','+churn_period+','+return_rate+','+rate_10_period+',\n')
    for i in range(30):
        for line in content_dict[i+1]:
            file_content.append(line)

    with open('repo_churn_limits.csv','w',encoding='utf-8')as f:
        for line in file_content:
            f.write(line)


# 粗略分析曲线的凹凸性，凹凸性不明显则返回none
def testConcaveConvex(list):
    left = 0
    right = len(list)-1
    mid = int((left + right)/2)
    if list[mid]*2 < (list[left]+list[right])*0.8:
        return 'convex'
    elif list[mid]*2 > (list[left]+list[right])*1.2:
        return 'concave'
    return 'none'


#########################################################################################
# 通过时序曲线数据，绘制活跃度累计增长曲线，并找肘部作为划分点
# 活跃度计算方式为粗略计算
# repo_id: 仓库id
# time_sequence_dir: 时序数据文件所在目录
# filename: 时序数据文件名（不含文件夹路径）
# save_dir:要保存的文件路径
def findRepoDividePoints(repo_id,time_sequence_dir,filename,save_dir=''):
    data_lists = []
    colors = ['red', 'limegreen', 'yellow', 'm', 'b', 'k', 'cyan', 'orangered', 'fuchsia']
    with open(time_sequence_dir+'/'+filename, 'r', encoding='utf-8')as f:
        line = f.readline()
        name_list = line.strip(',\n').split(',')
        for i in range(len(name_list)):
            data_lists.append([])
        for line in f.readlines():
            data_items = line.strip(',\n').split(',')
            for i in range(len(data_items)):
                data_lists[i].append(float(data_items[i]))
    activity_sum_list = []
    sum = 0
    time_list = data_lists[0]
    for j in range(len(time_list)):
        issue_count = data_lists[1][j]
        pull_count = data_lists[2][j]
        commit_count = data_lists[3][j]
        review_count = data_lists[4][j]
        issue_comment_count = data_lists[5][j]
        commit_comment_count = data_lists[6][j]
        review_comment_count = data_lists[7][j]
        activity = 2 * issue_count + 3 * pull_count + 4 * review_comment_count + issue_comment_count \
                   # + 2 * review_count + 2 * commit_comment_count + 3 * commit_count
        sum += activity
        activity_sum_list.append(sum)
    plt.plot(time_list, activity_sum_list, linewidth=1, color='limegreen', marker='.', label='活跃度',
             markerfacecolor='w')
    curve = testConcaveConvex(activity_sum_list)
    if curve!='none':
        kneeLocator = kneed.KneeLocator(time_list, activity_sum_list, curve=curve, direction='increasing',
                                        online=True)  # 下凸，递增
        flag = 0
        for elbow in kneeLocator.all_elbows:
            if flag == 0:
                axv_color = 'blue'
                flag = 1
            else:
                axv_color = 'orangered'
            plt.axvline(x=elbow, ymin=0.05, ymax=0.95, color=axv_color, linestyle='--',
                        label=curve + ' elbow = ' + str(elbow))
    plt.legend(loc="upper left")
    plt.xlabel('时间（天）')
    plt.ylabel('社区活跃度')
    plt.title('社区（repo_id = '+str(repo_id)+'）活跃度累计变化曲线及肘部')
    if save_dir!='':
        plt.savefig(save_dir + '/' + filename.replace('.csv', '.png'))
    plt.show()

    '''new_data_lists = []
    new_data_lists.append(data_lists[0])  # 时间
    for i in range(1,len(data_lists)):
        new_data_lists.append([])
        sum = 0
        for j in range(len(data_lists[i])):
            sum += data_lists[i][j]
            new_data_lists[i].append(sum)
    plt.figure(figsize=(10, 5))
    for i in range(1, len(data_lists)):
        plt.plot(new_data_lists[0], new_data_lists[i], linewidth=1, color=colors[i - 1], marker='.', label=name_list[i],
                 markerfacecolor='w')
        kneeLocator = kneed.KneeLocator(new_data_lists[0], new_data_lists[i], curve='convex', direction='increasing',
                                        online=False)   # 下凸，递增
        plt.axvline(x=kneeLocator.elbow, ymin=0.05, ymax=0.95, color=colors[i-1], linestyle='--',
                    label='elbow = ' + str(kneeLocator.elbow))

    # id = int(filename.split('_')[0])
    # for point in id_divide_points[id]:
    #     date = datetime.datetime.strptime(create_times[id - 1], fmt_MySQL) + datetime.timedelta(days=point)
    #     date = date.strftime(fmt_MySQL)
    #     plt.axvline(x=point, ymin=0.05, ymax=0.95, color='orangered', linestyle='--',
    #                 label='date = ' + date)

    plt.legend(loc="upper left")
    plt.xlabel('时间（天）')
    plt.ylabel('数量')
    step = int(data_lists[0][1]) - int(data_lists[0][0])
    plt.title('社区（repo_id=' + str(repo_id) + '）' + 'create_times[id - 1]' + '~' + 'end_time' + '期间不同数据'
              + '累计数量时序曲线（step=' + str(step) + ')')
    if save_dir != '':
        plt.savefig(save_dir + '/' + filename.replace('.csv', '.png'))
    plt.show()'''


# 通过绘制活跃度累计增长曲线，并找肘部作为划分点
# 活跃度计算方式：详见activity_data_dir
# repo_id: 仓库id
# activity_data_dir: 仓库活跃度数据文件所在目录
# filename: 仓库活跃度数据文件名（不含文件夹路径）
# save_dir:要保存的文件路径
def findRepoDividePointsByActivity(repo_id,activity_data_dir,filename,save_dir='',step=7):
    if step!=7 and step % 7 != 0:
        step = int(step/7)*7+7
    time_list = []
    activity_sum_list = []
    activity_sum = 0.0
    with open(activity_data_dir+'/'+filename,'r',encoding='utf-8')as f:
        line = f.readline()
        i = 1
        for line in f.readlines():
            activity_sum += float(line.split(',')[1])
            if i*7 % step == 0:
                time_list.append(int(line.split(',')[0])-step+7)
                activity_sum_list.append(activity_sum)
            i += 1

    plt.plot(time_list, activity_sum_list, linewidth=1, color='orangered', marker='.', label='活跃度累加值',
             markerfacecolor='w')
    curve = testConcaveConvex(activity_sum_list)
    if curve != 'none':
        kneeLocator = kneed.KneeLocator(time_list, activity_sum_list, curve=curve, direction='increasing',
                                        online=True)  # 下凸，递增
        flag = 0
        for elbow in kneeLocator.all_elbows:
            if flag == 0:
                axv_color = 'limegreen'
                flag = 1
            else:
                axv_color = 'blue'
            plt.axvline(x=elbow, ymin=0.05, ymax=0.95, color=axv_color, linestyle='--',
                        label=curve + ' elbow = ' + str(elbow))
    plt.legend(loc="upper left")
    plt.xlabel('时间（天）')
    plt.ylabel('社区活跃度')
    plt.title('社区（repo_id = ' + str(repo_id) + '）活跃度累计变化曲线及肘部(step='+str(step)+')')
    if save_dir != '':
        plt.savefig(save_dir + '/' + filename.replace('.csv', '.png'))
    plt.show()


if __name__ == '__main__':
    input_file = 'repo_period_divide_points_30.txt'
    output_file = 'repo_periods.csv'
    # dividePeriodByPoints(input_file,output_file,1)

    data_dir = 'E:/bysj_project/return_visit_rate_period/return_visit_rate_data_period'
    period_filename = 'repo_periods_1.csv'
    # getChurnLimits(data_dir,period_filename)

    #####################################################
    repo_id = '156401841'
    time_sequence_dir = 'E:/bysj_project/time_sequence/time_sequence_data'
    filename = '1_alan-turing-institute_sktime.csv'
    # findRepoDividePoints(repo_id,time_sequence_dir,filename,'')

    #####################################################
    # filenames = os.listdir(time_sequence_dir)
    # # 为filenames根据仓库id排序
    # id_filenames = dict()
    # for filename in filenames:
    #     id_filenames[int(filename.split('_')[0])] = filename
    # dbObject = dbHandle()
    # cursor = dbObject.cursor()
    # cursor.execute('select id,repo_id,created_at from churn_search_repos_final')
    # results = cursor.fetchall()
    # for result in results:
    #     findRepoDividePoints(result[1],time_sequence_dir,id_filenames[result[0]],
    #                          'C:/Users/cxy/Desktop/test/test')

    #########################################################
    activity_data_dir = 'E:/bysj_project/repo_activity/without_commit/repo_activity_7'
    filenames = os.listdir(activity_data_dir)
    id_filenames = dict()
    for filename in filenames:
        id_filenames[int(filename.split('_')[0])] = filename
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select id,repo_id from churn_search_repos_final')
    results = cursor.fetchall()
    for result in results:
        findRepoDividePointsByActivity(result[1],activity_data_dir,id_filenames[result[0]],
                                       'C:/Users/cxy/Desktop/test/test',step=28)