import numpy as np
from sklearn.metrics import accuracy_score,roc_auc_score,precision_score,recall_score,f1_score
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt
import matplotlib
from sklearn.tree import DecisionTreeClassifier
import pandas as pd
import random


def getRandomIndex(num,ran):
    list = random.sample(range(0,ran),num)
    return list

# https://zhuanlan.zhihu.com/p/59121403
def my_adaboost_clf(X_train, Y_train, X_test, Y_test, num_boost_round=300, weak_clf=DecisionTreeClassifier(max_depth = 1,random_state=1)):
    n_train, n_test = len(X_train), len(X_test)
    # Initialize weights
    w = np.ones(n_train) / n_train
    pred_train, pred_test = [np.zeros(n_train), np.zeros(n_test)]

    for i in range(num_boost_round):
        # Fit a classifier with the specific weights
        weak_clf.fit(X_train, Y_train, sample_weight = w)
        pred_train_i = weak_clf.predict(X_train)
        pred_test_i = weak_clf.predict(X_test)

        # Indicator function
        miss = [int(x) for x in (pred_train_i != Y_train)]
        print("weak_clf_%02d train acc: %.4f"
         % (i + 1, 1 - sum(miss) / n_train))

        # Error,分类误差率，矩阵乘法
        err_m = np.dot(w, miss)
        # Alpha,最终集成使用的的基学习器的权重，误差率小的基学习器拥有较大的权值，误差率大的基学习器拥有较小的权值。
        alpha_m = 0.5 * np.log((1 - err_m) / float(err_m))
        # New weights
        miss2 = [x if x==1 else -1 for x in miss] # -1 * y_i * G(x_i): 1 / -1
        w = np.multiply(w, np.exp([float(x) * alpha_m for x in miss2])) #对应元素相乘
        w = w / sum(w)

        # Add to prediction，所有弱分类器结果加权求和
        pred_train_i = [1 if x == 1 else -1 for x in pred_train_i]
        pred_test_i = [1 if x == 1 else -1 for x in pred_test_i]
        pred_train = pred_train + np.multiply(alpha_m, pred_train_i)
        pred_test = pred_test + np.multiply(alpha_m, pred_test_i)

    pred_train = [1 if x > 0 else -1 for x in pred_train]
    pred_test = [1 if x > 0 else -1 for x in pred_test]
    return pred_train,pred_test
    # print("My AdaBoost clf train accuracy: %.4f" % (sum(pred_train == Y_train) / n_train))
    # print("My AdaBoost clf test accuracy: %.4f" % (sum(pred_test == Y_test) / n_test))


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

    data_np = np.array(all_data)
    id_list, x, y = np.split(data_np, indices_or_sections=(1, -1,), axis=1)

    train_data, test_data, train_label, test_label = train_test_split(x, y, random_state=1, train_size=0.8,
                                                                      test_size=0.2)
    # 降低一个维度，比如（261，1）变为（261，），同时修改数据类型
    train_label = np.array([x[0] for x in train_label],dtype=int)
    test_label = np.array([x[0] for x in test_label], dtype=int)

    train_pred,test_pred = my_adaboost_clf(train_data,train_label,test_data,test_label,
                                           num_boost_round=100,
                                           weak_clf=DecisionTreeClassifier(
                                               criterion='gini',max_depth = 1,
                                               random_state=1))

    print("训练集：")
    print('Precesion: %.4f' % precision_score(train_label, train_pred))
    print('Recall: %.4f' % recall_score(train_label, train_pred))
    print('F1-score: %.4f' % f1_score(train_label, train_pred))
    print('Accuracy: %.4f' % accuracy_score(train_label, train_pred))
    print('AUC: %.4f' % roc_auc_score(train_label, train_pred))

    print("测试集：")
    print('Precesion: %.4f' % precision_score(test_label, test_pred))
    print('Recall: %.4f' % recall_score(test_label, test_pred))
    print('F1-score: %.4f' % f1_score(test_label, test_pred))
    print('Accuracy: %.4f' % accuracy_score(test_label, test_pred))
    print('AUC: %.4f' % roc_auc_score(test_label, test_pred))

