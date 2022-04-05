import os

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
# step:统计步长，为7的倍数（若不是7的倍数则选择最近值）
# figname: 保存的图片名，如果为空字符串则不保存
# data_filename: 保存的数据问件名，如果为空字符串则不保存
# mode: mode=0时绘制累计流失率曲线；mode=1时绘制实时流失率曲线
# with_newcomer: 是否绘制新用户数量曲线
def drawChurnRateCurve(repo_id,startDay,endDay,churn_limit_list,step=7,mode=0,figname='',data_filename='',with_newcomer=True):
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
    ax.set_ylabel('开发者流失率')

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
            line = 'newcomer_count_list,'
            for count in newcomer_count_list:
                line += str(count)+','
            f.write(line+'\n')


# 为每个仓库的全部历史绘制用户流失率曲线
# dir_name: 保存图像和曲线数据的文件夹的名称
# churn_limit_file: 存储流失期限数据的文件
# with_newcomer: 是否绘制新用户数量曲线
def drawChurnRateCurvesForRepos(dir_name,churn_limit_file,step=28,with_newcomer=True):
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    order = 'select id,repo_name,repo_id,created_at from churn_search_repos_final'
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
                           figname=figname, data_filename=data_filename,mode=0,step=step,
                           with_newcomer=with_newcomer)
        # figname = figname.replace('curves_0','curves_1')
        # data_filename = data_filename.replace('data_0','data_1')
        # drawChurnRateCurve(repo_id, startDay, endDay, churn_limit_lists[result[0]-1],
        #                    figname=figname, data_filename=data_filename, mode=1, step=step,
        #                    with_newcomer=with_newcomer)


# 保存仓库每个时间段统计的所有历史用户、所有历史流失用户、留存用户、活跃用户、流失用户、新用户、回访用户
# dir_name: 保存文件的路径名
# churn_limit_lists: 不同社区的流失期限数据列表，每个列表每行格式为：起始时间,流失期限
# step:统计步长，为7的倍数（若不是7的倍数则选择最近值）
def saveRepoUsersByPeriod(dir_name,churn_limit_lists,step=7):
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select id,repo_id,repo_name,created_at from churn_search_repos_final where id > 22')
    results = cursor.fetchall()

    if step < 7:
        step = 7
    elif step % 7 !=0:
        if step-int(step/7)*7 < int(step/7)*7+7-step:
            step = int(step/7)*7
        else:
            step = int(step/7)*7 + 7

    for result in results:
        id = result[0]
        repo_id = result[1]
        repo_name = result[2]
        create_time = result[3][0:10]
        end_time = '2022-01-01'
        filename = dir_name+'/'+str(id)+'_'+repo_name.replace('/','-').replace(' ','_')+'-'+str(step)+'.csv'
        all_id_lists = []
        retain_id_lists = []
        churn_all_id_lists = []
        churn_id_lists = []
        newcomer_id_lists = []
        return_id_lists = []
        active_id_lists = []
        step_list = []
        user_inactive_weeks = dict()

        timedelta = datetime.datetime.strptime(end_time, fmt_MySQL) - datetime.datetime.strptime(create_time, fmt_MySQL)
        period_weeks = int(timedelta.days / 7)  # 时间段总周数

        start_day = create_time
        end_day = (datetime.datetime.strptime(start_day, fmt_MySQL) + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
        print(str(id)+' --',start_day,'-', end_day)

        churn_limit_list = churn_limit_lists[id - 1]

        all_user_list = []  # 每个统计间隔内累计所有用户列表
        retain_user_list = []   # 每个统计间隔内留存的用户列表
        churn_all_user_list = []  # 每个统计间隔内累计流失用户列表
        churn_user_list = []  # 每个统计间隔内流失用户列表
        new_user_list = []  # 每个统计间隔内新用户列表
        return_user_list = []   # 每个统计间隔内回访用户列表
        active_user_list = []  # 每个统计间隔内活跃用户列表

        for i in range(period_weeks):
            week_user_list = getRepoUserList(repo_id, startDay=start_day, endDay=end_day)
            churn_limit = 53
            for j in range(len(churn_limit_list) - 1, -1, -1):
                if churn_limit_list[j][0] <= start_day:
                    churn_limit = int(churn_limit_list[j][1])
                    break
            for user_id in user_inactive_weeks.keys():
                if user_id in week_user_list and user_inactive_weeks[user_id] > 0:  # 上周无活动，本周有活动
                    user_inactive_weeks[user_id] = 0
                    if user_id in churn_user_list:  # 流失用户回归
                        churn_user_list.remove(user_id)
                    if user_id in churn_all_user_list:
                        churn_all_user_list.remove(user_id)
                elif user_id not in week_user_list:  # 本周没有活动
                    user_inactive_weeks[user_id] += 1
                    if user_inactive_weeks[user_id] >= churn_limit and user_id not in churn_all_user_list:# !!!之前的流失率计算代码有误
                        if user_inactive_weeks[user_id] > churn_limit:#########################################
                            print(repo_id,i,user_id,churn_limit,user_inactive_weeks[user_id])
                        churn_user_list.append(user_id)
                        churn_all_user_list.append(user_id)
                        if user_id in retain_user_list:
                            retain_user_list.remove(user_id)
            for user_id in week_user_list:
                if user_id not in active_user_list:  # 本时间段内活跃用户
                    active_user_list.append(user_id)
                if user_id in all_user_list and user_id not in retain_user_list:  # 回访用户
                    retain_user_list.append(user_id)
                    return_user_list.append(user_id)
                if user_id not in all_user_list:  # 新用户
                    retain_user_list.append(user_id)
                    all_user_list.append(user_id)
                    new_user_list.append(user_id)
                if user_id not in user_inactive_weeks.keys():
                    user_inactive_weeks[user_id] = 0

            if (i + 1) * 7 % step == 0:
                all_id_lists.append(all_user_list.copy())
                retain_id_lists.append(retain_user_list.copy())
                newcomer_id_lists.append(new_user_list.copy())
                return_id_lists.append(return_user_list.copy())
                churn_id_lists.append(churn_user_list.copy())
                churn_all_id_lists.append(churn_all_user_list.copy())
                active_id_lists.append(active_user_list.copy())
                step_list.append(i * 7)
                new_user_list = []
                return_user_list = []
                churn_user_list = []
                active_user_list = []

            start_day = end_day
            end_day = (datetime.datetime.strptime(start_day, fmt_MySQL) + datetime.timedelta(days=7)).strftime(
                '%Y-%m-%d')
            if end_day > end_time:
                end_day = end_time
            print(start_day, end_day)
        with open(filename,'w',encoding='utf-8')as f:
            f.write('time,all users in history,all churners in history,retained users,active users in period,'
                    'churners in period,new users in period,return visitors in period,\n')
            for i in range(len(step_list)):
                line = str(step_list[i])+','
                for user_id in all_id_lists[i]:
                    line += str(user_id)+' '
                line += ','
                for user_id in churn_all_id_lists[i]:
                    line += str(user_id)+' '
                line += ','
                for user_id in retain_id_lists[i]:
                    line += str(user_id)+' '
                line += ','
                for user_id in active_id_lists[i]:
                    line += str(user_id)+' '
                line += ','
                for user_id in churn_id_lists[i]:
                    line += str(user_id)+' '
                line += ','
                for user_id in newcomer_id_lists[i]:
                    line += str(user_id)+' '
                line += ','
                for user_id in return_id_lists[i]:
                    line += str(user_id)+' '
                line += ',\n'
                f.write(line)
        f.close()


# 绘制不同的流失率曲线
# repo_id:仓库id
# filename:仓库对应的user id文件名
# mode:曲线类别,0--历史总流失率、1--净流失率一、2--净流失率二、3--基期流失率、4--基期末期平均法、5--用户生命时间法、6--几月流失率
# churn_limit_list: 仓库不同时间段的流失期限列表, mode=1、2时使用
# step: 统计时间间隔
# start_dis: mode=6时使用，开始的时间点，单位为step，可正可负
# end_dis: mode=6时使用，结束的时间点，单位为step，可正可负
# figname: 存储的图像名，若为空字符串则不存储
def drawChurnRateCurvesByUsersData(repo_id,filename,mode=0,churn_limit_list=None,step=7,start_dis=0,end_dis=0,figname = ''):
    if churn_limit_list is None:
        churn_limit_list = []
        if mode ==1 or mode == 2:
            print('churn limit list is None!')
    all_count_list = []
    retain_count_list = []
    churn_all_count_list = []
    churn_count_list = []
    active_count_list = []
    new_count_list = []
    new_return_count_list = []
    step_list = []
    churn_all_id_lists = []  # mode = 2时使用
    retain_id_lists = []     # mode = 2时使用
    churn_id_lists = []      # mode = 1, 2, 6时使用
    active_id_lists = []     # mode = 1, 2, 6时使用
    with open(filename, 'r', encoding='utf-8')as f:
        f.readline()
        for line in f.readlines():
            contents = line.split(',')
            step_list.append(int(contents[0]))
            all_count_list.append(len(contents[1].split(' ')) - 1)
            churn_all_count_list.append(len(contents[2].split(' ')) - 1)
            retain_count_list.append(len(contents[3].split(' ')) - 1)
            active_count_list.append(len(contents[4].split(' ')) - 1)
            churn_count_list.append(len(contents[5].split(' ')) - 1)
            new_count_list.append(len(contents[6].split(' ')) - 1)
            new_return_count_list.append(len(contents[6].split(' ')) + len(contents[7].split(' ')) - 2)
            if mode == 1 or mode == 2 or mode == 6: #用于寻找准确的分母区间
                churn_id_lists.append(contents[5].split(' ')[0:-1])
                active_id_lists.append(contents[4].split(' ')[0:-1])
            if mode == 2:
                churn_all_id_lists.append(contents[2].split(' ')[0:-1])
                retain_id_lists.append(contents[3].split(' ')[0:-1])
    rate_list = [0.0]
    # print(len(step_list),len(new_count_list),len(new_return_count_list))#################################
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select created_at from churn_search_repos_final where repo_id = '+str(repo_id))
    result = cursor.fetchone()
    create_time = result[0][0:10]
    end_time = '2022-01-01'

    title_contents = ['历史总流失率','第一类净流失率','第二类净流失率','基期流失率','基期末期平均法','用户生命时间法','几月流失率']
    colors = ['orangered', 'limegreen','b', 'm','cyan','fuchsia','red', 'yellow','k']

    if mode < 6:
        if mode == 0:# 历史总流失率
            for i in range(1, len(step_list)):
                if all_count_list[i - 1] == 0:
                    rate_list.append(0.0)
                else:
                    rate_list.append(float(churn_all_count_list[i]) / all_count_list[i - 1])
        elif mode == 1 or mode == 2:# 净流失率一/二
            for i in range(1,len(step_list)):
                churn_limit = 53
                start_day = (datetime.datetime.strptime(create_time, fmt_MySQL) + datetime.timedelta(days=step*i)).strftime(fmt_MySQL)
                for j in range(len(churn_limit_list) - 1, -1, -1):
                    if churn_limit_list[j][0] <= start_day:
                        churn_limit = int(churn_limit_list[j][1])
                        break
                if i*step < churn_limit:
                    rate_list.append(0.0)
                else:
                    index = i - int(churn_limit*7/step)
                    if index < 0:
                        index = 0
                    max_exist_count = 0 #mode=1,step>7时可能找不到准确的区间，则找近似区间
                    max_exist_index = i - int(churn_limit*7/step)
                    if_find_period = True #是否准确找到分母区间
                    if churn_count_list[i] > 0:  # 寻找准确的分母区间
                        if_find_period = False
                        for k in range(i - int(churn_limit*7/step) + 9, i - int(churn_limit*7/step) - 10, -1):##############################
                            if k < 0 or k >= len(active_id_lists):
                                continue
                            exist_count = 0
                            for user_id in churn_id_lists[i]:
                                if user_id in active_id_lists[k]:
                                    exist_count += 1
                            if exist_count > max_exist_count:
                                max_exist_index = k
                                max_exist_count = exist_count
                            if exist_count == churn_count_list[i]:
                                index = k
                                if_find_period = True
                                # print(i,index - (i - int(churn_limit*7/step)), exist_count, index, i - int(churn_limit*7/step))
                                break
                        if if_find_period == False:
                            index = max_exist_index
                            print(i,index - (i - int(churn_limit*7/step)), max_exist_count,churn_count_list[i])#########################
                    if mode == 1:
                        if active_count_list[index] == 0:
                            rate_list.append(0.0)
                        else:
                            if if_find_period:
                                rate_list.append(float(churn_count_list[i]) / active_count_list[index])
                            else:# 没有找到合适的分母
                                rate_list.append(float(max_exist_count) / active_count_list[index])
                    elif mode == 2:
                        churn_count = 0
                        for user_id in churn_all_id_lists[i]:
                            if user_id in retain_id_lists[index]:
                                churn_count += 1
                        # print(i,churn_count-churn_all_count_list[i],churn_count,churn_all_count_list[i])
                        if retain_count_list[index] == 0:
                            rate_list.append(0.0)
                        else:
                            rate_list.append(float(churn_count) / retain_count_list[index])
        elif mode == 3: # 基期流失率
            for i in range(1,len(step_list)):
                if retain_count_list[i - 1] == 0:
                    rate_list.append(0.0)
                else:
                    rate_list.append(float(churn_count_list[i]) / retain_count_list[i - 1])
        elif mode == 4: # 基期末期平均法
            for i in range(1,len(step_list)):
                if (retain_count_list[i - 1]+retain_count_list[i]) == 0:
                    rate_list.append(0.0)
                else:
                    rate_list.append(float(churn_count_list[i])*2.0 / (retain_count_list[i - 1]+retain_count_list[i]))
        elif mode == 5: # 用户生命时间法
            for i in range(1,len(step_list)):
                if (retain_count_list[i - 1]+new_return_count_list[i]*0.5) == 0.0:
                    rate_list.append(0.0)
                else:
                    rate_list.append(float(churn_count_list[i]) / (retain_count_list[i - 1]+new_return_count_list[i]*0.5))##############
        plt.figure(figsize=(10, 5))
        plt.plot(step_list, rate_list, label='开发者流失率(mode='+str(mode)+')', linewidth=1, color=colors[mode], marker=',')
        plt.title(
            '社区（repo_id = ' + str(repo_id) + '）' + create_time +'~'+end_time+'期间' +'开发者流失率（'+title_contents[mode]+'）曲线(mode='+str(mode)
            +',step=' + str(step) + ')')
        if figname!='':
            plt.savefig(figname)
        plt.show()
    elif mode == 6:#几月流失率
        plt.figure(figsize=(10,5))
        if start_dis >= 0:
            start_point = start_dis
        else:
            start_point = len(step_list)+start_dis
        if end_dis >=0:
            end_point = len(step_list)-end_dis
        else:
            end_point = len(step_list)+end_dis
        start_time = (datetime.datetime.strptime(create_time, fmt_MySQL) + datetime.timedelta(days=start_point*step))\
            .strftime('%Y-%m-%d')
        end_time = (datetime.datetime.strptime(create_time, fmt_MySQL) + datetime.timedelta(days=end_point*step))\
            .strftime('%Y-%m-%d')
        for i in range(start_point,end_point-1):
            month_list = []
            month_rate_list = []
            for j in range(i+1,len(step_list)):
                churn_count = 0
                for user_id in churn_id_lists[j]:
                    if user_id in active_id_lists[i]:
                        churn_count += 1
                month_list.append(j-i)
                month_rate_list.append(float(churn_count)/active_count_list[i])
            # print(month_list)
            # break
            plt.plot(month_list,month_rate_list, label='period='+str(i+1)+'的开发者流失率(mode='+str(mode)+')', linewidth=1, marker=',')
        plt.title('社区（repo_id = ' + str(repo_id) + '）' + start_time +'~'+end_time+'期间' +'开发者流失率（'+title_contents[mode]+'）曲线(mode='+str(mode)
            +',step=' + str(step) + ')')
        # plt.legend(loc='upper left')
        if figname!='':
            plt.savefig(figname)
        plt.show()


# 为所有仓库绘制净流失率曲线
# users_data_dir:存储各个周期内用户数据的文件夹
# save_dir: 保存图像和曲线数据的文件夹的名称
# churn_limit_file: 存储流失期限数据的文件
# with_newcomer: 是否绘制新用户数量曲线
# step:必须和users_data_dir一致
def drawNetChurnRateCurvesForRepos(users_data_dir,save_dir,churn_limit_file,step=28):
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    order = 'select id,repo_name,repo_id from churn_search_repos_final'
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

    filenames = os.listdir(users_data_dir)
    id_filenames = dict()
    for filename in filenames:
        id_filenames[int(filename.split('_')[0])] = filename

    for result in results:
        figname = save_dir + '/net_churn_rate_curves_'+str(step)+'/' + str(result[0]) + '_' + result[1].replace('/', '_') \
                  + '-net_churn_rate.png'
        id = result[0]
        repo_id = result[2]
        print(result[0],result[2])###############
        drawChurnRateCurvesByUsersData(repo_id, users_data_dir+'/'+id_filenames[id],
                                       mode=1, churn_limit_list=churn_limit_lists[id-1], step=step,figname=figname)


if __name__ == '__main__':
    startDay = '2012-12-21'
    endDay = '2016-01-01'
    repo_id = 7276954
    # drawChurnRateCurve(repo_id,startDay,endDay,[['2012-12-21','13'],['2018-02-23','14']],step=39,mode=0)
    # drawChurnRateCurve(repo_id, startDay, endDay, [['2012-12-21', '13'], ['2018-02-23', '14']], step=39, mode=1)
    # drawChurnRateCurve(repo_id, startDay, endDay, [['2012-12-21', '13'], ['2018-02-23', '14']], step=7, mode=0)
    # drawChurnRateCurve(repo_id, startDay, endDay, [['2012-12-21', '13'], ['2018-02-23', '14']], step=7, mode=1)
    # drawChurnRateCurvesForRepos('E:/bysj_project/churn_rate_with_newcomer_28', 'repo_churn_limits.csv', step=28)
    # drawChurnRateCurvesForRepos('E:/bysj_project/churn_rate_with_newcomer_7','repo_churn_limits.csv',step=7)
    # drawChurnRateCurvesForRepos('E:/bysj_project/churn_rate', 'repo_churn_limits.csv',with_newcomer=False)

    # 保存社区每周的不同类型用户列表
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
    # saveRepoUsersByPeriod('E:/bysj_project/repo_users_by_period/data_28',churn_limit_lists,28)

    # drawChurnRateCurvesByUsersData(repo_id,'E:/bysj_project/repo_users_by_period/data_7/2_Alluxio-alluxio-7.csv',
    #                                mode=1,churn_limit_list=churn_limit_lists[1],step=7)

    # drawChurnRateCurvesByUsersData(repo_id, 'E:/bysj_project/repo_users_by_period/data_28/2_Alluxio-alluxio-28.csv',
    #                                mode=1, churn_limit_list=churn_limit_lists[1], step=28)

    # drawChurnRateCurvesByUsersData(repo_id, 'E:/bysj_project/repo_users_by_period/data_28/2_Alluxio-alluxio-28.csv',
    #                                mode=6, churn_limit_list=churn_limit_lists[1], step=28,start_dis=-26,end_dis=0)

    # drawNetChurnRateCurvesForRepos('E:/bysj_project/repo_users_by_period/data_7',
    #                                'E:/bysj_project/net_churn_rate_curves',
    #                                'repo_churn_limits.csv',
    #                                step=7)
    drawNetChurnRateCurvesForRepos('E:/bysj_project/repo_users_by_period/data_28',
                                   'E:/bysj_project/net_churn_rate_curves/test',
                                   'repo_churn_limits.csv',
                                   step=28)