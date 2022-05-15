# 该文件用于将标准化处理后的整合数据进行SMOTE过采样，以达到平衡正负样本的目的
import numpy as np
import pandas as pd
import os
import random
from collections import Counter
from imblearn.over_sampling import SMOTE


def getRandomIndex(num,ran):
    list = random.sample(range(0,ran),num)
    return list


# 根据标准化后的正负样本的整合文件，获取SMOTE过采样后的数据
# period_length: 120或30
# overlap_ratio: 当user_type为loyaler时，获取数据时同一开发者不同区间的重叠度
def getBanlancedDataAndSave(normalized_data_dir,save_dir,period_length, overlap_ratio,data_type_list=None):
    if data_type_list is None:
        data_type_list = [
            'issue',
            'issue comment',
            'pull',
            'pull merged',
            'review',########
            'review comment',
            'commit',
            'betweeness',
            'weighted degree',
            'received issue comment',
            'received review',########
            'received review comment'
        ]
    if period_length == 120:
        col_count = 12*len(data_type_list)
    elif period_length == 30:
        col_count = 6*len(data_type_list)
    else:
        print('period length error!')
        return
    filename1 = normalized_data_dir+'\\'+'churner_integration-'+str(period_length)+'-'+str(overlap_ratio)+'.csv'
    filename2 = normalized_data_dir + '\\' + 'loyaler_integration-' + str(period_length) + '-' + str(
        overlap_ratio) + '.csv'

    content1 = pd.read_csv(filename1).iloc[:,:col_count+2]
    content2 = pd.read_csv(filename2).iloc[:,:col_count+2]

    all_zero_row_index = []
    for i in range(content2.shape[0]):
        if np.max(np.array(content2.iloc[i,1:]))==0.0:
            # print(i,'\n',content2.iloc[i],'\n')
            all_zero_row_index.append(i)
    print('Drop '+str(len(all_zero_row_index))+' all-zero rows in loyaler data.')

    content2.drop(all_zero_row_index,axis=0,inplace=True)  # inplace=True 在原数据上更改

    # 混合正负样本(未打乱顺序）
    all_data = content1.append(content2)
    all_data = np.array(all_data)

    # 划分特征和标签
    user_id_list,X,y = np.split(all_data,indices_or_sections=(1,-1,),axis=1)
    # 降维
    # user_id_list=np.array([x[0] for x in user_id_list], dtype=int)
    y = np.array([x[0] for x in y], dtype=int)

    smote = SMOTE(random_state=42)
    X_smote,y_smote = smote.fit_resample(X,y)

    output_df = pd.concat([pd.DataFrame(X_smote),pd.DataFrame(y_smote,columns=['label'])],axis=1)
    output_filename = save_dir+'\\balanced_data-'+str(period_length)+'-'+str(overlap_ratio)+'.csv'
    output_df.to_csv(output_filename)
    print(Counter(y),Counter(y_smote))


# if __name__ == '__main__':
#     getBanlancedDataAndSave(r'F:\MOOSE_cxy\developer_churn_prediction\churn_prediction\data_preprocess\data\repo_2\part_all\normalized_data',
#                              r'C:\Users\cxy\Desktop',30,0.0)