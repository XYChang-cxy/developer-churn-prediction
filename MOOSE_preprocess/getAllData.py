import random
import numpy as np
import pandas as pd
import csv



# filename:保存的文件名
# max_min_file：存放最大最小值的文件路径
# file_name_list：考察的属性列表，即文件名列表
# step_num：取多少步，总的数据时间范围即step_length*step_num
# attr_num：考察的属性数目
# churn_num: 排除部分开发者后考虑的流失用户数
def saveModelData(churn_filename, loyal_filename, max_min_file, file_name_list, step_num, attr_num, churn_num, loyal_num, except_churn_index=None, except_loyal_index=None):
    if except_loyal_index is None:
        except_loyal_index = []
    if except_churn_index is None:
        except_churn_index = []
    max_min_val = dict()
    with open(max_min_file, 'r') as f:
        for line in f.readlines():
            list = line.strip('\n').split('\t')
            max_min_val.update({list[0]: [float(list[1]), float(list[2])]})
    churn_images = np.zeros((churn_num, step_num, attr_num))
    loyal_images = np.zeros((loyal_num, step_num, attr_num))
    churn_users = []
    loyal_users = []
    for i in range(attr_num):
        csvFile = pd.read_csv('churn_' + file_name_list[i] + '.csv')
        deno = max_min_val[file_name_list[i]][0] - max_min_val[file_name_list[i]][1]
        j = 0
        for index in range(csvFile.__len__()):
            if index not in except_churn_index: # 排除部分开发者
                churn_users.append(csvFile.loc[index][0])
                for k in range(step_num):
                    churn_images[j][k][i] = float(csvFile.loc[index][k + 1]) / deno
                j += 1
        if j!=churn_num:
            print("error: 012")

    for i in range(attr_num):
        csvFile = pd.read_csv('loyal_' + file_name_list[i] + '.csv')
        deno = max_min_val[file_name_list[i]][0] - max_min_val[file_name_list[i]][1]
        j = 0
        for index in range(csvFile.__len__()):
            if index not in except_loyal_index:  # 排除部分开发者
                loyal_users.append(csvFile.loc[index][0])
                for k in range(step_num):
                    loyal_images[j][k][i] = float(csvFile.loc[index][k + 1]) / deno
                j += 1
        if j!=loyal_num:
            print("error: 013")

    with open(churn_filename, "w", newline='') as csvFile:
        writer = csv.writer(csvFile)
        line=[]
        for i in range(step_num*attr_num+2):
            line.append(i)
        writer.writerow(line)
        for i in range(churn_num):
            line=[]
            line.append(churn_users[i])
            for j in range(step_num):
                for k in range(attr_num):
                    line.append(churn_images[i][j][k])
            line.append(1)
            writer.writerow(line)

    with open(loyal_filename, "w", newline='') as csvFile:
        writer = csv.writer(csvFile)
        line = []
        for i in range(step_num * attr_num + 2):
            line.append(i)
        writer.writerow(line)
        for i in range(loyal_num):
            line=[]
            line.append(loyal_users[i])
            for j in range(step_num):
                for k in range(attr_num):
                    line.append(loyal_images[i][j][k])
            line.append(-1)
            writer.writerow(line)


def getRandomIndex(num,ran):
    list = random.sample(range(0,ran),num)
    return list


# 获取训练、测试数据并返回
# 此处except_churn_index, except_loyal_index分别表示需要排除的开发者对应的index
# 注意此处的churn_num和loyal_num为排除一部分不考虑的开发者以后的数量
def getTrainData(churn_num,loyal_num,train_churn_num,train_loyal_num,except_churn_index, except_loyal_index):
    # churn_images = np.zeros((churn_num,12,9))
    # churn_labels = np.zeros((churn_num,2))
    # max_min_val = dict()
    # with open('data/max_min_values.txt', 'r') as f:
    #     for line in f.readlines():
    #         list = line.strip('\n').split('\t')
    #         max_min_val.update({list[0]: [float(list[1]), float(list[2])]})
    # for i in range(9):
    #     csvFile = pd.read_csv('data/churn_'+filenames[i]+'.csv')
    #     deno = max_min_val[filenames[i]][0]-max_min_val[filenames[i]][1]
    #     j=0
    #     for index in range(churn_num):
    #         for k in range(12):
    #             churn_images[j][k][i] = csvFile.loc[index][k+1]/deno
    #         j+=1
    train_num = train_churn_num + train_loyal_num

    train_labels = np.zeros(train_num)
    train_images = np.zeros((train_num, 12, 8))
    train_churn_images = np.zeros((train_churn_num, 12, 8))
    train_loyal_images = np.zeros((train_loyal_num, 12, 8))

    test_labels = np.zeros(churn_num+loyal_num-train_num)
    test_images = np.zeros((churn_num+loyal_num-train_num,12,8))
    test_churn_images = np.zeros((churn_num-train_churn_num, 12, 8))
    test_loyal_images = np.zeros((loyal_num-train_loyal_num, 12, 8))

    train_churn_index = getRandomIndex(train_churn_num, churn_num)
    train_loyal_index = getRandomIndex(train_loyal_num, loyal_num)
    filenames = ['commits', 'issues', 'issue_comments', 'pulls', 'merged_pulls', #'reviews',
                 'review_comments', 'dcn_betweeness_normalized', 'dcn_weighted_degree']

    max_min_val = dict()
    with open('data/max_min_values.txt', 'r') as f:
        for line in f.readlines():
            list = line.strip('\n').split('\t')
            max_min_val.update({list[0]: [float(list[1]), float(list[2])]})

    for i in range(8):
        csvFile = pd.read_csv('data/churn_' + filenames[i] + '.csv')
        file = []
        for l in range(csvFile.__len__()):
            if l not in except_churn_index:
                file.append(csvFile.loc[l])

        deno = max_min_val[filenames[i]][0] - max_min_val[filenames[i]][1]
        j = 0
        for index in train_churn_index:
            for k in range(12):
                train_churn_images[j][k][i] = file[index][k + 1] / deno # csvFile.loc[index][k + 1] / deno
            j += 1
        j = 0
        for index in range(churn_num):
            if index not in train_churn_index:
                for k in range(12):
                    test_churn_images[j][k][i] = file[index][k + 1] / deno # csvFile.loc[index][k + 1] / deno
                j += 1

    for i in range(8):
        csvFile = pd.read_csv('data/loyal_' + filenames[i] + '.csv')
        file = []
        for l in range(csvFile.__len__()):
            if l not in except_loyal_index:
                file.append(csvFile.loc[l])

        deno = max_min_val[filenames[i]][0] - max_min_val[filenames[i]][1]
        j = 0
        for index in train_loyal_index:
            for k in range(12):
                train_loyal_images[j][k][i] = file[index][k + 1] / deno # csvFile.loc[index][k + 1] / deno
            j += 1
        j = 0
        for index in range(loyal_num):
            if index not in train_loyal_index:
                for k in range(12):
                    test_loyal_images[j][k][i] = file[index][k + 1] / deno # csvFile.loc[index][k + 1] / deno
                j += 1

    random_train_loyal_index = sorted(getRandomIndex(train_loyal_num, train_num))  # 随机获取11个下标，用于随机插入忠诚用户数据
    p = 0
    q = 0
    # churn_label = np.zeros(2)
    # loyal_label = np.zeros(2)
    # churn_label[0] = 1
    # loyal_label[1] = 1
    for i in range(train_num):
        if i in random_train_loyal_index:
            train_images[i] = train_loyal_images[p]
            train_labels[i] = -1
            p += 1
        else:
            train_images[i] = train_churn_images[q]
            train_labels[i] = 1
            q += 1
    random_test_loyal_index = sorted(getRandomIndex(loyal_num-train_loyal_num, churn_num+loyal_num-train_num))
    p = 0
    q = 0
    for i in range(churn_num+loyal_num-train_num):
        if i in random_test_loyal_index:
            test_images[i]=test_loyal_images[p]
            test_labels[i] = -1
            p += 1
        else:
            test_images[i] = test_churn_images[q]
            test_labels[i] = 1
            q += 1
    train_data = np.zeros((train_num,96)) #展开成一维后的训练数据
    test_data = np.zeros((churn_num+loyal_num-train_num,96))
    for i in range(train_num):
        train_data[i]=train_images[i].ravel()
    for i in range(churn_num+loyal_num-train_num):
        test_data[i]=test_images[i].ravel()
    # print("train_num:",len(train_data),train_num)
    # for i in range(train_num):
    #     print(train_data[i],train_labels[i])
    # print("test_num:", len(test_data), churn_num+loyal_num-train_num)
    # for i in range(churn_num+loyal_num-train_num):
    #     print(test_data[i], test_labels[i])
    return train_data,train_labels,test_data,test_labels,train_images,test_images


if __name__=='__main__':
    churn_num = 224
    loyal_num = 317

    except_churn_users = []
    except_churn_index = []
    except_loyal_users = []
    except_loyal_index = []
    csvFile = pd.read_csv('churn_pulls.csv')
    csvFile1 = pd.read_csv('churn_commits.csv')
    csvFile2 = pd.read_csv('churn_issue_comments.csv')
    csvFile3 = pd.read_csv('churn_review_comments.csv')
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
            except_churn_users.append(csvFile.loc[i][0])
            except_churn_index.append(i)
    print(except_churn_users)
    print(len(except_churn_users))

    csvFile = pd.read_csv('loyal_pulls.csv')
    csvFile1 = pd.read_csv('loyal_commits.csv')
    csvFile2 = pd.read_csv('loyal_issue_comments.csv')
    csvFile3 = pd.read_csv('loyal_review_comments.csv')
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

    file_name_list = ['commits', 'issues', 'issue_comments', 'pulls', 'merged_pulls',  # 'reviews',
                      'review_comments', 'dcn_betweeness_normalized', 'dcn_weighted_degree']
    saveModelData("CHURN_DATA.csv","LOYAL_DATA.csv","max_min_values.txt",file_name_list,12,8,
                  churn_num,loyal_num,except_churn_index,except_loyal_index)

