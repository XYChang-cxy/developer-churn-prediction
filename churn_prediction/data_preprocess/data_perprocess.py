import datetime
import numpy as np
import pandas as pd
import os
from churn_prediction.data_preprocess.database_connect import *
from churn_prediction.get_churn_limit import getChurnLimitLists,getChurnLimitListForRepo
from churn_prediction.data_preprocess.get_user import saveUserActivePeriod,getModelUserPeriod
from churn_prediction.data_preprocess.get_detailed_data import getCountDataAndSave,getDCNDataAndSave,getReceivedDataAndSave
from churn_prediction.data_preprocess.get_integrated_data import getIntegratedDataAndSave
from churn_prediction.data_preprocess.get_balanced_integrated_data import getSplitBanlancedDataAndSave


def main(id,continue_running=False):
    # id = 20
    period_length_list = [120, 30]  # 两种输入，一种是10天*12，一种是5天*6
    user_type_list = ['churner', 'loyaler']
    data_type_list = [
        'issue',
        'issue comment',
        'pull',
        'pull merged',
        # 'review',  ########gitee中没有review数据
        'review comment',
        # 'commit',
        'betweeness',
        'weighted degree',
        'received issue comment',
        # 'received review',  ########gitee中没有review数据
        'received review comment'
    ]

    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute('select created_at from churn_search_repos_final where id = '+str(id))
    create_time = cursor.fetchone()[0][0:10]
    end_time = '2022-01-01'

    # 所有用于训练的csv数据（含过程数据）文件都存在以下目录中
    data_dir = r'F:\MOOSE_cxy\developer_churn_prediction\churn_prediction\data_preprocess\new_data'

    print('**************************Data Preprocess**************************')
    print('\nStep1: make directories.')
    # ① 为目标仓库创建存储数据的文件夹
    part_all_dir = data_dir+'\\repo_'+str(id)+'\\part_all'
    part_1_dir = data_dir+'\\repo_'+str(id)+'\\part_1'
    part_2_dir = data_dir + '\\repo_' + str(id) + '\\part_2'
    if not os.path.exists(part_all_dir+'\\detailed_data'):
        os.makedirs(part_all_dir+'\\detailed_data')
    if not os.path.exists(part_all_dir+'\\normalized_data'):
        os.makedirs(part_all_dir+'\\normalized_data')
    # if not os.path.exists(part_all_dir+'\\balanced_data'):
    #     os.makedirs(part_all_dir+'\\balanced_data')
    if not os.path.exists(part_all_dir+'\\split_balanced_data'):
        os.makedirs(part_all_dir+'\\split_balanced_data')

    churn_limit_list = getChurnLimitListForRepo(id,create_time,end_time)
    '''if len(churn_limit_list)==2: # 分为两段
        if not os.path.exists(part_1_dir + '\\detailed_data'):
            os.makedirs(part_1_dir + '\\detailed_data')
        if not os.path.exists(part_1_dir + '\\normalized_data'):
            os.makedirs(part_1_dir + '\\normalized_data')
        # if not os.path.exists(part_1_dir + '\\balanced_data'):
        #     os.makedirs(part_1_dir + '\\balanced_data')
        if not os.path.exists(part_1_dir + '\\split_balanced_data'):
            os.makedirs(part_1_dir + '\\split_balanced_data')
        if not os.path.exists(part_2_dir + '\\detailed_data'):
            os.makedirs(part_2_dir + '\\detailed_data')
        if not os.path.exists(part_2_dir + '\\normalized_data'):
            os.makedirs(part_2_dir + '\\normalized_data')
        # if not os.path.exists(part_2_dir + '\\balanced_data'):
        #     os.makedirs(part_2_dir + '\\balanced_data')
        if not os.path.exists(part_2_dir + '\\split_balanced_data'):
            os.makedirs(part_2_dir + '\\split_balanced_data')'''

    if continue_running:
        s = 'Y'
    else:
        s = input('Step1 has finished, continue?[Y/n]')
    if s!='Y' and s!='y' and s!='':
        return
    print('\nStep2: get active period for all users.')
    # ② 获取所有流失用户和留存用户的连续活动时间（第一次活动和最后一次活动时间）
    # saveUserActivePeriod(id,create_time,end_time,part_all_dir)
    # '''if len(churn_limit_list)==2:
    #     saveUserActivePeriod(id,churn_limit_list[0][0],churn_limit_list[1][0],part_1_dir)
    #     saveUserActivePeriod(id,churn_limit_list[1][0],end_time,part_2_dir)'''
    #
    # if continue_running:
    #     s = 'Y'
    # else:
    #     s = input('Step2 has finished, continue?[Y/n]')
    # if s != 'Y' and s != 'y' and s != '':
    #     return
    # print('\nStep3: get users and correspond period for model training.')
    # # ③ 获取剔除不重要开发者（活动时间少于第90百分位数）后，分成churner和loyaler两部分，并生成重要开发者的取样区间
    # for period_length in period_length_list:
    #     for user_type in user_type_list:
    #         if user_type=='churner':
    #             overlap_ratio_list=[0.0]
    #         else:
    #             overlap_ratio_list = [0.0, 0.5]  # 两种取样重合度，表示同一(忠诚）开发者不同取样区间的重合度
    #         for overlap_ratio in overlap_ratio_list:
    #             getModelUserPeriod(id,user_type,part_all_dir,part_all_dir+'\\'+str(id)+'_user_active_period.csv',
    #                                period_length,overlap_ratio,time_threshold=-1)
    #             '''if len(churn_limit_list)==2:
    #                 getModelUserPeriod(id,user_type,part_1_dir,part_1_dir+'\\'+str(id)+'_user_active_period.csv',
    #                                    period_length,overlap_ratio,time_threshold=-1)
    #                 getModelUserPeriod(id, user_type, part_2_dir, part_2_dir + '\\' + str(id) + '_user_active_period.csv',
    #                                    period_length, overlap_ratio,time_threshold=-1)'''
    #
    # if continue_running:
    #     s = 'Y'
    # else:
    #     s = input('Step3 has finished, continue?[Y/n]')
    # if s != 'Y' and s != 'y' and s != '':
    #     return
    # print('\nStep4: get detailed sample data for model training.')
    # # ④ 根据选取的开发者和区域区间，获取样本详细数据，并存储到detailed_data文件夹
    # for period_length in period_length_list:
    #     for user_type in user_type_list:
    #         if user_type == 'churner':
    #             overlap_ratio_list = [0.0]
    #         else:
    #             overlap_ratio_list = [0.0, 0.5]
    #         for overlap_ratio in overlap_ratio_list:
    #             if user_type=='churner':
    #                 period_filename = 'repo_'+user_type+'s_period-'+str(period_length)+'.csv'
    #             else:
    #                 period_filename = 'repo_' + user_type + 's_period-' + str(period_length) + '-' + str(
    #                     overlap_ratio) + '.csv'
    #             for data_type in data_type_list:
    #                 if data_type=='betweeness' or data_type=='weighted degree':
    #                     getDCNDataAndSave(id,part_all_dir+'\\'+period_filename,period_length,data_type,
    #                                       part_all_dir+'\\detailed_data')
    #                 elif data_type.find('received')!=-1:
    #                     getReceivedDataAndSave(id,part_all_dir+'\\'+period_filename,period_length,data_type[9:],
    #                                            part_all_dir+'\\detailed_data')
    #                 else:
    #                     getCountDataAndSave(id,part_all_dir+'\\'+period_filename,period_length,data_type,
    #                                         part_all_dir+'\\detailed_data')
    #                 '''if len(churn_limit_list)==2:
    #                     if data_type == 'betweeness' or data_type == 'weighted degree':
    #                         getDCNDataAndSave(id, part_1_dir + '\\' + period_filename, period_length, data_type,
    #                                           part_1_dir + '\\detailed_data')
    #                     elif data_type.find('received') != -1:
    #                         getReceivedDataAndSave(id, part_1_dir + '\\' + period_filename, period_length, data_type[9:],
    #                                                part_1_dir + '\\detailed_data')
    #                     else:
    #                         getCountDataAndSave(id, part_1_dir + '\\' + period_filename, period_length, data_type,
    #                                             part_1_dir + '\\detailed_data')
    #                     if data_type == 'betweeness' or data_type == 'weighted degree':
    #                         getDCNDataAndSave(id, part_2_dir + '\\' + period_filename, period_length, data_type,
    #                                           part_2_dir + '\\detailed_data')
    #                     elif data_type.find('received') != -1:
    #                         getReceivedDataAndSave(id, part_2_dir + '\\' + period_filename, period_length, data_type[9:],
    #                                                part_2_dir + '\\detailed_data')
    #                     else:
    #                         getCountDataAndSave(id, part_2_dir + '\\' + period_filename, period_length, data_type,
    #                                             part_2_dir + '\\detailed_data')'''
    #
    # if continue_running:
    #     s = 'Y'
    # else:
    #     s = input('Step4 has finished, continue?[Y/n]')
    # if s != 'Y' and s != 'y' and s != '':
    #     return
    print('\nStep5: get integrated and normalized data.')
    # ⑤ 根据详细数据生成整合的标准化后的数据
    for period_length in period_length_list:
        for user_type in user_type_list:
            # if user_type == 'churner':
            #     overlap_ratio_list = [0.0]
            # else:
            #     overlap_ratio_list = [0.0, 0.5]
            overlap_ratio_list = [0.0, 0.5]  # 由于要标准化处理，所以churner数据存储时也要分开overlap_ratio
            for overlap_ratio in overlap_ratio_list:
                getIntegratedDataAndSave(part_all_dir+'\\detailed_data',part_all_dir+'\\normalized_data',
                                         user_type,period_length,overlap_ratio,data_type_list)
                '''if len(churn_limit_list)==2:
                    getIntegratedDataAndSave(part_1_dir + '\\detailed_data', part_1_dir + '\\normalized_data',
                                             user_type, period_length, overlap_ratio, data_type_list)
                    getIntegratedDataAndSave(part_2_dir + '\\detailed_data', part_2_dir + '\\normalized_data',
                                             user_type, period_length, overlap_ratio, data_type_list)'''

    if continue_running:
        s = 'Y'
    else:
        s = input('Step5 has finished, continue?[Y/n]')
    if s != 'Y' and s != 'y' and s != '':
        return
    print('\nStep6: get balanced data.')
    for period_length in period_length_list:
        overlap_ratio_list = [0.0, 0.5]
        for overlap_ratio in overlap_ratio_list:
            # getBanlancedDataAndSave(part_all_dir + '\\normalized_data', part_all_dir + '\\balanced_data',
            #                         period_length, overlap_ratio, data_type_list)
            # if len(churn_limit_list) == 2:
            #     getBanlancedDataAndSave(part_1_dir + '\\normalized_data', part_1_dir + '\\balanced_data',
            #                             period_length, overlap_ratio, data_type_list)
            #     getBanlancedDataAndSave(part_2_dir + '\\normalized_data', part_2_dir + '\\balanced_data',
            #                             period_length, overlap_ratio, data_type_list)
            getSplitBanlancedDataAndSave(part_all_dir + '\\normalized_data', part_all_dir + '\\split_balanced_data',
                                    period_length, overlap_ratio, data_type_list,1)
            '''if len(churn_limit_list) == 2:
                getSplitBanlancedDataAndSave(part_1_dir + '\\normalized_data', part_1_dir + '\\split_balanced_data',
                                        period_length, overlap_ratio, data_type_list,1)
                getSplitBanlancedDataAndSave(part_2_dir + '\\normalized_data', part_2_dir + '\\split_balanced_data',
                                        period_length, overlap_ratio, data_type_list,1)'''


    print('Data preprocessing finished.')


if __name__ == '__main__':
    id_list = [20]#2
    for id in id_list:
        main(id,False)