import pandas as pd


def getMaxMinValues(file1,file2):
    max_val = 0
    min_val = 0
    csvFile = pd.read_csv(file1)
    # print(csvFile.loc[1][0])
    for i in range(0, len(csvFile)):
        for j in range(1, 13):
            if csvFile.loc[i][j] > max_val:
                max_val = csvFile.loc[i][j]
            if csvFile.loc[i][j] < min_val:
                min_val = csvFile.loc[i][j]
    csvFile = pd.read_csv(file2)
    for i in range(0, len(csvFile)):
        for j in range(1, 13):
            if csvFile.loc[i][j] > max_val:
                max_val = csvFile.loc[i][j]
            if csvFile.loc[i][j] < min_val:
                min_val = csvFile.loc[i][j]
    return max_val, min_val


if __name__ == '__main__':
    with open("data/max_min_values.txt","w") as f:
        max_val, min_val = getMaxMinValues('data/churn_commits.csv', 'data/loyal_commits.csv')
        f.write("commits\t" + str(max_val) + '\t' + str(min_val)+'\n')
        max_val, min_val = getMaxMinValues('data/churn_issues.csv', 'data/loyal_issues.csv')
        f.write("issues\t" + str(max_val) + '\t' + str(min_val)+'\n')
        max_val, min_val = getMaxMinValues('data/churn_issue_comments.csv', 'data/loyal_issue_comments.csv')
        f.write("issue_comments\t" + str(max_val) + '\t' + str(min_val)+'\n')
        max_val, min_val = getMaxMinValues('data/churn_pulls.csv', 'data/loyal_pulls.csv')
        f.write("pulls\t" + str(max_val) + '\t' + str(min_val)+'\n')
        max_val, min_val = getMaxMinValues('data/churn_merged_pulls.csv', 'data/loyal_merged_pulls.csv')
        f.write("merged_pulls\t" + str(max_val) + '\t' + str(min_val)+'\n')
        max_val, min_val = getMaxMinValues('data/churn_reviews.csv', 'data/loyal_reviews.csv')
        f.write("reviews\t" + str(max_val) + '\t' + str(min_val) + '\n')
        max_val, min_val = getMaxMinValues('data/churn_review_comments.csv', 'data/loyal_review_comments.csv')
        f.write("review_comments\t" + str(max_val) + '\t' + str(min_val) + '\n')
        max_val, min_val = getMaxMinValues('data/churn_dcn_betweeness_normalized.csv',
                                           'data/loyal_dcn_betweeness_normalized.csv')
        f.write("dcn_betweeness_normalized\t" + str(max_val) + '\t' + str(min_val) + '\n')
        max_val, min_val = getMaxMinValues('data/churn_dcn_betweeness.csv','data/loyal_dcn_betweeness.csv')
        f.write("dcn_betweeness\t" + str(max_val) + '\t' + str(min_val) + '\n')
        max_val, min_val = getMaxMinValues('data/churn_dcn_weighted_degree.csv', 'data/loyal_dcn_weighted_degree.csv')
        f.write("dcn_weighted_degree\t" + str(max_val) + '\t' + str(min_val) + '\n')
        max_val, min_val = getMaxMinValues('data/churn_dcn_degrees.csv', 'data/loyal_dcn_degrees.csv')
        f.write("dcn_degree\t" + str(max_val) + '\t' + str(min_val) + '\n')