from churn_data_analysis.draw_time_sequence_chart import dbHandle
import datetime
import matplotlib
import matplotlib.pyplot as plt
from churn_data_analysis.draw_return_visit_curve import getRepoUserList

matplotlib.rcParams['font.sans-serif'] = ['KaiTi']
matplotlib.rcParams['axes.unicode_minus'] = False
fmt_MySQL = '%Y-%m-%d'


# 绘制某一仓库在一段时间的流失率随时间变化曲线
# repo_id:仓库id
# startDay:筛选时间段的起始日期（包含）
# endDay:筛选时间段的终止日期（不含）
# churn_limit_list: 起始时间,流失期限 列表
# step:统计步长，为7的倍数（若不是7的倍数则选择最近值）################ 77777777777
# figname: 保存的图片名，如果为空字符串则不保存
# data_filename: 保存的数据问件名，如果为空字符串则不保存
# mode: mode=0时绘制累计流失率曲线；mode=1时绘制实时流失率曲线
# with_newcomer: 是否绘制新用户数量曲线
def drawChurnRateCurve(repo_id,startDay,endDay,churn_limit_list,step=7,mode=0,figname='',data_filename='',with_newcomer=True):
    dbObject = dbHandle()
    cursor = dbObject.cursor()

    all_user_list = [] #每个统计间隔内所有用户列表
    churn_user_list = [] #每个统计间隔内流失用户列表

    step_list = []
    user_count_list = [] #不同统计间隔的所有用户数
    churn_count_list = [] #不同统计间隔的流失用户数，当前间隔的流失用户数/上一间隔的所有用户数=流失率
    newcomer_count_list = [] #新开发者数
    #######################################
    newcomer_count_list.append(0) #第一个newcomer_count的增加会导致第二个流失率的减少，所以要往右移一位
    newcomer_count = 0
    user_inactive_weeks = dict()

    timedelta = datetime.datetime.strptime(endDay, fmt_MySQL) - datetime.datetime.strptime(startDay, fmt_MySQL)
    period_weeks = int(timedelta.days / 7) #时间段总周数

    start_day = startDay
    end_day = (datetime.datetime.strptime(start_day, fmt_MySQL) + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    print(startDay,endDay)

    if step < 7:
        step = 7
    elif step % 7 !=0:
        if step-int(step/7)*7 < int(step/7)*7+7-step:
            step = int(step/7)*7
        else:
            step = int(step/7)*7 + 7
    for i in range(period_weeks):
        week_user_list=getRepoUserList(repo_id,startDay=start_day,endDay=end_day)
        churn_limit = 53
        for j in range(len(churn_limit_list)-1,-1,-1):
            if churn_limit_list[j][0]<=start_day:
                churn_limit = int(churn_limit_list[j][1])
                break

        if mode == 0:
            for user_id in user_inactive_weeks.keys():
                if user_id in week_user_list and user_inactive_weeks[user_id] > 0:  # 上周无活动，本周有活动
                    user_inactive_weeks[user_id]=0
                    if user_id in churn_user_list: # 流失用户回归
                        churn_user_list.remove(user_id)
                elif user_id not in week_user_list:   # 本周没有活动
                    user_inactive_weeks[user_id]+=1
                    if user_inactive_weeks[user_id]==churn_limit and user_id not in churn_user_list:
                        churn_user_list.append(user_id)
            for user_id in week_user_list:
                if user_id not in all_user_list:
                    newcomer_count += 1
                    all_user_list.append(user_id) # mode=0时，all_user_list只增不减
                if user_id not in user_inactive_weeks.keys():
                    user_inactive_weeks[user_id]=0
        else:   # mode = 1
            for user_id in user_inactive_weeks.keys():
                if user_id in week_user_list and user_inactive_weeks[user_id] > 0:  # 上周无活动，本周有活动
                    user_inactive_weeks[user_id]=0
                    if user_id in churn_user_list:  # 在一个step内被判定为流失又回归
                        churn_user_list.remove(user_id)
                elif user_id not in week_user_list:   # 本周没有活动
                    user_inactive_weeks[user_id]+=1
                    if user_inactive_weeks[user_id]==churn_limit and user_id not in churn_user_list:
                        churn_user_list.append(user_id)
                        if user_id in all_user_list:
                            all_user_list.remove(user_id)
            for user_id in week_user_list:
                if user_id not in all_user_list:
                    newcomer_count += 1
                    all_user_list.append(user_id)
                if user_id not in user_inactive_weeks.keys():
                    user_inactive_weeks[user_id]=0

        if step == 7 or (i+1)*7 % step == 0:
            user_count_list.append(len(all_user_list))
            churn_count_list.append(len(churn_user_list))
            step_list.append(i*7)
            newcomer_count_list.append(newcomer_count)
            newcomer_count = 0
            if mode == 1:
                churn_user_list = []

        start_day = end_day
        end_day = (datetime.datetime.strptime(start_day, fmt_MySQL) + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
        if end_day > endDay:
            end_day = endDay
        print(start_day, end_day)
        # print(sorted(all_user_list))
        # print(sorted(churn_user_list))
        # print()

    rate_list = [0.0]
    for i in range(1,len(step_list)):
        if user_count_list[i-1]==0:
            rate_list.append(0.0)
        else:
            rate_list.append(float(churn_count_list[i])/user_count_list[i-1])
    print(churn_count_list)
    print(user_count_list)
    print(step_list)
    print(rate_list)
    if mode == 0:
        line_color = 'orangered'
        ax2_color = 'limegreen'
    else:
        line_color = 'blue'
        ax2_color = 'fuchsia'
    fig = plt.figure(figsize=(10,5))
    ax = fig.add_subplot(111)

    ax.plot(step_list, rate_list, label='开发者流失率', linewidth=1, color=line_color, marker=',')
    ax.legend(loc="upper left")
    ax.set_xlabel('时间（天）')
    ax.set_ylabel('开发者流失率（%）')

    if with_newcomer == True:
        ax2 = ax.twinx()
        ax2.plot(step_list,newcomer_count_list[0:-1],label='新增开发者数', linewidth=1, color=ax2_color, marker=',')
        ax2.legend(loc="upper right")
        ax2.set_ylabel('新增开发者数')
    title_content = '开发者流失率'
    if with_newcomer == True:
        title_content += '/新增开发者数量'
    if mode == 0:
        title_content = '累计'+title_content
    else:
        title_content += '随时间变化'
    plt.title('社区（repo_id = ' + str(repo_id) + '）' + startDay + '~' + endDay + '期间'+title_content+'曲线(step='+str(step)+')')
    if figname != '':
        plt.savefig(figname[0:-4]+'-'+str(mode)+figname[-4:])
    plt.show()
    if data_filename!='':
        with open(data_filename[0:-4]+'-'+str(mode)+data_filename[-4:],'w',encoding='utf-8')as f:
            line = 'user_count_list,'
            for count in user_count_list:
                line+=str(count)+','
            f.write(line+'\n')
            line = 'churn_count_list,'
            for count in churn_count_list:
                line += str(count)+','
            f.write(line+'\n')


# 为每个仓库的全部历史绘制用户流失率曲线
# dir_name: 保存图像和曲线数据的文件夹的名称
# churn_limit_file: 存储流失期限数据的文件
# with_newcomer: 是否绘制新用户数量曲线
def drawChurnRateCurvesForRepos(dir_name,churn_limit_file,with_newcomer=True):
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    order = 'select id,repo_name,repo_id,created_at from churn_search_repos_final where id = 29'
    cursor.execute(order)
    results = cursor.fetchall()
    churn_limit_lists = []
    for i in range(30):
        churn_limit_lists.append([])
    with open(churn_limit_file,'r',encoding='utf-8')as f:
        f.readline()
        for line in f.readlines():
            items = line.split(',')
            id = int(items[0])
            new_list = []
            new_list.append(items[1])
            new_list.append(items[3])
            churn_limit_lists[id-1].append(new_list)
    # for i in range(30):
    #     print(i+1)
    #     print(churn_limit_lists[i])

    for result in results:
        figname = dir_name + '/churn_rate_curves_0/' + str(result[0]) + '_' + result[1].replace('/', '_') + '-churn_rate.png'
        data_filename = dir_name + '/churn_rate_data_0/' + str(result[0]) + '_' + result[1].replace('/','_') + '-churn_rate.csv'
        startDay = result[3][0:10]
        endDay = '2022-01-01'
        repo_id = result[2]
        print()
        print(result[1] + ':', startDay + ' -- ' + endDay)
        drawChurnRateCurve(repo_id, startDay, endDay, churn_limit_lists[result[0]-1],
                           figname=figname, data_filename=data_filename,mode=0,step=28,
                           with_newcomer=with_newcomer)
        # figname = figname.replace('curves_0','curves_1')
        # data_filename = data_filename.replace('data_0','data_1')
        # drawChurnRateCurve(repo_id, startDay, endDay, churn_limit_lists[result[0]-1],
        #                    figname=figname, data_filename=data_filename, mode=1, step=28,
        #                    with_newcomer=with_newcomer)


if __name__ == '__main__':
    startDay = '2012-12-21'
    endDay = '2016-01-01'
    repo_id = 7276954
    # drawChurnRateCurve(repo_id,startDay,endDay,[['2012-12-21','13'],['2018-02-23','14']],step=39,mode=0)
    # drawChurnRateCurve(repo_id, startDay, endDay, [['2012-12-21', '13'], ['2018-02-23', '14']], step=39, mode=1)
    # drawChurnRateCurve(repo_id, startDay, endDay, [['2012-12-21', '13'], ['2018-02-23', '14']], step=7, mode=0)
    # drawChurnRateCurve(repo_id, startDay, endDay, [['2012-12-21', '13'], ['2018-02-23', '14']], step=7, mode=1)
    drawChurnRateCurvesForRepos('E:/bysj_project/churn_rate_with_newcomer','repo_churn_limits.csv')
    drawChurnRateCurvesForRepos('E:/bysj_project/churn_rate', 'repo_churn_limits.csv',with_newcomer=False)