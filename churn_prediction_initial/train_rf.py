import numpy as np
from sklearn.metrics import accuracy_score,roc_auc_score,precision_score,recall_score,f1_score
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import random

def getRandomIndex(num,ran):
    list = random.sample(range(0,ran),num)
    return list

if __name__ == '__main__':
    churn_num = 111
    loyal_num = 216
    churn_index_list = sorted(getRandomIndex(churn_num, churn_num + loyal_num))
    csvFile1 = pd.read_csv('data/CHURN_DATA.csv')
    csvFile2 = pd.read_csv('data/LOYAL_DATA.csv')
    all_data = []
    j = 0
    k = 0
    for i in range(churn_num + loyal_num):
        if i in churn_index_list:
            all_data.append(csvFile1.loc[j])
            j += 1
        else:
            all_data.append(csvFile2.loc[k])
            k += 1

    # for item in all_data:
    #     if item[-1]<0:
    #         item[-1]=0

    data_np = np.array(all_data)
    id_list, x, y = np.split(data_np, indices_or_sections=(1, -1,), axis=1)

    train_data, test_data, train_label, test_label = train_test_split(x, y, random_state=1, train_size=0.8,
                                                                      test_size=0.2)
    train_label = np.array(train_label, dtype=int)
    test_label = np.array(test_label, dtype=int)

    model = RandomForestClassifier(n_estimators=250,
                                   bootstrap=True,
                                   max_features='sqrt')#分裂时最多考虑根号（n_features)个（可以有效分裂的）特征，从中选最优
    model.fit(train_data, train_label)

    y_pred = model.predict(train_data)
    print("训练集：")
    print('Precesion: %.4f' % precision_score(train_label, y_pred))
    print('Recall: %.4f' % recall_score(train_label, y_pred))
    print('F1-score: %.4f' % f1_score(train_label, y_pred))
    print('Accuracy: %.4f' % accuracy_score(train_label, y_pred))
    print('AUC: %.4f' % roc_auc_score(train_label, y_pred))

    y_pred = model.predict(test_data)
    print("测试集：")
    print('Precesion: %.4f' % precision_score(test_label, y_pred))
    print('Recall: %.4f' % recall_score(test_label, y_pred))
    print('F1-score: %.4f' % f1_score(test_label, y_pred))
    print('Accuracy: %.4f' % accuracy_score(test_label, y_pred))
    print('AUC: %.4f' % roc_auc_score(test_label, y_pred))


