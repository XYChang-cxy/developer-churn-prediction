import matplotlib
import matplotlib.pyplot as plt
from churn_data_analysis import settings
import pymysql
import datetime
from churn_data_analysis import draw_return_visit_curve

matplotlib.rcParams['font.sans-serif'] = ['KaiTi']
matplotlib.rcParams['axes.unicode_minus'] = False

fmt_MySQL = '%Y-%m-%d'


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
            else:
                time_name = 'create_time'
            order = 'select count(*) from ' + table_name + ' where repo_id = ' + str(
                repo_id) + ' and ' + time_name + ' between \"' + start_day + '\" and \"' + end_day +'\"'
            # print(order)
            cursor.execute(order)
            result = cursor.fetchone()
            item_count = result[0]
        counts.append(float(item_count)/step)
    plt.plot(times, counts, label=table_name[5:] + '数量', linewidth=1, color='g', marker='.', markerfacecolor='w')
    plt.legend(loc="upper right")
    plt.xlabel('时间（天）')
    plt.ylabel('数量')
    plt.title('社区（repo_id=' + str(repo_id) + '）' + startDay + '~' + endDay + '期间'+table_name[5:]
              +'数量时序曲线（step='+str(step)+')')
    plt.show()



if __name__ == '__main__':
    startDay = '2012-12-01'
    endDay = '2022-01-01'
    repo_id = 7276954
    drawTimeSequenceCount(repo_id,'repo_pull',startDay,endDay,step=10)
