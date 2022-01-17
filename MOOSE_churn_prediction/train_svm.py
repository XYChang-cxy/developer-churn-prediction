from sklearn import svm
import numpy as np
from sklearn.metrics import accuracy_score,roc_auc_score,precision_score,recall_score,f1_score,classification_report
from sklearn.model_selection import train_test_split,GridSearchCV
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import random


def getRandomIndex(num,ran):
    list = random.sample(range(0,ran),num)
    return list

if __name__ == '__main__':
    '''churn_num = 224
    loyal_num = 317

    except_churn_users = []
    except_churn_index = []
    except_loyal_users = []
    except_loyal_index = []
    csvFile = pd.read_csv('data/churn_pulls.csv')
    csvFile1 = pd.read_csv('data/churn_commits.csv')
    csvFile2 = pd.read_csv('data/churn_issue_comments.csv')
    csvFile3 = pd.read_csv('data/churn_review_comments.csv')
    for i in range(csvFile.__len__()):
        pr = 0
        cm = 0
        ic = 0
        rc = 0
        for j in range(1,13):
            pr += csvFile.loc[i][j]
            cm += csvFile1.loc[i][j]
            ic += csvFile2.loc[i][j]
            rc += csvFile3.loc[i][j]
        if pr ==0 and cm ==0 or ic+rc < 1:
            except_churn_users.append(csvFile.loc[i][0])
            except_churn_index.append(i)
    print(except_churn_users)
    print(len(except_churn_users))

    csvFile = pd.read_csv('data/loyal_pulls.csv')
    csvFile1 = pd.read_csv('data/loyal_commits.csv')
    csvFile2 = pd.read_csv('data/loyal_issue_comments.csv')
    csvFile3 = pd.read_csv('data/loyal_review_comments.csv')
    for i in range(csvFile.__len__()):
        pr = 0
        cm = 0
        ic = 0
        rc = 0
        for j in range(1, 13):
            pr += csvFile.loc[i][j]
            cm += csvFile1.loc[i][j]
            ic += csvFile2.loc[i][j]
            rc += csvFile3.loc[i][j]
        if pr == 0 and cm == 0 or ic + rc < 1:
            except_loyal_users.append(csvFile.loc[i][0])
            except_loyal_index.append(i)
    print(except_loyal_users)
    print(len(except_loyal_users))

    churn_num -= len(except_churn_users)
    loyal_num -= len(except_loyal_users)
    train_churn_num = int(churn_num * 0.8)
    train_loyal_num = int(loyal_num * 0.8)
    print('流失总数:',churn_num,'忠诚总数:',loyal_num,'训练集流失数:',train_churn_num,'训练集忠诚数:',train_loyal_num)###############
    train_data,train_label,test_data,test_label,train_images,test_images=getTrainData(churn_num,loyal_num,train_churn_num,train_loyal_num,except_churn_index,except_loyal_index)
    '''
    churn_num = 111
    loyal_num = 216
    churn_index_list = sorted(getRandomIndex(churn_num,churn_num+loyal_num))
    # print(churn_index_list)
    csvFile1 = pd.read_csv('data/CHURN_DATA.csv')
    csvFile2 = pd.read_csv('data/LOYAL_DATA.csv')
    all_data = []
    j=0
    k=0
    for i in range(churn_num+loyal_num):
        if i in churn_index_list:
            all_data.append(csvFile1.loc[j])
            j+=1
        else:
            all_data.append(csvFile2.loc[k])
            k+=1
    # print(j,k)
    # print(all_data)
    data_np=np.array(all_data)
    id_list,x,y=np.split(data_np,indices_or_sections=(1,-1,),axis=1)
    # print(x.shape,y.shape)
    train_data, test_data, train_label, test_label = train_test_split(x,y,random_state=1,train_size=0.8, test_size=0.2)

    train_label = np.array([x[0] for x in train_label], dtype=int)
    test_label = np.array([x[0] for x in test_label], dtype=int)
    # print(train_data.isnull().any())######################33
    #
    # train_null = pd.isnull(train_data)
    # train_null = train_data[train_null == True]
    # print(train_null)

    # classifier = svm.SVC(C=50, kernel='rbf',gamma=5, decision_function_shape='ovr')  # ovr:一对多策略
    classifier = svm.SVC(kernel='linear',C=1000)
    classifier.fit(train_data, train_label)

    train_pred = classifier.predict(train_data)
    test_pred = classifier.predict(test_data)

    print("训练集结果：")
    print("accuracy score:\t", accuracy_score(train_label, train_pred))
    # print("auroc:\t",roc_auc_score(train_label,train_pred))
    print("precision:\t", precision_score(train_label, train_pred))
    print("recall:\t", recall_score(train_label, train_pred))
    print("micro f1_score:\t", f1_score(train_label, train_pred))

    '''count = 0
    for i in range(len(train_pred)):
        if train_label[i] * train_pred[i]<0:
            print(i,train_label[i],train_pred[i])
            count += 1
    print(count)'''

    print("\n测试集结果：")
    print("accuracy score:\t", accuracy_score(test_label, test_pred))
    # print("auroc:\t", roc_auc_score(test_label,test_pred))
    print("precision:\t", precision_score(test_label, test_pred))
    print("recall:\t", recall_score(test_label, test_pred))
    print("micro f1_score:\t", f1_score(test_label, test_pred, average='micro'))

    '''count = 0
    for i in range(len(test_pred)):
        if test_label[i] * test_pred[i]<0:
            print(i,test_label[i],test_pred[i])
            count += 1
    print(count)'''

    '''tuned_parameters = [{'kernel': ['rbf'], 'gamma': [1e-4, 1e-3,0.01,0.1,1,5,10],
                         'C': [0.1, 1, 10, 50,100,300,500]},
                        {'kernel': ['linear'], 'C': [0.1, 1, 10, 50,100,300,500]}]
    scores = ['precision', 'recall']
    for score in scores:
        print("# Tuning hyper-parameters for %s" % score)
        print()

        # 调用 GridSearchCV，将 SVC(), tuned_parameters, cv=5, 还有 scoring 传递进去，
        clf = GridSearchCV(svm.SVC(), tuned_parameters, cv=5,
                           scoring='%s_macro' % score)
        # 用训练集训练这个学习器 clf
        clf.fit(train_data, train_label)

        print("Best parameters set found on development set:")
        print()

        # 再调用 clf.best_params_ 就能直接得到最好的参数搭配结果
        print(clf.best_params_)

        print()
        print("Grid scores on development set:")
        print()
        means = clf.cv_results_['mean_test_score']
        stds = clf.cv_results_['std_test_score']

        # 看一下具体的参数间不同数值的组合后得到的分数是多少
        for mean, std, params in zip(means, stds, clf.cv_results_['params']):
            print("%0.3f (+/-%0.03f) for %r"
                  % (mean, std * 2, params))

        print()

        print("Detailed classification report:")
        print()
        print("The model is trained on the full development set.")
        print("The scores are computed on the full evaluation set.")
        print()
        y_true, y_pred = test_label, clf.predict(test_data)

        # 打印在测试集上的预测结果与真实值的分数
        print(classification_report(y_true, y_pred))

        print()'''

