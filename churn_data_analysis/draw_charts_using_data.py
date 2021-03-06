# This file is used to draw charts through data files
# created by Xiyu Chang on 2022-03-13
import matplotlib
import matplotlib.pyplot as plt
import os
from churn_data_analysis.draw_return_visit_curve import dbHandle
import datetime
fmt_MySQL = '%Y-%m-%d'


# 根据时序图的数据记录文件重新绘制图像
# time_sequence_dir: 时序图数据文件所在文件夹
# divide_points_filename: 划分点文件名，若不为空则在曲线中标明划分点
# save_dir: 保存新生成图片的目录，若为空字符串则不保存
def drawTimeSequencesUsingData(time_sequence_dir,divide_points_filename='',save_dir=''):
    filenames = os.listdir(time_sequence_dir)
    # 为filenames根据仓库id排序
    id_filenames=dict()
    for filename in filenames:
        id_filenames[int(filename.split('_')[0])]=filename
    filenames = []
    for i in range(30):
        if i+1 in id_filenames.keys():
            filenames.append(id_filenames[i+1])
    # print(filenames)
    create_times = []
    repo_id_list = []
    end_time = '2022-01-01'
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select id,repo_id,created_at from churn_search_repos_final')
    results = cursor.fetchall()
    for result in results:
        # print(result[0],result[1][0:10])
        create_times.append(result[2][0:10])
        repo_id_list.append(result[1])

    # 获取时间段划分点
    id_divide_points = dict()
    if divide_points_filename!='':
        with open(divide_points_filename,'r',encoding='utf-8')as f:
            for line in f.readlines():
                items = line.strip(',\n').split(',')
                id = int(items[0])
                points = []
                for i in range(1,len(items)):
                    if items[i].find('**')!=-1:
                        points.append(30*int(items[i].strip('**')))
                    elif items[i].find('*')!=-1:
                        points.append(30*int(items[i].strip('*')))
                id_divide_points[id]=points

    colors = ['red', 'limegreen', 'yellow', 'm', 'b', 'k', 'cyan', 'orangered', 'fuchsia']
    for filename in filenames:
        data_lists=[]
        with open(time_sequence_dir+'/'+filename,'r',encoding='utf-8')as f:
            line = f.readline()
            name_list = line.strip(',\n').split(',')
            for i in range(len(name_list)):
                data_lists.append([])
            for line in f.readlines():
                data_items = line.strip(',\n').split(',')
                for i in range(len(data_items)):
                    data_lists[i].append(float(data_items[i]))
        plt.figure(figsize=(10, 5))
        for i in range(1,len(data_lists)):
            plt.plot(data_lists[0], data_lists[i], linewidth=1, color=colors[i-1], marker='.',label=name_list[i],
                     markerfacecolor='w')
        id = int(filename.split('_')[0])
        for point in id_divide_points[id]:
            date = datetime.datetime.strptime(create_times[id-1],fmt_MySQL)+datetime.timedelta(days=point)
            date = date.strftime(fmt_MySQL)
            plt.axvline(x=point, ymin=0.05, ymax=0.95, color='orangered', linestyle='--',
                        label='date = '+ date)
        plt.legend(loc="upper left")
        plt.xlabel('时间（天）')
        plt.ylabel('数量')
        step = int(data_lists[0][1])-int(data_lists[0][0])
        plt.title('社区（repo_id=' + str(repo_id_list[id-1]) + '）' + create_times[id-1] + '~' + end_time + '期间不同数据'
                  + '数量时序曲线（step=' + str(step) + ')')
        if save_dir != '':
            plt.savefig(save_dir+'/'+filename.replace('.csv','.png'))
        plt.show()


# 根据回访率曲线的数据记录文件重新绘制图像
# return_visit_dir: 回访率曲线数据文件所在文件夹
# period_filename: 记录分段情况文件的文件名，若为空则表示时间起始时间为仓库创建时间
# save_dir: 保存新生成图片的目录，若为空字符串则不保存
def drawReturnVisitCurves(return_visit_dir,period_filename='',save_dir=''):
    # 读取数据文件名
    filenames = os.listdir(return_visit_dir)
    # 为filenames根据仓库id排序
    id_filenames = dict()
    for filename in filenames:
        id = int(filename.split('_')[0])
        if id not in id_filenames.keys():
            id_filenames[id]=[]
        id_filenames[id].append(filename)
    filenames = []
    for i in range(30):
        if i + 1 in id_filenames.keys():
            for name in id_filenames[i + 1]:
                filenames.append(name)

    # 获取仓库创建时间和repo_id
    create_times = []
    repo_id_list = []
    end_time = '2022-01-01'
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select id,repo_id,created_at from churn_search_repos_final')
    results = cursor.fetchall()
    for result in results:
        # print(result[0],result[1][0:10])
        create_times.append(result[2][0:10])
        repo_id_list.append(result[1])

    id_periods = dict()
    if period_filename != '':
        # 获取不同仓库id对应的时间段
        with open(period_filename, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                items = line.strip(',\n').split(',')
                id = int(items[0])
                period_list = []
                for i in range(1, len(items)):
                    period_list.append(items[i])
                id_periods[id] = period_list

    for filename in filenames:
        with open(return_visit_dir + '/' + filename, 'r', encoding='utf-8')as f:
            rates = []
            for rate in f.readline().strip(',\n').split(','):
                rates.append(float(rate))
            weeks = range(1,53)
            plt.figure(figsize=(5,3))
            plt.plot(weeks, rates, label='流失开发者回访率', linewidth=1,  marker='.', color='mediumblue',
                     markerfacecolor='w',alpha=0.7)
            elbow = int(f.readline().split(',')[0])
            rate_10_week = int(f.readline().split(',')[0])
            plt.axvline(x=elbow, ymin=0.05, ymax=0.95,  linestyle='--',color='orangered',alpha=0.7,
                        label='elbow = ' + str(elbow))
            # plt.axvline(x=rate_10_week, ymin=0.05, ymax=0.95, color='orangered', linestyle='--',
            #             label='10% rate = ' + str(rate_10_week))
            plt.legend(loc="upper right")
            plt.xlabel('流失期限（周）')
            plt.ylabel('流失开发者回访率（%）')
            id = int(filename.split('_')[0])
            if period_filename == '':
                startDay = create_times[id - 1]
                endDay = end_time
            else:
                period_id = int(filename.strip('.csv').split('-')[-1])
                startDay,endDay = id_periods[id][period_id].split('--')
            # plt.title(
            #     '社区（repo_id = ' + str(repo_id_list[id - 1]) + '）' + startDay + '~' + endDay + '期间用户回访率曲线')
            if save_dir != '':
                plt.savefig(save_dir + '/' + filename.replace('.csv', '.png'),dpi=300,bbox_inches = 'tight')
            plt.show()


# 根据数据绘制流失率曲线
# data_dir: 存储流失率数据的文件夹
# step: 必须和文件中的step一致
# mode: mode=0时绘制累计流失率曲线；mode=1时绘制实时流失率曲线,和数据文件一致
# save_dir: 存储的目标文件夹，若为空字符串则不存储
def drawChurnRateCurves(data_dir,step,mode,save_dir=''):
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select id,repo_id,created_at from churn_search_repos_final')
    results = cursor.fetchall()

    filenames = os.listdir(data_dir)
    # 为filenames根据仓库id排序
    id_filenames = dict()
    for filename in filenames:
        id = int(filename.split('_')[0])
        if id not in id_filenames.keys():
            id_filenames[id] = []
        id_filenames[id].append(filename)
    filenames = []
    for i in range(30):
        if i + 1 in id_filenames.keys():
            for name in id_filenames[i + 1]:
                filenames.append(name)

    for result in results:
        id = result[0]
        repo_id = result[1]
        create_time = result[2][0:10]
        end_time = '2022-01-01'
        filename = filenames[id-1]
        user_count_list = []
        churn_count_list = []
        newcomer_count_list = []
        step_list = []
        with open(data_dir+'/'+filename,'r',encoding='utf-8')as f:
            line = f.readline()
            for count in line.split(',')[1:-1]:
                user_count_list.append(int(count))
            line = f.readline()
            for count in line.split(',')[1:-1]:
                churn_count_list.append(int(count))
            line = f.readline()
            if line.find(',')!=-1:
                for count in line.split(',')[1:-1]:
                    newcomer_count_list.append(int(count))
        for i in range(1,len(user_count_list)+1):
            step_list.append(i*step)
        rate_list = [0.0]
        for i in range(1, len(step_list)):
            if user_count_list[i - 1] == 0:
                rate_list.append(0.0)
            else:
                rate_list.append(float(churn_count_list[i]) / user_count_list[i - 1])
        if mode == 0:
            line_color = 'orangered'
            ax2_color = 'limegreen'
        else:
            line_color = 'blue'
            ax2_color = 'fuchsia'
        fig = plt.figure(figsize=(10, 5))
        ax = fig.add_subplot(111)

        ax.plot(step_list, rate_list, label='开发者流失率', linewidth=1, color=line_color, marker=',')
        ax.legend(loc="upper left")
        ax.set_xlabel('时间（天）')
        ax.set_ylabel('开发者流失率（%）')

        if len(newcomer_count_list)>0:
            ax2 = ax.twinx()
            ax2.plot(step_list, newcomer_count_list[0:-1], label='新增开发者数', linewidth=1, color=ax2_color, marker=',')
            ax2.legend(loc="upper right")
            ax2.set_ylabel('新增开发者数')
        title_content = '开发者流失率'
        if len(newcomer_count_list)>0:
            title_content += '/新增开发者数量'
        if mode == 0:
            title_content = '累计' + title_content
        else:
            title_content += '随时间变化'
        plt.title(
            '社区（repo_id = ' + str(repo_id) + '）' + create_time + '~' + end_time + '期间' + title_content + '曲线(step=' + str(
                step) + ')')
        if save_dir != '':
            figname = filename.split('.')[0]+'-churn_rate-'+str(mode)+'.png'
            plt.savefig(save_dir+'/'+figname)
        plt.show()


# 根据数据绘制流失率变化量曲线
# data_dir: 存储流失率数据的文件夹
# step: 必须和文件中的step一致
# mode: mode=0时绘制累计流失率曲线；mode=1时绘制实时流失率曲线,和数据文件一致
# save_dir: 存储的目标文件夹，若为空字符串则不存储
def drawChurnRateDeltaCurve(data_dir,step,mode,save_dir=''):
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select id,repo_id,created_at from churn_search_repos_final')
    results = cursor.fetchall()

    filenames = os.listdir(data_dir)
    # 为filenames根据仓库id排序
    id_filenames = dict()
    for filename in filenames:
        id = int(filename.split('_')[0])
        if id not in id_filenames.keys():
            id_filenames[id] = []
        id_filenames[id].append(filename)
    filenames = []
    for i in range(30):
        if i + 1 in id_filenames.keys():
            for name in id_filenames[i + 1]:
                filenames.append(name)

    for result in results:
        id = result[0]
        repo_id = result[1]
        create_time = result[2][0:10]
        end_time = '2022-01-01'
        filename = filenames[id-1]
        user_count_list = []
        churn_count_list = []
        newcomer_count_list = []
        step_list = []
        with open(data_dir+'/'+filename,'r',encoding='utf-8')as f:
            line = f.readline()
            for count in line.split(',')[1:-1]:
                user_count_list.append(int(count))
            line = f.readline()
            for count in line.split(',')[1:-1]:
                churn_count_list.append(int(count))
            line = f.readline()
            if line.find(',')!=-1:
                for count in line.split(',')[1:-1]:
                    newcomer_count_list.append(int(count))
        for i in range(1,len(user_count_list)+1):
            step_list.append(i*step)
        rate_list = [0.0]
        for i in range(1, len(step_list)):
            if user_count_list[i - 1] == 0:
                rate_list.append(0.0)
            else:
                rate_list.append(float(churn_count_list[i]) / user_count_list[i - 1])
        delta_rate_list = [0.0]
        for i in range(1,len(rate_list)):
            delta_rate_list.append(rate_list[i]-rate_list[i-1])
        delta_newcomer_list = [0.0]
        if len(newcomer_count_list)>0:
            for i in range(1, len(newcomer_count_list)):
                delta_newcomer_list.append(newcomer_count_list[i - 1] - newcomer_count_list[i])
        if mode == 0:
            line_color = 'red'
            ax2_color = 'green'
        else:
            line_color = 'cyan'
            ax2_color = 'black'
        fig = plt.figure(figsize=(10, 5))
        ax = fig.add_subplot(111)

        ax.plot(step_list, delta_rate_list, label='流失率变化量', linewidth=1, color=line_color, marker=',')
        ax.legend(loc="upper left")
        ax.set_xlabel('时间（天）')
        ax.set_ylabel('流失率变化量（%）')

        if len(newcomer_count_list)>0:
            ax2 = ax.twinx()
            ax2.plot(step_list, delta_newcomer_list[0:-1], label='newcomer变化量相反数', linewidth=1, color=ax2_color, marker=',')
            ax2.legend(loc="upper right")
            ax2.set_ylabel('newcomer变化量相反数')
        title_content = '流失率变化量'
        if len(newcomer_count_list)>0:
            title_content += '/newcomer变化量'
        if mode == 0:
            title_content = '累计' + title_content
        else:
            title_content += '随时间变化'
        plt.title(
            '社区（repo_id = ' + str(repo_id) + '）' + create_time + '~' + end_time + '期间' + title_content + '曲线(step=' + str(
                step) + ')')
        if save_dir != '':
            figname = filename.split('.')[0]+'-churn_rate-'+str(mode)+'.png'
            plt.savefig(save_dir+'/'+figname)
        plt.show()


if __name__ == '__main__':
    # drawTimeSequencesUsingData('E:/bysj_project/time_sequence/time_sequence_data','repo_period_divide_points_30.txt','E:/bysj_project/time_sequence/time_sequence_charts_with_divide')
    # drawReturnVisitCurves('E:/bysj_project/return_visit_rate/return_visit_rate_data','','C:/Users/cxy/Desktop/test')
    # drawReturnVisitCurves('E:/bysj_project/return_visit_rate_period/return_visit_rate_data_period','repo_periods_1.csv','C:/Users/cxy/Desktop/test')
    # drawChurnRateCurves('E:/bysj_project/churn_rate_with_newcomer_28/churn_rate_data_0',28,0,'C:/Users/cxy/Desktop/test/test')
    # drawChurnRateDeltaCurve('E:/bysj_project/churn_rate_with_newcomer_28/churn_rate_data_1',28,1,'E:/bysj_project/churn_rate_with_newcomer_28/delta_curves_1')

    drawReturnVisitCurves('E:/bysj_project/return_visit_rate/return_visit_rate_data','','C:/Users/cxy/Desktop/return_visit_curve')

    pass
