import matplotlib
import matplotlib.pyplot as plt
from churn_data_analysis import settings
import pymysql
import datetime
from churn_data_analysis import draw_return_visit_curve
from churn_data_analysis.draw_return_visit_curve import dbHandle

matplotlib.rcParams['font.sans-serif'] = ['KaiTi']
matplotlib.rcParams['axes.unicode_minus'] = False

fmt_MySQL = '%Y-%m-%d'


# 绘制仓库特定时间段内某一类数据平均每日数量随时间变化曲线
# repo_id: 仓库id
# table_name: 数据对应的表名
# startDay: 起始日期
# endDay: 结束日期
# step: 计算数量的步长，默认每7天计算一次数量并求平均
def drawTimeSequenceCount(repo_id,table_name,startDay,endDay,step=7):
    dbObject = draw_return_visit_curve.dbHandle()
    cursor = dbObject.cursor()
    counts = []
    times = []
    timedelta = datetime.datetime.strptime(endDay, fmt_MySQL) - datetime.datetime.strptime(startDay, fmt_MySQL)
    time_count = int(timedelta.days/step)
    for i in range(time_count):
        times.append(step * i)
        start_day = (datetime.datetime.strptime(startDay, fmt_MySQL) + datetime.timedelta(days=i * step)).strftime(
            fmt_MySQL)
        end_day = (datetime.datetime.strptime(start_day, fmt_MySQL) + datetime.timedelta(days=step)).strftime(
            fmt_MySQL)
        if table_name == 'repo_user':
            item_count = draw_return_visit_curve.getRepoUserList(repo_id, start_day, end_day)
        else:
            if table_name=='repo_review':
                time_name = 'submit_time'
            elif table_name == 'repo_commit':
                time_name = 'commit_time'
            elif table_name == 'repo_commit_comment':
                time_name = 'comment_time'
            elif table_name == 'repo_star':
                time_name = 'star_time'
            else:
                time_name = 'create_time'
            order = 'select count(*) from ' + table_name + ' where repo_id = ' + str(
                repo_id) + ' and ' + time_name + ' between \"' + start_day + '\" and \"' + end_day +'\"'
            # print(order)
            cursor.execute(order)
            result = cursor.fetchone()
            item_count = result[0]
        counts.append(float(item_count)/step)
    plt.figure(figsize=(10,5))
    plt.plot(times, counts, label=table_name[5:] + '数量', linewidth=1, color='g', marker='.', markerfacecolor='w')
    plt.legend(loc="upper right")
    plt.xlabel('时间（天）')
    plt.ylabel('数量')
    plt.title('社区（repo_id=' + str(repo_id) + '）' + startDay + '~' + endDay + '期间'+table_name[5:]
              +'数量时序曲线（step='+str(step)+')')
    plt.show()


# 绘制某一仓库特定时间段内某些类数据平均每日数量随时间变化曲线
# repo_id: 仓库id
# table_list: 数据表名的列表
# startDay: 起始日期
# endDay: 结束日期
# step: 计算数量的步长，默认每7天计算一次数量并求平均
# figname: 保存的图片名，如果为空字符串则不保存
# data_filename: 保存的数据问件名，如果为空字符串则不保存
def drawTimeSequences(repo_id,table_list,startDay,endDay,step=7,figname='',data_filename=''):
    dbObject = draw_return_visit_curve.dbHandle()
    cursor = dbObject.cursor()
    count_list = []
    for i in range(len(table_list)):
        count_list.append([])
    times = []
    timedelta = datetime.datetime.strptime(endDay, fmt_MySQL) - datetime.datetime.strptime(startDay, fmt_MySQL)
    time_count = int(timedelta.days/step)
    for i in range(time_count):
        print(str(i)+'/'+str(time_count))
        times.append(step * i)
        start_day = (datetime.datetime.strptime(startDay, fmt_MySQL) + datetime.timedelta(days=i * step)).strftime(
            fmt_MySQL)
        end_day = (datetime.datetime.strptime(start_day, fmt_MySQL) + datetime.timedelta(days=step)).strftime(
            fmt_MySQL)
        for j in range(len(table_list)):
            table_name = table_list[j]
            if table_name == 'repo_user':
                item_count = draw_return_visit_curve.getRepoUserList(repo_id, start_day, end_day)
            else:
                if table_name=='repo_review':
                    time_name = 'submit_time'
                elif table_name == 'repo_commit':
                    time_name = 'commit_time'
                elif table_name == 'repo_commit_comment':
                    time_name = 'comment_time'
                elif table_name == 'repo_star':
                    time_name = 'star_time'
                else:
                    time_name = 'create_time'
                order = 'select count(*) from ' + table_name + ' where repo_id = ' + str(
                    repo_id) + ' and ' + time_name + ' between \"' + start_day + '\" and \"' + end_day +'\"'
                # print(order)
                cursor.execute(order)
                result = cursor.fetchone()
                item_count = result[0]
            count_list[j].append(float(item_count)/step)
    plt.figure(figsize=(10,5))
    colors = ['red', 'limegreen', 'yellow', 'm', 'b', 'k', 'cyan', 'orangered','fuchsia']
    for j in range(len(count_list)):
        plt.plot(times, count_list[j], linewidth=1.5, marker='.', markerfacecolor='w',color=colors[j],alpha=0.7)
    if data_filename!='':#保存数据
        with open(data_filename,'w',encoding='utf-8')as f:
            first_line = 'time,'
            for table_name in table_list:
                first_line+=table_name+','
            f.write(first_line+'\n')
            for j in range(time_count):
                new_line = str(times[j])+','
                for i in range(len(count_list)):
                    new_line+=str(count_list[i][j])+','
                f.write(new_line+'\n')
    plt.legend(table_list,loc="upper left")
    plt.xlabel('时间（天）')
    plt.ylabel('数量')
    plt.title('社区（repo_id=' + str(repo_id) + '）' + startDay + '~' + endDay + '期间不同数据'
              +'数量时序曲线（step='+str(step)+')')
    if figname!= '':
        plt.savefig(figname)
    plt.show()


# 绘制所有仓库全部历史不同数据数量随时间变化曲线,保存图像和曲线数据
# dir_name: 保存图像和曲线数据的文件夹的名称
# table_list: 数据表名的列表
def drawTimeSequenceForAllRepos(dir_name,table_list):
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    order = 'select id,repo_name,repo_id,created_at from churn_search_repos_final'
    cursor.execute(order)
    results = cursor.fetchall()
    for result in results:
        figname = dir_name + '/time_sequence_charts/'+str(result[0])+'_'+result[1].replace('/','_')+'.png'
        data_filename = dir_name + '/time_sequence_data/' + str(result[0]) + '_' + result[1].replace('/', '_') + '.csv'
        startDay = result[3][0:10]
        endDay = '2022-01-01'
        repo_id = result[2]
        print()
        print(result[1]+':',startDay+' -- '+endDay)
        drawTimeSequences(repo_id,table_list,startDay,endDay,30,figname,data_filename)


# 绘制某一仓库特定时间段内star和fork日均/累计数量随时间变化曲线
# repo_id: 仓库id
# startDay: 起始日期
# endDay: 结束日期
# step: 计算数量的步长，默认每7天计算一次数量并求平均
# figname: 保存的图片名，如果为空字符串则不保存
# data_filename: 保存的数据问件名，如果为空字符串则不保存
# mode: 模式，0表示日均值，1表示累计值
def drawStarForkCountCurve(repo_id,startDay,endDay,step=7,mode=0,figname='',data_filename=''):
    table_list = ['repo_fork','repo_star']
    time_names = ['create_time','star_time']
    dbObject = draw_return_visit_curve.dbHandle()
    cursor = dbObject.cursor()
    count_list = []
    for i in range(len(table_list)):
        count_list.append([])
    times = []
    timedelta = datetime.datetime.strptime(endDay, fmt_MySQL) - datetime.datetime.strptime(startDay, fmt_MySQL)
    time_count = int(timedelta.days / step)
    for i in range(time_count):
        print(str(i) + '/' + str(time_count))
        times.append(step * i)
        start_day = (datetime.datetime.strptime(startDay, fmt_MySQL) + datetime.timedelta(days=i * step)).strftime(
            fmt_MySQL)
        end_day = (datetime.datetime.strptime(start_day, fmt_MySQL) + datetime.timedelta(days=step)).strftime(
            fmt_MySQL)
        for j in range(len(table_list)):
            table_name = table_list[j]
            time_name = time_names[j]
            order = 'select count(*) from ' + table_name + ' where repo_id = ' + str(
                repo_id) + ' and ' + time_name + ' between \"' + start_day + '\" and \"' + end_day + '\"'
            # print(order)
            cursor.execute(order)
            result = cursor.fetchone()
            item_count = result[0]
            if mode == 0:
                count_list[j].append(float(item_count) / step)
            else:
                if len(count_list[j])==0:
                    count_list[j].append(item_count)
                else:
                    count_list[j].append(item_count+count_list[j][-1])

    plt.figure(figsize=(10, 5))
    colors = ['red', 'limegreen', 'yellow', 'm', 'b', 'k', 'cyan', 'orangered', 'fuchsia']
    for j in range(len(count_list)):
        plt.plot(times, count_list[j], linewidth=1.5, marker='.', markerfacecolor='w', color=colors[j], alpha=0.7)
    if data_filename != '':  # 保存数据
        with open(data_filename, 'w', encoding='utf-8')as f:
            first_line = 'time,'
            for table_name in table_list:
                first_line += table_name + ','
            f.write(first_line + '\n')
            for j in range(time_count):
                new_line = str(times[j]) + ','
                for i in range(len(count_list)):
                    new_line += str(count_list[i][j]) + ','
                f.write(new_line + '\n')
    plt.legend(table_list, loc="upper left")
    plt.xlabel('时间（天）')
    plt.ylabel('数量')
    if mode == 0:
        plt.title('社区（repo_id=' + str(repo_id) + '）' + startDay + '~' + endDay + '期间fork/star'
                  + '日均数量时序曲线（step=' + str(step) + ')')
    else:
        plt.title('社区（repo_id=' + str(repo_id) + '）' + startDay + '~' + endDay + '期间fork/star'
                  + '累计数量时序曲线（step=' + str(step) + ')')
    if figname != '':
        plt.savefig(figname)
    plt.show()


# 为所有仓库绘制fork、star曲线
# dir_name: 保存图像和曲线数据的文件夹的名称
def drawForkStarForAllRepos(dir_name):
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    order = 'select id,repo_name,repo_id,created_at from churn_search_repos_final'
    cursor.execute(order)
    results = cursor.fetchall()
    for result in results:
        figname = dir_name + '/avg_curves/' + str(result[0]) + '_' + result[1].replace('/', '_') + '_fork-star.png'
        data_filename = dir_name + '/avg_data/' + str(result[0]) + '_' + result[1].replace('/', '_') + '_fork-star.csv'
        startDay = result[3][0:10]
        endDay = '2022-01-01'
        repo_id = result[2]
        print()
        print(result[1] + ':', startDay + ' -- ' + endDay)
        drawStarForkCountCurve(repo_id, startDay,endDay,30,0,figname,data_filename)
        figname = figname.replace('avg_curves','sum_curves')
        data_filename = data_filename.replace('avg_data','sum_data')
        drawStarForkCountCurve(repo_id, startDay, endDay, 30, 1, figname, data_filename)



if __name__ == '__main__':
    startDay = '2012-12-21'
    endDay = '2022-01-01'
    repo_id = 7276954
    # drawTimeSequenceCount(repo_id,'repo_pull',startDay,endDay,step=10)
    table_list = [
        'repo_issue',
        'repo_pull',
        'repo_commit',
        'repo_review',
        # 'repo_fork',
        # 'repo_star',
        'repo_issue_comment',
        'repo_commit_comment',
        'repo_review_comment'
    ]
    # drawTimeSequences(repo_id,table_list,startDay,endDay,step=30)
    drawTimeSequenceForAllRepos('E:/bysj_project/time_sequence',table_list)
    # drawStarForkCountCurve(repo_id,startDay,endDay,30)
    # drawStarForkCountCurve(repo_id, startDay, endDay, 30,1)
    # drawForkStarForAllRepos('E:/bysj_project/time_sequence/time_sequence_fork_star')

