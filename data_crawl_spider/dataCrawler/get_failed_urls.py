import os

def writeUrls(lines,filename):
    urls_dir = '../dataCrawler/urls'
    with open(urls_dir+'/'+filename, 'w', encoding='utf-8')as f:
        for line in lines:
            f.write(line+'\n')
    f.close()


def getInfoUrls(dir,all_logs):
    pull_review_comment_urls = []
    pull_review_urls = []
    pull_detail_urls = []
    pull_urls = []
    user_urls = []
    issue_urls = []
    issue_comment_urls = []
    commit_urls = []
    commit_comment_urls = []
    fork_urls = []
    star_urls = []
    language_urls = []
    repo_indexes = []
    for filename in all_logs:
        with open(dir+'/'+filename,'r',encoding='utf-8') as f:
            for line in f.readlines():
                if line.find('https')==-1 and line.find('repo_index')==-1:
                    continue
                line_url = ''
                if line.find('https')!= -1:
                    line_url = line[line.find('https'):-1]
                print(line_url)
                if line.find('WARNING')!=-1 and line.find('404')!=-1:
                    if line.find('parse_issue ')!=-1:
                        issue_urls.append(line_url)
                    elif line.find('parse_pull')!=-1:
                        pull_urls.append(line_url)
                    elif line.find('parse_issue_comment') != -1:
                        issue_comment_urls.append(line_url)
                    elif line.find('parse_commit ') != -1:
                        commit_urls.append(line_url)
                    elif line.find('parse_commit_comment') != -1:
                        commit_comment_urls.append(line_url)
                    elif line.find('parse_fork') != -1:
                        fork_urls.append(line_url)
                    elif line.find('parse_star') != -1:
                        star_urls.append(line_url)
                    elif line.find('parse_user') != -1:
                        user_urls.append(line_url)
                elif line.find('token changed')!=-1:
                    if line.find('parse_user')!=-1:
                        user_urls.append(line_url)
                    elif line.find('parse_issue ')!=-1:
                        issue_urls.append(line_url)
                    elif line.find('parse_issue_comment') != -1:
                        issue_comment_urls.append(line_url)
                    elif line.find('parse_commit ') != -1:
                        commit_urls.append(line_url)
                    elif line.find('parse_commit_comment') != -1:
                        commit_comment_urls.append(line_url)
                    elif line.find('parse_fork') != -1:
                        fork_urls.append(line_url)
                    elif line.find('parse_star') != -1:
                        star_urls.append(line_url)
                    elif line.find('parse_pull') != -1:
                        if line_url.find('pulls?') != -1:
                            pull_urls.append(line_url)
                        elif line_url.find('/reviews') != -1:
                            pull_review_urls.append(line_url)
                        elif line_url.find('/comments') != -1:
                            pull_review_comment_urls.append(line_url)
                        else:
                            pull_detail_urls.append(line_url)
                    elif line.find('language')!=-1:
                        language_urls.append(line_url)
                    elif line.find('parse ')!=-1:
                        repo_indexes.append(line.strip('\n'))
    if len(pull_review_comment_urls)>0:
        writeUrls(pull_review_comment_urls,'info_review_comment.txt')
    if len(pull_review_urls)>0:
        writeUrls(pull_review_urls,'info_review.txt')
    if len(pull_detail_urls)>0:
        writeUrls(pull_detail_urls,'info_pull_detail.txt')
    if len(pull_urls)>0:
        writeUrls(pull_urls,'info_pull.txt')
    if len(user_urls)>0:
        writeUrls(user_urls,'info_user.txt')
    if len(issue_urls)>0:
        writeUrls(issue_urls,'info_issue.txt')
    if len(issue_comment_urls)>0:
        writeUrls(issue_comment_urls,'info_issue_comment.txt')
    if len(commit_urls)>0:
        writeUrls(commit_urls,'info_commit.txt')
    if len(fork_urls)>0:
        writeUrls(fork_urls,'info_fork.txt')
    if len(star_urls)>0:
        writeUrls(star_urls,'info_star.txt')
    if len(language_urls)>0:
        writeUrls(language_urls,'info_languages.txt')
    if len(repo_indexes)>0:
        writeUrls(repo_indexes,'info_repos.txt')


def getErrorUrls(dir,error_logs):
    pull_review_comment_urls = []
    pull_review_urls = []
    pull_detail_urls = []
    pull_urls = []
    user_urls = []
    issue_urls = []
    issue_comment_urls = []
    commit_urls = []
    commit_comment_urls = []
    fork_urls = []
    star_urls = []
    language_urls = []
    repo_indexes = []
    for filename in error_logs:
        with open(dir+'/'+filename,'r',encoding='utf-8') as f:
            for line in f.readlines():
                if line.find('https')==-1 and line.find('repo_index')==-1:
                    continue
                # if line.find('next_url')!=-1:
                #     continue
                line_url = ''
                if line.find('https')!= -1:
                    line_url = line[line.find('https'):-1]
                print(line_url)
                if line.find('parse_pull')!=-1:
                    if line_url.find('pulls?')!=-1:
                        pull_urls.append(line_url)
                    elif line_url.find('/reviews')!=-1:
                        pull_review_urls.append(line_url)
                    elif line_url.find('/comments')!=-1:
                        pull_review_comment_urls.append(line_url)
                    else:
                        pull_detail_urls.append(line_url)
                elif line.find('parse_issue[')!= -1:
                    issue_urls.append(line_url)
                elif line.find('parse_user')!= -1:
                    user_urls.append(line_url)
                elif line.find('parse_issue_comment')!= -1:
                    issue_comment_urls.append(line_url)
                elif line.find('parse_commit[')!= -1:
                    commit_urls.append(line_url)
                elif line.find('parse_commit_comment')!= -1:
                    commit_comment_urls.append(line_url)
                elif line.find('parse_fork')!= -1:
                    fork_urls.append(line_url)
                elif line.find('parse_star')!=-1:
                    star_urls.append(line_url)
                elif line.find('language') != -1:
                    language_urls.append(line_url)
                # elif line.find('repoMetadataItem')!=-1 or line.find('commit comments url')!=-1 or \
                #         line.find('stargazers url')!=-1:
                elif line.find('parse[')!=-1:
                    repo_indexes.append(line.strip('\n'))
    if len(pull_review_comment_urls)>0:
        writeUrls(pull_review_comment_urls,'error_review_comment.txt')
    if len(pull_review_urls)>0:
        writeUrls(pull_review_urls,'error_review.txt')
    if len(pull_detail_urls)>0:
        writeUrls(pull_detail_urls,'error_pull_detail.txt')
    if len(pull_urls)>0:
        writeUrls(pull_urls,'error_pull.txt')
    if len(user_urls)>0:
        writeUrls(user_urls,'error_user.txt')
    if len(issue_urls)>0:
        writeUrls(issue_urls,'error_issue.txt')
    if len(issue_comment_urls)>0:
        writeUrls(issue_comment_urls,'error_issue_comment.txt')
    if len(commit_urls)>0:
        writeUrls(commit_urls,'error_commit.txt')
    if len(fork_urls)>0:
        writeUrls(fork_urls,'error_fork.txt')
    if len(star_urls)>0:
        writeUrls(star_urls,'error_star.txt')
    if len(language_urls)>0:
        writeUrls(language_urls,'error_languages.txt')
    if len(repo_indexes)>0:
        writeUrls(repo_indexes,'error_repos.txt')


def main():
    dir = '../dataCrawler/logs'
    filenames = os.listdir(dir)
    all_logs = []
    error_logs = []
    for filename in filenames:
        if filename == 'all.log' or filename == 'error.log':
            continue
        elif filename.find('all')!=-1:
            all_logs.append(filename)
        elif filename.find('error')!=-1:
            error_logs.append(filename)
    if 'all.log' in filenames:
        all_logs.append('all.log')
    if 'error.log' in filenames:
        error_logs.append('error.log')
    getErrorUrls(dir,error_logs)
    getInfoUrls(dir,all_logs)


def duplicateElimination():
    url_dir = '../dataCrawler/urls'
    target_dir = '../dataCrawler/urls_simplified'
    filenames = os.listdir(url_dir)
    fileList = [
        'user.txt','issue.txt','issue_comment.txt','commit.txt','commit_comment.txt',
        'fork.txt','star.txt','languages.txt','repos.txt','pull.txt','pull_detail.txt',
        'review.txt','review_comment.txt'
    ]
    for i in range(len(fileList)):
        new_list = []
        if 'error_'+fileList[i] in filenames:
            with open(url_dir+'/error_'+fileList[i],'r',encoding='utf-8') as f:
                for line in f.readlines():
                    if line not in new_list:
                        new_list.append(line)
            f.close()
        if 'info_'+fileList[i] in filenames:
            with open(url_dir+'/info_'+fileList[i],'r',encoding='utf-8') as f:
                for line in f.readlines():
                    if line not in new_list:
                        new_list.append(line)
            f.close()
        if len(new_list)>0:
            # print(fileList[i])
            # for line in new_list:
            #     print(line,end='')
            with open(target_dir+'/'+fileList[i],'w',encoding='utf-8')as f:
                for line in new_list:
                    f.write(line)
            f.close()


if __name__ == '__main__':
    # main()
    duplicateElimination()