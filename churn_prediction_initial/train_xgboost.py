import numpy as np
from sklearn.metrics import accuracy_score,roc_auc_score,precision_score,recall_score,f1_score
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold, cross_val_score
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt
import matplotlib
import xgboost as xgb
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

    for item in all_data:
        if item[-1]<0:
            item[-1]=0

    data_np = np.array(all_data)
    id_list, x, y = np.split(data_np, indices_or_sections=(1, -1,), axis=1)

    train_data, test_data, train_label, test_label = train_test_split(x, y, random_state=1, train_size=0.8,
                                                                      test_size=0.2)
    train_label = np.array([x[0] for x in train_label], dtype=int)
    test_label = np.array([x[0] for x in test_label], dtype=int)

    # 以下是XGBoost特有操作
    # xgboost模型初始化设置
    dtrain = xgb.DMatrix(train_data, label=train_label)
    dtest = xgb.DMatrix(test_data)

    watchlist = [(dtrain, 'train')]

    other_params = {'eta': 0.3,
                    'n_estimators': 150,
                    'gamma': 0.15,
                    'max_depth': 3,
                    'min_child_weight': 3,
                    'colsample_bytree': 0.7,
                    'subsample': 0.9,
                    'reg_lambda': 4,
                    'reg_alpha': 1.2,
                    'seed': 33}

    cv_params = {'eta': np.logspace(-2, -0.5, 10)}
    classifier_model = xgb.XGBClassifier(**other_params)
    # verbose>1表示所有子模型都输出日志；refit=true程序交叉验证得到的最优参数；cv=5五折交叉验证；n_jobs=-1并行数和CPU核数一致
    '''gs = GridSearchCV(classifier_model, cv_params, scoring='f1', verbose=2, refit=True, cv=5, n_jobs=-1)
    gs.fit(train_data,train_label)
    # 性能测评
    print("参数的最佳取值：:", gs.best_params_)
    print("最佳模型得分:", gs.best_score_)'''
    classifier_model.fit(train_data,train_label)



    '''# booster:
    params = {'booster': 'gbtree',# 基分类器，决策树
              'objective': 'binary:logistic',#目标函数 二分类逻辑回归问题，输出为概率
              'eval_metric': 'auc',# 评估指标，auc，可以用列表设多个
              'max_depth': 3, #树最大深度，默认为6
              'lambda': 4, #L2正则化权重系数，默认为1
              'alpha':1.2, #L1正则化权重系数，默认为1
              'subsample': 0.9,#默认为1，用于训练的模型子样本占整个样本集和的比例
              'colsample_bytree': 0.7,#默认为1，建树时对特征的采样比例
              'min_child_weight': 3,#默认1，如果一个叶节点样本权重和小于该值则停止分裂
              'max_delta_step':0,#默认是0，限制每颗树权重改变的最大步长
              'eta': 0.3,# 收缩步长，默认0.3，防止过拟合
              'seed': 33,#初始化随机数种子
              'nthread': 8,#线程数量
              'gamma': 0.15,#分类叶节点需要的最大的loss reduction
              'learning_rate': 0.01,#每一次提升的学习率的列表
              }# 'n_estimators': 500, #弱学习器数量，即num_boost_round

    bst = xgb.train(params, dtrain, num_boost_round=50, evals=watchlist)'''

    '''ypred = bst.predict(dtrain)
    print(ypred)
    y_pred = (ypred >= 0.5) * 1'''
    ypred=y_pred = classifier_model.predict(train_data)
    print("训练集：")
    print('Precesion: %.4f' % precision_score(train_label, y_pred))
    print('Recall: %.4f' % recall_score(train_label, y_pred))
    print('F1-score: %.4f' % f1_score(train_label, y_pred))
    print('Accuracy: %.4f' % accuracy_score(train_label, y_pred))
    print('AUC: %.4f' % roc_auc_score(train_label, ypred))

    '''ypred = bst.predict(dtrain)
    print(ypred)
    # 设置阈值、评价指标
    y_pred = (ypred >= 0.5) * 1'''
    ypred=y_pred = classifier_model.predict(test_data)
    print("测试集：")
    print('Precesion: %.4f' % precision_score(test_label, y_pred))
    print('Recall: %.4f' % recall_score(test_label, y_pred))
    print('F1-score: %.4f' % f1_score(test_label, y_pred))
    print('Accuracy: %.4f' % accuracy_score(test_label, y_pred))
    print('AUC: %.4f' % roc_auc_score(test_label, ypred))

    # ypred = bst.predict(dtest)
    # print("测试集每个样本的得分\n", ypred)
    # ypred_leaf = bst.predict(dtest, pred_leaf=True)
    # print("测试集每棵树所属的节点数\n", ypred_leaf)
    # ypred_contribs = bst.predict(dtest, pred_contribs=True)
    # print("特征的重要性\n", ypred_contribs)
