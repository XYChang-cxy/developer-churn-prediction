import os
from churn_data_analysis.draw_time_sequence_chart import dbHandle
import datetime
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from prettytable import PrettyTable
from statsmodels.tsa.stattools import adfuller
from churn_data_analysis.net_churn_rate_analysis import getNetChurnRateData
from statsmodels.tsa.vector_ar.var_model import VAR
from statsmodels.tsa.stattools import grangercausalitytests
from churn_data_analysis.churner_composition_analysis import getChurnerCompositionCurveByMetric,getChurnerCompositionCurveByScore

matplotlib.rcParams['font.sans-serif'] = ['KaiTi']
matplotlib.rcParams['axes.unicode_minus'] = False
fmt_MySQL = '%Y-%m-%d'

# 保存用于格兰杰因果关系检验的数据
# time_sequence_dir: 保存时序数据文件的文件夹
# user_dir: 保存用于计算流失率的用户数据的文件夹
# save_dir: 保存生成数据的文件夹
# user_data_dir: 存储每周用户各类数据的文件夹
# churn_limit_lists:每个仓库的流失期限
# new_metric_dir_list: 存储各类新指标时序数据的文件夹的列表
# new_metric_first_line: 新指标数据的属性名（第一行），该参数限定了数据的顺序
def saveGrangerDataForRepos(time_sequence_dir,user_dir,user_data_dir,save_dir,
                            new_metric_dir_list,new_metric_first_line,
                            threshold_filename,churn_limit_lists,step=28):
    filenames = os.listdir(time_sequence_dir)
    time_sequence_filenames=dict()
    for filename in filenames:
        id = int(filename.split('_')[0])
        time_sequence_filenames[id]=filename

    filenames = os.listdir(user_dir)
    id_user_filename = dict()
    for filename in filenames:
        id = int(filename.split('_')[0])
        id_user_filename[id]=filename

    filenames = os.listdir(user_data_dir)
    id_user_data_filename = dict()
    for filename in filenames:
        id_user_data_filename[int(filename.split('_')[0])] = filename

    filenames = os.listdir(new_metric_dir_list[0])
    id_new_metric_filename = dict()
    for filename in filenames:
        id_new_metric_filename[int(filename.split('_')[0])] = filename

    id_threshold_lists = dict()
    with open(threshold_filename, 'r', encoding='utf-8')as f:
        f.readline()
        for line in f.readlines():
            threshold_list = []
            id = int(line.split(',')[0])
            threshold_list.append(float(line.split(',')[2]))
            threshold_list.append(float(line.split(',')[5]))
            threshold_list.append(float(line.split(',')[6]))
            threshold_list.append(float(line.split(',')[8]))
            threshold_list.append(float(line.split(',')[9]))
            id_threshold_lists[id] = threshold_list.copy()

    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select id,repo_id from churn_search_repos_final')
    results = cursor.fetchall()

    for result in results:
        id = result[0]
        repo_id = result[1]
        churn_limit_list = churn_limit_lists[id-1]
        threshold_list = id_threshold_lists[id]
        user_filename = user_dir+'/'+id_user_filename[id]
        user_data_filename = user_data_dir + '/' + id_user_data_filename[id]
        churn_rate_list = getNetChurnRateData(repo_id,user_filename,churn_limit_list,step)[1]
        with open(time_sequence_dir+'/'+time_sequence_filenames[id],'r',encoding='utf-8')as f:
            first_line = f.readline()
            content_list = f.readlines()

        # imp_churn_rate_lists = []
        # for metric in range(5):
        #     imp_churn_rate_list = getChurnerCompositionCurveByMetric(repo_id,user_filename,user_data_filename,
        #                                                              threshold_list[metric],churn_limit_list,
        #                                                              metric=metric,if_draw_1=False,if_draw_2=False)[2]
        #     imp_churn_rate_lists.append(imp_churn_rate_list.copy())
        imp_churn_rate_list = getChurnerCompositionCurveByScore(repo_id,user_filename,user_data_filename,threshold_list,
                                                                if_draw_1=False,if_draw_2=False)[2]
        # imp_churn_rate_lists.append(imp_churn_rate_list.copy())

        new_metric_content_lists = []
        for dir in new_metric_dir_list:
            with open(dir+'\\'+id_new_metric_filename[id],'r',encoding='utf-8')as f:
                f.readline()
                tmp_content_list = f.readlines()
                new_metric_content_lists.append(tmp_content_list.copy())
            f.close()

        with open(save_dir+'/'+id_user_filename[id],'w',encoding='utf-8')as f:
            first_line = first_line.strip(
                '\n') + new_metric_first_line + 'net_churn_rate,imp_churn_rate,\n'
            f.write(first_line)
            for i in range(len(content_list)):
                content = content_list[i].strip('\n')
                for j in range(len(new_metric_dir_list)):
                    tmp_index = new_metric_content_lists[j][i].find(',')
                    tmp_line = new_metric_content_lists[j][i][tmp_index+1:-1]
                    content += tmp_line
                content += str(churn_rate_list[i])+','+str(imp_churn_rate_list[i])+','
                f.write(content+'\n')
        f.close()


# 生成剔除初始时间后的数据文件
def saveGrangerDataWithoutStart(granger_data_dir,granger_data_dir_2,start_days_list,step=28):
    filenames = os.listdir(granger_data_dir)
    id_filename = dict()
    id_list = []
    for filename in filenames:
        id_filename[int(filename.split('_')[0])] = filename
        id_list.append(int(filename.split('_')[0]))
    id_list = sorted(id_list)
    for id in id_list:
        content_list = []
        with open(granger_data_dir + '/' + id_filename[id],'r',encoding='utf-8')as f:
            content_list.append(f.readline())
            for j in range(int(start_days_list[id-1]/step)+1):
                f.readline()
            for line in f.readlines():
                content_list.append(line)
        with open(granger_data_dir_2 +'/' + id_filename[id],'w',encoding='utf-8')as f:
            for line in content_list:
                f.write(line)
        f.close()


# ADF单位根检验
# x: 待检测的数据
# regression: 截距项和时间趋势项，{‘c’，‘ct’，‘ctt’，‘n’}，或者为空字符串（从复杂到简单依次尝试）
# info_show: 是否打印信息
# 返回值: -1--不能拒绝原假设，是非平稳序列；0--拒绝原假设，是平稳序列（0阶单整）；-2--当前regression下拒绝原假设，但相关参数系数显著为0，需要进一步测试;
#        p_value
#        regression
def adfTest(x,regression='',info_show=False):
    if regression != '':
        result = adfuller(x,autolag='BIC',regression=regression,regresults=True) # autolag使用BIC，即Schwarz Info Criterion
        result = tuple(result)
        t_statistic = result[0]
        p_value = result[1]
        # # 如果t_statistic大于临界值，则不能拒绝H0，表明存在单位根，是非平稳序列
        critical_value_1 = result[2]['1%']  # 显著性水平在1%时的临界值
        critical_value_5 = result[2]['5%']  # 显著性水平在5%时的临界值
        critical_value_10 = result[2]['10%']  # 显著性水平在10%时的临界值

        if info_show:
            print('adf t-statistic:\t\t',"{0:.6f}".format(t_statistic))
            print('1% critical value:\t\t',"{0:.6f}".format(critical_value_1))
            print('5% critical value:\t\t', "{0:.6f}".format(critical_value_5))
            print('10% critical value:\t\t', "{0:.6f}".format(critical_value_10))
            print('p value:\t\t\t\t',"{0:.4f}".format(p_value))
        if p_value >= 0.05:
            if info_show:
                print('Can\'t reject null hypothesis: x has a unit root!(regression = '+ regression +')\n')
            return -1,p_value,regression
        else:
            if regression == 'ct':
                trend_p_value = result[3].resols.pvalues[2]
                if info_show:
                    print('P value of trend coefficient is '+"{0:.4f}".format(trend_p_value),end=', ')
                if trend_p_value < 0.05:
                    if info_show:
                        print('trend coefficient is not significantly zero.')
                        print('The sequence x is a stationary sequence!(regression = '+ regression +')\n')
                    return 0,p_value,regression
                else:
                    if info_show:
                        print('trend coefficient is significantly zero.')
                        print('Maybe you should change param \'regression\' and retry!\n')
                    return -2,p_value,regression
            elif regression == 'c':
                constant_p_value = result[3].resols.pvalues[1]
                if info_show:
                    print('P value of trend coefficient is '+"{0:.4f}".format(constant_p_value),end=', ')
                if constant_p_value < 0.05:
                    if info_show:
                        print('constant coefficient is not significantly zero.')
                        print('The sequence x is a stationary sequence!(regression = ' + regression + ')\n')
                    return 0,p_value,regression
                else:
                    if info_show:
                        print('constant coefficient is significantly zero.')
                        print('Maybe you should change param \'regression\'and retry!\n')
                    return -2,p_value,regression
            elif regression == 'n':
                if info_show:
                    print('The sequence x is a stationary sequence!(regression = ' + regression + ')\n')
                return 0,p_value,regression
    else:   # regression = ''
        result = adfuller(x, autolag='BIC', regression='ct', regresults=True)
        result = tuple(result)
        t_statistic = result[0]
        p_value = result[1]
        critical_value_1 = result[2]['1%']
        critical_value_5 = result[2]['5%']
        critical_value_10 = result[2]['10%']
        trend_p_value = result[3].resols.pvalues[2]
        if info_show:
            print('regression: constant and trend, p value:',"{0:.4f}".format(p_value),
                  ', p value of trend:',"{0:.4f}".format(trend_p_value))
        if p_value < 0.05 and trend_p_value < 0.05:
            if info_show:
                print('adf t-statistic:\t\t', "{0:.6f}".format(t_statistic))
                print('1% critical value:\t\t', "{0:.6f}".format(critical_value_1))
                print('5% critical value:\t\t', "{0:.6f}".format(critical_value_5))
                print('10% critical value:\t\t', "{0:.6f}".format(critical_value_10))
                print('The sequence x is a stationary sequence!(regression = ct)\n')
            return 0,p_value,'ct'
        else:
            result = adfuller(x, autolag='BIC', regression='c', regresults=True)
            result = tuple(result)
            t_statistic = result[0]
            p_value = result[1]
            critical_value_1 = result[2]['1%']
            critical_value_5 = result[2]['5%']
            critical_value_10 = result[2]['10%']
            constant_p_value = result[3].resols.pvalues[1]
            if info_show:
                print('regression: constant only, p value:', "{0:.4f}".format(p_value),
                      ', p value of const:', "{0:.4f}".format(constant_p_value))
            if p_value < 0.05 and constant_p_value < 0.05:
                if info_show:
                    print('adf t-statistic:\t\t', "{0:.6f}".format(t_statistic))
                    print('1% critical value:\t\t', "{0:.6f}".format(critical_value_1))
                    print('5% critical value:\t\t', "{0:.6f}".format(critical_value_5))
                    print('10% critical value:\t\t', "{0:.6f}".format(critical_value_10))
                    print('The sequence x is a stationary sequence!(regression = c)\n')
                return 0,p_value,'c'
            else:
                result = adfuller(x, autolag='BIC', regression='n', regresults=True)
                result = tuple(result)
                t_statistic = result[0]
                p_value = result[1]
                critical_value_1 = result[2]['1%']
                critical_value_5 = result[2]['5%']
                critical_value_10 = result[2]['10%']
                if info_show:
                    print('regression: no constant and no trend, p value:', "{0:.4f}".format(p_value))
                if p_value < 0.05:
                    if info_show:
                        print('adf t-statistic:\t\t', "{0:.6f}".format(t_statistic))
                        print('1% critical value:\t\t', "{0:.6f}".format(critical_value_1))
                        print('5% critical value:\t\t', "{0:.6f}".format(critical_value_5))
                        print('10% critical value:\t\t', "{0:.6f}".format(critical_value_10))
                        print('The sequence x is a stationary sequence!(regression = n)\n')
                    return 0,p_value,'n'
                else:
                    if info_show:
                        print('The sequence x has a unit root!\n')
                    return -1,p_value,''


# 为所有原序列做单位根检验（ADF检验），并存储结果
# granger_data_dir: 存储格兰杰因果分析数据的文件夹,
# unit_root_dir: 存储单位根检验结果的文件夹
def testUnitRootForFiles(granger_data_dir,unit_root_dir):
    filenames = os.listdir(granger_data_dir)
    id_filename = dict()
    for filename in filenames:
        id_filename[int(filename.split('_')[0])] = filename

    # id_list = [2,25,26,27,29]

    for id in sorted(id_filename.keys()):# id_list
        filename = id_filename[id]
        data_lists = []
        with open(granger_data_dir+'/'+filename,'r',encoding='utf-8')as f:
            name_list = f.readline().strip(',\n').split(',')[1:]
            for i in range(len(name_list)):
                data_lists.append([])
            for line in f.readlines():
                tmp_list = line.strip(',\n').split(',')[1:]
                for i in range(len(tmp_list)):
                    data_lists[i].append(float(tmp_list[i]))
        f.close()
        stationarity_list = []
        pvalue_list = []
        regression_list = []
        for tmp_list in data_lists:
            count_0 = 0
            for x in tmp_list:
                if x == 0:
                    count_0 += 1
            # if count_0 >= 0.75*len(tmp_list):
            #     print(id)
            if tmp_list[-1] >= 0 and count_0 <= 0.75*len(tmp_list):  #排除全是-1的序列和0数量超过总长度3/4的序列
                last_minus = -1
                for l in range(len(tmp_list)-1,-1,-1):
                    if tmp_list[l]<0:
                        last_minus = l
                        break
                ret = adfTest(tmp_list[last_minus+1:])
                stationarity_list.append(ret[0])
                pvalue_list.append(ret[1])
                regression_list.append(ret[2])
            else:
                stationarity_list.append(-1)
                pvalue_list.append(-1)
                regression_list.append('')

        with open(unit_root_dir + '/' + filename,'w',encoding='utf-8')as f:
            new_line = ','
            for name in name_list:
                new_line += name + ','
            f.write(new_line + '\n')

            new_line = 'stationarity,'
            for i in range(len(name_list)):
                new_line += str(stationarity_list[i]) + ','
            f.write(new_line + '\n')

            new_line = 'p value,'
            for i in range(len(name_list)):
                new_line += "{0:.4f}".format(pvalue_list[i]) + ','
            f.write(new_line + '\n')

            new_line = 'regression,'
            for i in range(len(name_list)):
                new_line += regression_list[i] + ','
            f.write(new_line + '\n')
        f.close()


# 为所有序列做单位根检验（ADF检验），并存储结果;不平稳序列做差分直到平稳，存储新数据和平稳性结果
# granger_data_dir: 存储格兰杰因果分析数据的文件夹,
# granger_data_diff_dir: 差分后数据存储的文件夹
# unit_root_dir: 存储单位根检验结果的文件夹
def testUnitRootWithDiffForFiles(granger_data_dir,granger_data_diff_dir,unit_root_dir):
    filenames = os.listdir(granger_data_dir)
    id_filename = dict()
    for filename in filenames:
        id_filename[int(filename.split('_')[0])] = filename

    # id_list = [2,25,26,27,29]

    for id in sorted(id_filename.keys()):  # id_list
        filename = id_filename[id]
        data_lists = []
        diff_data_lists = []
        diff_name_list = []
        diff_time_list = []
        with open(granger_data_dir + '/' + filename, 'r', encoding='utf-8')as f:
            name_list = f.readline().strip(',\n').split(',')[1:]
            for i in range(len(name_list)):
                data_lists.append([])
            for line in f.readlines():
                diff_time_list.append(int(line.split(',')[0]))
                tmp_list = line.strip(',\n').split(',')[1:]
                for i in range(len(tmp_list)):
                    data_lists[i].append(float(tmp_list[i]))
        f.close()
        stationarity_list = []
        pvalue_list = []
        regression_list = []
        for j in range(len(data_lists)):
            tmp_list = data_lists[j]
            name = name_list[j]
            count_0 = 0
            for x in tmp_list:
                if x == 0:
                    count_0 += 1
            if tmp_list[-1] >= 0 and count_0 <= 0.75 * len(tmp_list):  # 排除全是-1的序列和0数量超过总长度3/4的序列
                last_minus = -1
                for l in range(len(tmp_list) - 1, -1, -1):
                    if tmp_list[l] < 0:
                        last_minus = l
                        break
                ret = adfTest(tmp_list[last_minus + 1:])
                diff_order = 0
                diff_list = tmp_list[last_minus + 1:]
                while(ret[0]!=0):
                    diff_order += 1
                    diff_array = np.diff(np.array(tmp_list[last_minus + 1:]),diff_order)
                    diff_list = []
                    for k in range(diff_order):# 补全差分序列的长度
                        # diff_list.append(diff_array[k])
                        diff_list.append(0)  # 用0补全
                    diff_list.extend(diff_array.tolist())
                    ret = adfTest(diff_list)
                new_stationary_list = []
                new_stationary_list.extend(tmp_list[:last_minus+1])
                new_stationary_list.extend(diff_list)
                diff_data_lists.append(new_stationary_list)
                diff_name_list.append(name+'_'+str(diff_order))

                if diff_order > 1:
                    print('repo',id,'diff order is',diff_order)
                stationarity_list.append(diff_order)
                pvalue_list.append(ret[1])
                regression_list.append(ret[2])
            else:
                diff_data_lists.append(tmp_list)
                diff_name_list.append(name + '_')
                stationarity_list.append(-1)
                pvalue_list.append(-1)
                regression_list.append('')
        # 将平稳处理后的序列写入新文件中
        with open(granger_data_diff_dir + '/' + filename, 'w', encoding='utf-8')as f:
            line = 'time,'
            for name in diff_name_list:
                line += name+','
            f.write(line+'\n')
            for row in range(len(diff_data_lists[0])):
                line = str(diff_time_list[row]) + ','
                for col in range(len(diff_data_lists)):
                    line += str(diff_data_lists[col][row])+','
                f.write(line+'\n')
        f.close()

        with open(unit_root_dir + '/' + filename, 'w', encoding='utf-8')as f:
            new_line = ','
            for name in name_list:
                new_line += name + ','
            f.write(new_line + '\n')

            new_line = 'stationarity,'
            for i in range(len(name_list)):
                new_line += str(stationarity_list[i]) + ','
            f.write(new_line + '\n')

            new_line = 'p value,'
            for i in range(len(name_list)):
                new_line += "{0:.4f}".format(pvalue_list[i]) + ','
            f.write(new_line + '\n')

            new_line = 'regression,'
            for i in range(len(name_list)):
                new_line += regression_list[i] + ','
            f.write(new_line + '\n')
        f.close()


# 根据VAR模型测试最佳滞后阶数，如果四个值都不相等，则返回AIC结果
# data_frame: pandas中的DataFrame类型
def testVarLags(data_frame):
    var = VAR(data_frame)
    try:
        order = var.select_order(12)
    except BaseException as e:
        print(e)
        order = var.select_order()
    # print(order.summary())
    order_list = []
    order_list.append(order.aic)
    order_list.append(order.bic)
    order_list.append(order.fpe)
    order_list.append(order.hqic)
    # print(order.aic,order.bic,order.fpe,order.hqic)

    order_count_dict = dict()
    for a in order_list:
        if a not in order_count_dict.keys():
            order_count_dict[a]=0
        order_count_dict[a]+=1
    most_order = 0
    order_count = 0
    for key in order_count_dict.keys():
        if order_count_dict[key] > order_count:
            order_count = order_count_dict[key]
            most_order = key
        elif order_count == order_count_dict[key] and key < most_order:
            most_order = key
    if order_count > 1:
        return most_order,order_count,order_list
    else:
        return order.aic,order_count,order_list  # 如果四个都不一样，则根据AIC结果返回


# used_lags: 整数，滞后系数
# 返回值：flag1--若为True说明第二列数据（流失率）是因；flag2--若为True说明第一列数据是因
def grangerCausalityTest(data_frame,used_lags,x1_name,x2_name,verbose=False):
    maxlag = []
    maxlag.append(used_lags)

    if verbose:
        print(
            '\nNull Hypothesis: \"' + x2_name + '\" does not Granger Cause \"' + x1_name +
            '\". Granger Causality Test results are:'
        )
    ret1=grangercausalitytests(data_frame.iloc[:, [0, 1]], maxlag,verbose=verbose)
    ssr_ftest_p_1 = float("{0:.4f}".format(ret1[used_lags][0]['ssr_ftest'][1]))
    ssr_chi2test_p_1 = float("{0:.4f}".format(ret1[used_lags][0]['ssr_chi2test'][1]))
    lrtest_p_1 = float("{0:.4f}".format(ret1[used_lags][0]['lrtest'][1]))
    params_ftest_p_1 = float("{0:.4f}".format(ret1[used_lags][0]['params_ftest'][1]))
    p_values_1 = [ssr_ftest_p_1,ssr_chi2test_p_1,lrtest_p_1,params_ftest_p_1]
    # print(p_values_1)

    if verbose:
        print(
            '\n\nNull Hypothesis: \"' + x1_name + '\" does not Granger Cause \"' + x2_name +
            '\". Granger Causality Test results are:'
        )
    ret2=grangercausalitytests(data_frame.iloc[:, [1, 0]], maxlag,verbose=verbose)
    ssr_ftest_p_2 = float("{0:.4f}".format(ret2[used_lags][0]['ssr_ftest'][1]))
    ssr_chi2test_p_2 = float("{0:.4f}".format(ret2[used_lags][0]['ssr_chi2test'][1]))
    lrtest_p_2 = float("{0:.4f}".format(ret2[used_lags][0]['lrtest'][1]))
    params_ftest_p_2 = float("{0:.4f}".format(ret2[used_lags][0]['params_ftest'][1]))
    p_values_2 = [ssr_ftest_p_2,ssr_chi2test_p_2,lrtest_p_2,params_ftest_p_2]
    # print(p_values_2)
    if max(p_values_1) < 0.05:
        flag1 = True
    else:
        flag1 = False
    if max(p_values_2) < 0.05:
        flag2 = True
    else:
        flag2 = False

    return flag1,flag2,p_values_1,p_values_2


# 为granger_data_dir文件夹所有文件的所有序列做格兰杰因果检验
# 该函数运行前需要先做单位根检验
def grangerTestForFiles(granger_data_dir,unit_root_dir,granger_result_dir):
    filenames = os.listdir(granger_data_dir)
    id_filename = dict()
    id_list = []
    for filename in filenames:
        id_filename[int(filename.split('_')[0])] = filename
        id_list.append(int(filename.split('_')[0]))
    id_list = sorted(id_list)

    for id in id_list:
        filename = id_filename[id]

        stationary_metric_index = []
        stationary_rate_index = []

        with open(unit_root_dir+'/'+filename,'r',encoding='utf-8')as f:
            name_list = f.readline().strip('\n').split(',')[:-1]
            stationarity_list = f.readline().strip('\n').split(',')[:-1]
            for i in range(1,len(name_list)-2):
                if stationarity_list[i]=='0' or stationarity_list[i]=='1':  # 对平稳序列和一阶差分序列进行因果检验
                    stationary_metric_index.append(i)
            for i in range(len(name_list)-2,len(name_list)):
                if stationarity_list[i] == '0' or stationarity_list[i]=='1':
                    stationary_rate_index.append(i)
        with open(granger_result_dir+'/'+filename,'w',encoding='utf-8')as f:
            f.write(','+name_list[-2]+',churn_rate_pvalue,'+name_list[-1]+',imp_churn_rate_pvalue,\n')
        f.close()
        for i in stationary_metric_index:
            new_line = name_list[i] + ','
            for j in stationary_rate_index:
                data_frame = pd.read_csv(granger_data_dir+'/'+filename, usecols=[i, j])

                var_ret = testVarLags(data_frame)
                if var_ret[0] <= 0:#############################
                    print('VAR estimation result is '+str(var_ret[0])+':',filename,name_list[i],name_list[j])
                    new_line += ',,'
                else:
                    used_lags = var_ret[0]
                    granger_ret = grangerCausalityTest(data_frame,used_lags,name_list[i],name_list[j])
                    if granger_ret[0] and granger_ret[1]:
                        granger_value = 'cause and effect'
                    elif granger_ret[0] and not granger_ret[1]:
                        granger_value = 'cause'
                    elif not granger_ret[0] and granger_ret[1]:
                        granger_value = 'effect'
                    else:
                        granger_value = 'none'
                    p_value = str(granger_ret[2][0]) + ' ' + str(granger_ret[3][0])
                    new_line += granger_value+','+p_value+','
            with open(granger_result_dir+'/'+filename,'a',encoding='utf-8')as f:
                f.write(new_line+'\n')
            f.close()


# 为granger_data_dir文件夹所有文件的所有序列,包含一阶差分序列,做格兰杰因果检验
# 该函数运行前需要先做单位根检验
def grangerTestDiffForFiles(granger_data_dir,unit_root_dir,granger_result_dir):
    filenames = os.listdir(granger_data_dir)
    id_filename = dict()
    id_list = []
    for filename in filenames:
        id_filename[int(filename.split('_')[0])] = filename
        id_list.append(int(filename.split('_')[0]))
    id_list = sorted(id_list)

    for id in id_list:
        filename = id_filename[id]

        stationary_metric_index = []
        stationary_rate_index = []
        churn_rate_stationaries = []
        metric_stationaries = dict()

        with open(unit_root_dir+'/'+filename,'r',encoding='utf-8')as f:
            name_list = f.readline().strip('\n').split(',')[:-1]
            stationarity_list = f.readline().strip('\n').split(',')[:-1]
            for i in range(1,len(name_list)-2):
                if stationarity_list[i]=='0' or stationarity_list[i]=='1':  # 对平稳序列和一阶差分序列进行因果检验
                    stationary_metric_index.append(i)
                    metric_stationaries[i] = stationarity_list[i]
            for i in range(len(name_list)-2,len(name_list)):
                churn_rate_stationaries.append(stationarity_list[i])
                if stationarity_list[i] == '0' or stationarity_list[i]=='1':
                    stationary_rate_index.append(i)
        with open(granger_result_dir+'/'+filename,'w',encoding='utf-8')as f:
            f.write(','+name_list[-2]+'_'+churn_rate_stationaries[0]+',churn_rate_pvalue,'+name_list[-1]+'_'
                    +churn_rate_stationaries[1]+',imp_churn_rate_pvalue,\n')
        f.close()
        for i in stationary_metric_index:
            new_line = name_list[i] + '_' + metric_stationaries[i] +','
            for j in stationary_rate_index:
                data_frame = pd.read_csv(granger_data_dir+'/'+filename, usecols=[i, j])

                var_ret = testVarLags(data_frame)
                if var_ret[0] <= 0:#############################
                    print('VAR estimation result is '+str(var_ret[0])+':',filename,name_list[i],name_list[j])
                    new_line += ',,'
                else:
                    used_lags = var_ret[0]
                    granger_ret = grangerCausalityTest(data_frame,used_lags,name_list[i],name_list[j])
                    if granger_ret[0] and granger_ret[1]:
                        granger_value = 'cause and effect'
                    elif granger_ret[0] and not granger_ret[1]:
                        granger_value = 'cause'
                    elif not granger_ret[0] and granger_ret[1]:
                        granger_value = 'effect'
                    else:
                        granger_value = 'none'
                    p_value = str(granger_ret[2][0]) + ' ' + str(granger_ret[3][0])
                    new_line += granger_value+','+p_value+','
            with open(granger_result_dir+'/'+filename,'a',encoding='utf-8')as f:
                f.write(new_line+'\n')
            f.close()


# 统计格兰杰因果分析结果
# mode: effect--流失率变化原因；cause--流失率变化结果；cause and effect--和流失率变化互为因果
def grangerResultSummary(granger_result_dir,save_filename,col_list,mode='effect'):
    id_list = []
    id_filenames = dict()
    filenames = os.listdir(granger_result_dir)
    for filename in filenames:
        id = int(filename.split('_')[0])
        id_list.append(id)
        id_filenames[id] = filename
    id_list = sorted(id_list)

    col_name = dict()
    col_name['repo_issue']='issue数量'
    col_name['repo_pull']='PR数量'
    col_name['repo_commit']='commit数量'
    col_name['repo_review']='review数量'
    col_name['repo_issue_comment']='issue comment数量'
    col_name['repo_commit_comment']='commit comment数量'
    col_name['repo_review_comment']='review comment数量'
    tmp_list0 = ['', 'thres_']
    tmp_list1 = ['', 'core_']
    tmp_list2 = ['mean','median']
    tmp_list3 = ['issue','pull','issue_pull']
    for item0 in tmp_list0:
        for item1 in tmp_list1:
            for item2 in tmp_list2:
                for item3 in tmp_list3:
                    col = item1 + item3 + '_time_'+ item0 + item2
                    name = ''
                    if item0 != '':
                        name += '（剔除极大值）'
                    name += item3.replace('_', '和')
                    if item1 != '':
                        name += '被内部人员'
                    name += '首次响应的时间的'

                    if item2 == 'mean':
                        name += '均值'
                    else:
                        name += '中位数'
                    col_name[col]=name
    for item1 in tmp_list1:
        for item3 in tmp_list3:
            col = item1 + item3 + '_response_rate'
            name = '平均每条'+item3.replace('_', '和')
            if item1 != '':
                name += '被内部人员'
            name += '响应的频率'
            col_name[col]=name
    for item3 in tmp_list3:
        col_name['open_'+item3+'_count']='open状态的'+item3.replace('_', '和')+'数量'
    for item2 in tmp_list2:
        for item3 in tmp_list3:
            col = 'open_' + item3 + '_age_' + item2
            name = 'open状态的'+item3.replace('_', '和')+'寿命的'
            if item2 == 'mean':
                name += '均值'
            else:
                name += '中位数'
            col_name[col] = name
    # for col in col_name.keys():
    #     print(col,':',col_name[col])

    col_id_list_1 = dict()  # 每一条指标对应的仓库，净流失率
    col_id_list_2 = dict()  # 每一条指标对应的仓库，重要开发者流失率
    for col in col_list:
        col_id_list_1[col]=[]
        col_id_list_2[col]=[]

    for id in id_list:
        filename = id_filenames[id]
        with open(granger_result_dir + '/' + filename,'r',encoding='utf-8')as f:
            f.readline()
            for line in f.readlines():
                col = line.split(',')[0]
                c1 = line.split(',')[1]
                if len(line.split(','))>3:
                    c2 = line.split(',')[3]
                else:
                    c2 = ''
                if c1 == 'cause and effect' or c1==mode:
                    col_id_list_1[col].append(id)
                if c2 == 'cause and effect' or c2==mode:
                    col_id_list_2[col].append(id)
    with open(save_filename,'w',encoding='utf-8-sig')as f:
        f.write('metric name,含义,churn_rate,imp_churn_rate,\n')
        for col in col_list:
            line = col+','+col_name[col]+','
            list1 = ''
            for id in col_id_list_1[col]:
                list1 += str(id) + '、'
            list2 = ''
            for id in col_id_list_2[col]:
                list2 += str(id) + '、'
            line += list1 + ',' + list2 + ','
            f.write(line+'\n')
    f.close()


    table = PrettyTable(['metric name','churn rate','imp churn rate'])
    for col in col_list:
        list1 = ''
        for id in col_id_list_1[col]:
            list1 += str(id) + ' '
        list2 = ''
        for id in col_id_list_2[col]:
            list2 += str(id) + ' '
        table.add_row([col,list1,list2])
    print(table)


# 统计格兰杰因果分析结果,包括一阶差分后稳定的序列
# mode: effect--流失率变化原因；cause--流失率变化结果；cause and effect--和流失率变化互为因果
def grangerDiffResultSummary(granger_result_dir,save_filename,col_list,mode='effect'):
    id_list = []
    id_filenames = dict()
    filenames = os.listdir(granger_result_dir)
    for filename in filenames:
        id = int(filename.split('_')[0])
        id_list.append(id)
        id_filenames[id] = filename
    id_list = sorted(id_list)

    col_name = dict()
    col_name['repo_issue']='issue数量'
    col_name['repo_pull']='PR数量'
    col_name['repo_commit']='commit数量'
    col_name['repo_review']='review数量'
    col_name['repo_issue_comment']='issue comment数量'
    col_name['repo_commit_comment']='commit comment数量'
    col_name['repo_review_comment']='review comment数量'
    tmp_list0 = ['', 'thres_']
    tmp_list1 = ['', 'core_']
    tmp_list2 = ['mean','median']
    tmp_list3 = ['issue','pull','issue_pull']
    for item0 in tmp_list0:
        for item1 in tmp_list1:
            for item2 in tmp_list2:
                for item3 in tmp_list3:
                    col = item1 + item3 + '_time_'+ item0 + item2
                    name = ''
                    if item0 != '':
                        name += '（剔除极大值）'
                    name += item3.replace('_', '和')
                    if item1 != '':
                        name += '被内部人员'
                    name += '首次响应的时间的'

                    if item2 == 'mean':
                        name += '均值'
                    else:
                        name += '中位数'
                    col_name[col]=name
    for item1 in tmp_list1:
        for item3 in tmp_list3:
            col = item1 + item3 + '_response_rate'
            name = '平均每条'+item3.replace('_', '和')
            if item1 != '':
                name += '被内部人员'
            name += '响应的频率'
            col_name[col]=name
    for item3 in tmp_list3:
        col_name['open_'+item3+'_count']='open状态的'+item3.replace('_', '和')+'数量'
    for item2 in tmp_list2:
        for item3 in tmp_list3:
            col = 'open_' + item3 + '_age_' + item2
            name = 'open状态的'+item3.replace('_', '和')+'寿命的'
            if item2 == 'mean':
                name += '均值'
            else:
                name += '中位数'
            col_name[col] = name
    # for col in col_name.keys():
    #     print(col,':',col_name[col])

    col_id_list_1 = dict()  # 每一条指标对应的仓库，净流失率
    col_id_list_2 = dict()  # 每一条指标对应的仓库，重要开发者流失率
    for col in col_list:
        col_id_list_1[col]=[]
        col_id_list_2[col]=[]

    for id in id_list:
        filename = id_filenames[id]
        with open(granger_result_dir + '/' + filename,'r',encoding='utf-8')as f:
            f.readline()
            for line in f.readlines():
                col = line.split(',')[0][0:-2]
                diff_order = (line.split(',')[0]).split('_')[-1]
                c1 = line.split(',')[1]
                if len(line.split(','))>3:
                    c2 = line.split(',')[3]
                else:
                    c2 = ''
                if diff_order == '1':
                    id_str = str(id)+'(1)'
                else:
                    id_str = str(id)
                if c1 == 'cause and effect' or c1==mode:
                    col_id_list_1[col].append(id_str)
                if c2 == 'cause and effect' or c2==mode:
                    col_id_list_2[col].append(id_str)
    with open(save_filename,'w',encoding='utf-8-sig')as f:
        f.write('metric name,含义,churn_rate,imp_churn_rate,\n')
        for col in col_list:
            line = col+','+col_name[col]+','
            list1 = ''
            for id in col_id_list_1[col]:
                list1 += id + '、'
            list2 = ''
            for id in col_id_list_2[col]:
                list2 += id + '、'
            line += list1 + ',' + list2 + ','
            f.write(line+'\n')
    f.close()


    table = PrettyTable(['metric name','churn rate','imp churn rate'])
    for col in col_list:
        list1 = ''
        for id in col_id_list_1[col]:
            list1 += str(id) + ' '
        list2 = ''
        for id in col_id_list_2[col]:
            list2 += str(id) + ' '
        table.add_row([col,list1,list2])
    print(table)


if __name__ == '__main__':
    time_sequence_dir = r'E:\bysj_project\time_sequence_28\time_sequence_data'
    user_dir = r'E:\bysj_project\repo_users_by_period\data_28'
    user_data_dir = 'E:/bysj_project/repo_user_data_by_period/data_28'
    threshold_dir = 'E:/bysj_project/repo_churner_classification'
    threshold_filename = threshold_dir + '/' + 'repo_churner_threshold.csv'

    # new metric data dir
    response_time_data_dir = r'E:\bysj_project\new_metrics\time_sequence_28\first_response_time_data'
    core_response_time_data_dir = r'E:\bysj_project\new_metrics\time_sequence_28\core_first_response_time_data'
    response_time_data_dir_thres = r'E:\bysj_project\new_metrics\time_sequence_28\with_threshold\first_response_time_data'
    core_response_time_data_dir_thres = r'E:\bysj_project\new_metrics\time_sequence_28\with_threshold\core_first_response_time_data'
    response_rate_data_dir = r'E:\bysj_project\new_metrics\time_sequence_28\response_rate_data'
    core_response_rate_data_dir = r'E:\bysj_project\new_metrics\time_sequence_28\core_response_rate_data'
    open_count_data_dir = r'E:\bysj_project\new_metrics\time_sequence_28\open_state_data'
    open_age_data_dir = r'E:\bysj_project\new_metrics\time_sequence_28\open_age_data'
    new_metric_first_line = 'issue_time_mean,pull_time_mean,issue_pull_time_mean,' \
                            'issue_time_median,pull_time_median,issue_pull_time_median,' \
                            'core_issue_time_mean,core_pull_time_mean,core_issue_pull_time_mean,' \
                            'core_issue_time_median,core_pull_time_median,core_issue_pull_time_median,' \
                            'issue_time_thres_mean,pull_time_thres_mean,issue_pull_time_thres_mean,' \
                            'issue_time_thres_median,pull_time_thres_median,issue_pull_time_thres_median,' \
                            'core_issue_time_thres_mean,core_pull_time_thres_mean,core_issue_pull_time_thres_mean,' \
                            'core_issue_time_thres_median,core_pull_time_thres_median,core_issue_pull_time_thres_median,' \
                            'issue_response_rate,pull_response_rate,issue_pull_response_rate,' \
                            'core_issue_response_rate,core_pull_response_rate,core_issue_pull_response_rate,' \
                            'open_issue_count,open_pull_count,open_issue_pull_count,' \
                            'open_issue_age_mean,open_pull_age_mean,open_issue_pull_age_mean,' \
                            'open_issue_age_median,open_pull_age_median,open_issue_pull_age_median,' \

    new_metric_dir_list = [
        response_time_data_dir,
        core_response_time_data_dir,
        response_time_data_dir_thres,
        core_response_time_data_dir_thres,
        response_rate_data_dir,
        core_response_rate_data_dir,
        open_count_data_dir,
        open_age_data_dir,
    ]


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

    granger_data_dir = 'E:/bysj_project/granger_causality_test/data_28'
    unit_root_dir = r'E:\bysj_project\granger_unit_root_result\data_28'
    granger_data_dir_2 = 'E:/bysj_project/granger_causality_test/data_28_start'  # 剔除初期数据后的
    unit_root_dir_2 = r'E:\bysj_project\granger_unit_root_result\data_28_start'
    granger_result_dir_2 = r'E:\bysj_project\granger_results\data_28_start'
    start_days_list = [
        200, 150, 150, 100, 100,
        100, 200, 100, 100, 200,
        250, 150, 150, 100, 200,
        200, 200, 100, 100, 100,
        100, 150, 150, 250, 250,
        150, 150, 200, 100, 100
    ]

    # 生成用于格兰杰因果分析的数据文件（初始数据）
    # saveGrangerDataForRepos(time_sequence_dir,user_dir,user_data_dir,granger_data_dir,new_metric_dir_list,
    #                         new_metric_first_line,threshold_filename,churn_limit_lists,28)

    # 生成剔除初期数据后的数据文件
    # saveGrangerDataWithoutStart(granger_data_dir, granger_data_dir_2, start_days_list, 28)

    # 生成流失率数据前移3个月（流失期限）后的数据
    ######################################

    # 为原序列做平稳性检验
    # testUnitRootForFiles(granger_data_dir_2,unit_root_dir_2)

    # 存储格兰杰检验结果
    # grangerTestForFiles(granger_data_dir_2,unit_root_dir_2,granger_result_dir_2)

    with open(granger_data_dir_2+'/2_Alluxio-alluxio-28.csv','r',encoding='utf-8')as f:
        col_list=f.readline().strip(',\n').split(',')[1:-2]

    summary_filename = r'E:\bysj_project\granger_results\churn_rate_cause_summary.csv'

    # grangerResultSummary(granger_result_dir_2,summary_filename,col_list)


    ###########################################以下是加入差分处理的操作###########################################
    granger_data_diff_dir_2 = r'E:\bysj_project\granger_causality_test\data_28_start_diff'
    unit_root_diff_dir_2 = r'E:\bysj_project\granger_unit_root_result\data_28_start_diff'
    granger_result_diff_dir_2 = r'E:\bysj_project\granger_results\data_28_start_diff'
    diff_summary_filename = r'E:\bysj_project\granger_results\churn_rate_cause_diff_summary.csv'

    # testUnitRootWithDiffForFiles(granger_data_dir_2,granger_data_diff_dir_2,unit_root_diff_dir_2)

    # grangerTestDiffForFiles(granger_data_diff_dir_2, unit_root_diff_dir_2, granger_result_diff_dir_2)

    # grangerDiffResultSummary(granger_result_diff_dir_2, diff_summary_filename, col_list)

    '''# 测试ADF检验
    test_filename = granger_data_dir_2 + '/' + '24_pycaret-pycaret-28.csv'#'2_Alluxio-alluxio-28.csv'#'13_interpretml-interpret-28.csv'
    x = []
    with open(test_filename,'r',encoding='utf-8')as f:
        f.readline()
        for line in f.readlines():
            if float(line.split(',')[1])<0:
                continue
            x.append(float(line.split(',')[1]))
    ret = adfTest(x,info_show=True)
    diff_order = 0
    diff_list = []
    print(x)
    while (ret[0] != 0):
        diff_order += 1
        diff_array = np.diff(np.array(x), diff_order)
        diff_list = []
        for k in range(diff_order):  # 补全差分序列的长度
            # diff_list.append(diff_array[k])
            diff_list.append(0)
        diff_list.extend(diff_array.tolist())
        print(len(x), len(diff_list))
        print(diff_list)
        ret = adfTest(diff_list,info_show=True)
    print(diff_order)
    print(ret)'''

    '''# 测试VAR滞后阶数和格兰杰因果检验
    test_filename = granger_data_dir_2 + '/' + '27_scikit-learn-scikit-learn-28.csv'
    row_index_dict = dict()
    row_index_dict['issue'] = 1
    row_index_dict['pull'] = 2
    row_index_dict['commit'] = 3
    row_index_dict['review'] = 4
    row_index_dict['issue_comment'] = 5
    row_index_dict['commit_comment'] = 6
    row_index_dict['review_comment'] = 7
    row_index_dict['churn_rate'] = 8
    row_index_dict['imp_churn_rate'] = 14
    x1_name='issue'
    x2_name='churn_rate'
    x1_index = row_index_dict[x1_name]
    x2_index = row_index_dict[x2_name]
    data_frame = pd.read_csv(test_filename, usecols=[x1_index, x2_index])
    used_lags = testVarLags(data_frame)[0]
    if used_lags!=-1:
        print(grangerCausalityTest(data_frame,used_lags,x1_name,x2_name))'''



