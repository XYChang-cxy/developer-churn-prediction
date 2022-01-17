import pandas as pd


def getMaxMinValues(file1, file2, except_id_list=None):
    if except_id_list is None:
        except_id_list = []
    max_val = 0
    min_val = 0
    csvFile = pd.read_csv(file1)
    for i in range(0, len(csvFile)):
        if str(int(csvFile.loc[i][0])) in except_id_list:
            continue
        for j in range(1, 13):
            if csvFile.loc[i][j] > max_val:
                max_val = csvFile.loc[i][j]
            if csvFile.loc[i][j] < min_val:
                min_val = csvFile.loc[i][j]
    csvFile = pd.read_csv(file2)
    for i in range(0, len(csvFile)):
        if str(int(csvFile.loc[i][0])) in except_id_list:
            continue
        for j in range(1, 13):
            if csvFile.loc[i][j] > max_val:
                max_val = csvFile.loc[i][j]
            if csvFile.loc[i][j] < min_val:
                min_val = csvFile.loc[i][j]
    return max_val, min_val


def saveMaxMinValues(file_name_list, use_except=True, except_id_list=None):
    if except_id_list is None:
        except_id_list = []
    with open("max_min_values.txt","w") as f:
        for name in file_name_list:
            if use_except==True:
                max_val,min_val=getMaxMinValues('churn_'+name+'.csv','loyal_'+name+'.csv',except_id_list=except_id_list)
            else:
                max_val, min_val = getMaxMinValues('churn_' + name + '.csv', 'loyal_' + name + '.csv')
            f.write(name+"\t" + str(max_val) + '\t' + str(min_val) + '\n')


if __name__ == '__main__':
    except_users = []
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
            except_users.append(csvFile.loc[i][0])
    print(except_users)
    print(len(except_users))

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
            except_users.append(csvFile.loc[i][0])
    print(except_users)
    print(len(except_users))

    file_name_list=['commits', 'issues', 'issue_comments', 'pulls', 'merged_pulls', #'reviews',
                 'review_comments', 'dcn_betweeness_normalized', 'dcn_weighted_degree']
    saveMaxMinValues(file_name_list,True,except_id_list=except_users)
