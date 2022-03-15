from churn_data_analysis.draw_time_sequence_chart import dbHandle
import datetime
import os
fmt_MySQL = '%Y-%m-%d'


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


if __name__ == '__main__':
    input_file = 'repo_period_divide_points_30.txt'
    output_file = 'repo_periods.csv'
    # dividePeriodByPoints(input_file,output_file,1)

    data_dir = 'E:/bysj_project/return_visit_rate_period/return_visit_rate_data_period'
    period_filename = 'repo_periods_1.csv'
    getChurnLimits(data_dir,period_filename)
