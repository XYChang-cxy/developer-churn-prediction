import scrapy
import pymysql
from data_crawl_spider.dataCrawler.additionSpider.additionSpider import settings
from data_crawl_spider.dataCrawler.additionSpider.additionSpider.spiders.request_header import *
from data_crawl_spider.dataCrawler.additionSpider.additionSpider.items import *
import datetime
import re
import logging
import logging.handlers
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os

requests.packages.urllib3.disable_warnings() #request忽略http验证(verify=False)时消除警告
requests.adapters.DEFAULT_RETRIES = 5 #默认重试次数


def dbHandle():
    conn = pymysql.connect(
        host=settings.MYSQL_HOST,
        db=settings.MYSQL_DBNAME,
        user=settings.MYSQL_USER,
        passwd=settings.MYSQL_PASSWD,
        charset='utf8',
        use_unicode=True
    )
    return conn


class GithubAdditionSpider(scrapy.Spider):
    name = 'GitHub_addition'
    allowed_domains = ['api.github.com']

    skip_http_status_list = [401, 404, 500]  # 如果某个仓库主信息api获取失败，则跳过这一仓库
    page_loss_status_list = [404]  # 缺页情况，需要手动查找下一页
    token_overtime_status_list = [403]  # token每小时访问次数5000已用完,API rate limit exceeded for user ID xxxxxxxx
    token_index = 0

    proxy = '218.203.132.117:808'  ###??????
    proxies = {
        'http': 'http://175.4.68.43:8118',
        'https': 'https://218.203.132.117:808',
    }

    # 日志
    logger = logging.getLogger('mylogger')
    logger.setLevel(logging.DEBUG)
    all_handler = logging.handlers.TimedRotatingFileHandler('../additionSpider/spiderLogs/additional_all.log', when='H', interval=5, backupCount=30)
    all_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"))
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter("%(asctime)s \t %(levelname)s \t %(funcName)s \t %(message)s"))
    # error_handler = logging.FileHandler('../logs/error.log')
    error_handler = logging.handlers.TimedRotatingFileHandler('../additionSpider/spiderLogs/additional_error.log', when='H', interval=24,
                                                              backupCount=30)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(funcName)s[:%(lineno)d] - %(message)s"))
    logger.addHandler(all_handler)
    logger.addHandler(stream_handler)
    logger.addHandler(error_handler)

    # 在本spider中没用，但必须保证范围足够大
    start_time = '2000-01-01 00:00:00'
    end_time = '2022-01-01 23:59:59'

    fmt_GitHub = '%Y-%m-%dT%H:%M:%SZ'
    fmt_MySQL = '%Y-%m-%d %H:%M:%S'
    null_time = '1000-01-01 00:00:00'
    start_time = datetime.datetime.strptime(start_time, fmt_MySQL)
    end_time = datetime.datetime.strptime(end_time, fmt_MySQL)

    fileList = [
        'issue.txt',
        'issue_comment.txt',
        'pull.txt',
        'commit.txt',
        'commit_comment.txt',
        'fork.txt',
        'star.txt',
        'user.txt',
        'pull_detail.txt',
        'review.txt',
        'review_comment.txt'
        # 'languages.txt',
        # 'repos.txt',
    ]
    start_urls = ["https://api.github.com/users/XYChang-cxy"]
    scrapy_lists = []
    scrapy_indexes = []
    platform = 'GitHub'


    def __init__(self, repo=None, *args, **kwargs):
        super(GithubAdditionSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if response.status == 401:
            print(get_html_json(self.start_urls[0],getGitHubHeader(self.token_index),verify=False)[0])
            print(json.loads(response.body.decode('utf-8')))
            yield scrapy.Request(self.start_urls[0],callback=self.parse, dont_filter=True,
                                     headers=getGitHubHeader(self.token_index))
        else:
            dir_name = 'F:/MOOSE_cxy/developer_churn_prediction/data_crawl_spider/dataCrawler/urls_simplified'
            filenames = os.listdir(dir_name)
            for i in range(len(self.fileList)):
                if i < 9:
                    new_list = []
                    if self.fileList[i] in filenames:
                        with open(dir_name + '/' + self.fileList[i], 'r', encoding='utf-8')as f:
                            for line in f.readlines():
                                new_list.append(line.strip('\n'))
                    self.scrapy_lists.append(new_list)
                    self.scrapy_indexes.append(0)
                else:
                    if self.fileList[i] in filenames:
                        with open(dir_name + '/' + self.fileList[i], 'r', encoding='utf-8')as f:
                            for line in f.readlines():
                                if i == 9:
                                    self.scrapy_lists[8].append(line.strip('/reviews\n'))
                                elif i == 10:
                                    self.scrapy_lists[8].append(line.strip('/comments\n'))

            funcList = [
                self.parse_issue,
                self.parse_issue_comment,
                self.parse_pull,
                self.parse_commit,
                self.parse_commit_comment,
                self.parse_fork,
                self.parse_star,
                self.parse_user,
                self.parse_pull_detail
            ]
            for i in range(len(funcList)):
                if len(self.scrapy_lists[i])>0:
                    if i == len(funcList) - 2:
                        repo_id = 0
                    else:
                        repo_id = int(self.scrapy_lists[i][0].split('/')[4])
                    yield scrapy.Request(self.scrapy_lists[i][0],
                                         meta={"repo_id": repo_id, "platform": self.platform,
                                               "current_url": self.scrapy_lists[i][0]},
                                         callback=funcList[i], dont_filter=True,
                                         headers=getGitHubHeader(self.token_index))


    def parse_issue(self, response):
        repos_data = json.loads(response.body.decode('utf-8'))
        repos_header = response.headers
        repo_id = response.meta['repo_id']
        platform = response.meta['platform']
        current_url = response.meta['current_url']
        self.logger.debug(current_url)
        if response.status in self.page_loss_status_list: # page loss in this API
            self.logger.warning('404: page lost! -- '+ current_url)
        elif response.status in self.token_overtime_status_list: # github token is overtime and can be used after an hour
            self.token_index = (self.token_index + 1) % GitHub_token_number
            self.logger.info('github token changed: token_index = ' + str(self.token_index) + ' -- ' +current_url)
            yield scrapy.Request(current_url,
                                 meta={"repo_id": repo_id, "platform": platform,"current_url":current_url},
                                 callback=self.parse_issue, dont_filter=True,
                                 headers=getGitHubHeader(self.token_index))
        else:   # normal situation
            try:
                page_start_time = datetime.datetime.strptime(repos_data[-1]['created_at'], self.fmt_GitHub)
                page_end_time = datetime.datetime.strptime(repos_data[0]['created_at'], self.fmt_GitHub)
            except BaseException as e:
                self.logger.error('page start/end time error! -- '+current_url)
                page_start_time = datetime.datetime.now()
                page_end_time = datetime.datetime.now()
            if page_end_time < page_start_time: # 页面数据排序错误
                self.logger.error('data order error! -- '+current_url)
            elif page_end_time < self.start_time: # 已经爬完所需时间段的数据
                self.logger.info('page time before period: ' + str(page_end_time) + ' < ' + str(self.start_time))
            else:
                if page_start_time > self.end_time: # 还没遍历到所需的时间段
                    self.logger.info('page time after period: '+str(page_start_time) + ' > ' + str(self.end_time))
                else:
                    for repos_per_data in repos_data:
                        try:
                            issue_id = repos_per_data['id']
                            issue_number = repos_per_data['number']
                            create_time = datetime.datetime.strptime(repos_per_data['created_at'], self.fmt_GitHub)
                            if create_time > self.end_time: #还没到所需时间段的数据
                                continue
                            if create_time < self.start_time: # 爬完所需时间段的数据
                                break
                            create_time = create_time.strftime(self.fmt_MySQL)
                            update_time = datetime.datetime.strptime(repos_per_data['updated_at'], self.fmt_GitHub).strftime(self.fmt_MySQL)
                            if repos_per_data['closed_at'] is None:
                                close_time = self.null_time
                            else:
                                close_time = datetime.datetime.strptime(repos_per_data['closed_at'], self.fmt_GitHub).strftime(self.fmt_MySQL)
                            if repos_per_data['locked']=='true':
                                is_locked_issue = 1
                            else:
                                is_locked_issue = 0
                            issue_state = repos_per_data['state']
                            if issue_state is None:
                                issue_state = ''
                            issue_comment_count = repos_per_data['comments']
                            if repos_per_data['user'] is None:
                                user_id = 0
                            else:
                                user_id = repos_per_data['user']['id']
                            author_association = repos_per_data['author_association']
                            if author_association is None:
                                author_association = ''
                            if author_association == 'MEMBER' or author_association == 'COLLABORATOR':
                                is_core_issue = 1
                            else:
                                is_core_issue = 0
                            labels = repos_per_data['labels']
                            issue_labels = ''
                            if labels is not None and len(labels)>0:
                                for per_label in labels:
                                    issue_labels += per_label['name']+','
                            issue_title = repos_per_data['title']
                            if issue_title is None:
                                issue_title = ''
                            issue_body = repos_per_data['body']
                            if issue_body is None:
                                issue_body = ''
                            if issue_state == 'closed':
                                repoIssueClosedItem = RepoIssueClosedItem()
                                try:
                                    repoIssueClosedItem['repo_id'] = repo_id
                                    repoIssueClosedItem['issue_id'] = issue_id
                                    repoIssueClosedItem['platform'] = platform
                                    repoIssueClosedItem['create_time'] = create_time
                                    repoIssueClosedItem['close_time'] = close_time
                                    repoIssueClosedItem['user_id'] = user_id
                                except BaseException as e:
                                    self.logger.error('repoIssueClosedItem error! -- '+current_url)
                                yield repoIssueClosedItem

                            repoIssueItem = RepoIssueItem()
                            try:
                                repoIssueItem['repo_id'] = repo_id
                                repoIssueItem['platform'] = platform
                                repoIssueItem['issue_id'] = issue_id
                                repoIssueItem['issue_number'] = issue_number
                                repoIssueItem['create_time'] = create_time
                                repoIssueItem['update_time'] = update_time
                                repoIssueItem['close_time'] = close_time
                                repoIssueItem['is_core_issue'] = is_core_issue
                                repoIssueItem['is_locked_issue'] = is_locked_issue
                                repoIssueItem['issue_state'] = issue_state
                                repoIssueItem['issue_comment_count'] = issue_comment_count
                                repoIssueItem['user_id'] = user_id
                                repoIssueItem['author_association'] = author_association
                            except BaseException as e:
                                self.logger.error('repoIssueItem error! -- ' + current_url)
                            yield repoIssueItem

                            repoIssueExtendItem = RepoIssueExtendItem()
                            try:
                                repoIssueExtendItem['repo_id'] = repo_id
                                repoIssueExtendItem['issue_id'] = issue_id
                                repoIssueExtendItem['platform'] = platform
                                repoIssueExtendItem['issue_labels'] = issue_labels
                                repoIssueExtendItem['issue_title'] = issue_title
                                repoIssueExtendItem['issue_body'] = issue_body
                            except BaseException as e:
                                self.logger.error('repoIssueExtendItem error! -- ' + current_url)
                            yield repoIssueExtendItem
                        except BaseException as e:
                            self.logger.critical('repo issue crawl error! -- ' + current_url)
                            self.logger.critical(e)

        func_index = 0
        self.scrapy_indexes[func_index]+=1
        if self.scrapy_indexes[func_index]<len(self.scrapy_lists[func_index]):
            new_repo_id = int(self.scrapy_lists[func_index][self.scrapy_indexes[func_index]].split('/')[4])
            yield scrapy.Request(self.scrapy_lists[func_index][self.scrapy_indexes[func_index]],
                                     meta={"repo_id": new_repo_id, "platform": self.platform,
                                           "current_url": self.scrapy_lists[func_index][self.scrapy_indexes[func_index]]},
                                     callback=self.parse_issue, dont_filter=True,
                                     headers=getGitHubHeader(self.token_index))


    def parse_issue_comment(self,response):
        repos_data = json.loads(response.body.decode('utf-8'))
        repos_header = response.headers
        repo_id = response.meta['repo_id']
        platform = response.meta['platform']
        current_url = response.meta['current_url']
        self.logger.debug(current_url)
        if response.status in self.page_loss_status_list:
            self.logger.warning('404: page lost! -- ' + current_url)
        elif response.status in self.token_overtime_status_list:
            self.token_index = (self.token_index + 1) % GitHub_token_number
            self.logger.info('github token changed: token_index = ' + str(self.token_index) + ' -- ' +current_url)
            yield scrapy.Request(current_url,
                                 meta={"repo_id": repo_id, "platform": platform,
                                       "current_url": current_url},
                                 callback=self.parse_issue_comment, dont_filter=True,
                                 headers=getGitHubHeader(self.token_index))
        else:
            sid= SentimentIntensityAnalyzer()
            try:
                page_start_time = datetime.datetime.strptime(repos_data[-1]['created_at'], self.fmt_GitHub)
                page_end_time = datetime.datetime.strptime(repos_data[0]['created_at'], self.fmt_GitHub)
            except BaseException as e:
                self.logger.error('page start/end time error! -- ' + current_url)
                page_start_time = datetime.datetime.now()
                page_end_time = datetime.datetime.now()
            if page_end_time < page_start_time:  # 页面数据排序错误
                self.logger.error('data order error! -- ' + current_url)
            elif page_end_time < self.start_time:  # 已经爬完所需时间段的数据
                self.logger.info('page time before period: ' + str(page_end_time) + ' < ' + str(self.start_time))
            else:
                if page_start_time > self.end_time:  # 还没遍历到所需的时间段
                    self.logger.info('page time after period: ' + str(page_start_time) + ' > ' + str(self.end_time))
                else:
                    for repos_per_data in repos_data:
                        try:
                            issue_number = int(repos_per_data['issue_url'].split('/')[-1])
                            issue_comment_id = repos_per_data['id']
                            create_time = datetime.datetime.strptime(repos_per_data['created_at'], self.fmt_GitHub)
                            if create_time > self.end_time: #还没到所需时间段的数据
                                continue
                            if create_time < self.start_time: # 爬完所需时间段的数据
                                break
                            create_time = create_time.strftime(self.fmt_MySQL)
                            update_time = datetime.datetime.strptime(repos_per_data['updated_at'], self.fmt_GitHub).strftime(self.fmt_MySQL)
                            if repos_per_data['user'] is None:
                                user_id = 0
                                # user_url = ''
                            else:
                                user_id = repos_per_data['user']['id']
                                # user_url = repos_per_data['user']['url']
                            author_association = repos_per_data['author_association']
                            if author_association is None:
                                author_association = ''
                            if author_association == 'MEMBER' or author_association == 'COLLABORATOR':
                                is_core_issue_comment = 1
                            else:
                                is_core_issue_comment = 0
                            issue_comment_body = repos_per_data['body']
                            if issue_comment_body is None:
                                issue_comment_body = ''
                            # 分析body的极性
                            label = sid.polarity_scores(issue_comment_body)['compound']
                            if label >= 0.3:
                                polarity = 'positive'
                            elif label <= -0.3:
                                polarity = 'negative'
                            else:
                                polarity = 'neutral'

                            repoIssueCommentItem = RepoIssueCommentItem()
                            try:
                                repoIssueCommentItem['repo_id'] = repo_id
                                repoIssueCommentItem['platform'] = platform
                                repoIssueCommentItem['issue_number'] = issue_number
                                repoIssueCommentItem['issue_comment_id'] = issue_comment_id
                                repoIssueCommentItem['create_time'] = create_time
                                repoIssueCommentItem['update_time'] = update_time
                                repoIssueCommentItem['user_id'] = user_id
                                repoIssueCommentItem['author_association'] = author_association
                                repoIssueCommentItem['polarity'] = polarity
                                repoIssueCommentItem['is_core_issue_comment'] = is_core_issue_comment
                            except BaseException as e:
                                self.logger.error('repoIssueCommentItem error! -- ' + current_url)
                            yield repoIssueCommentItem

                            repoIssueCommentExtendItem = RepoIssueCommentExtendItem()
                            try:
                                repoIssueCommentExtendItem['repo_id'] = repo_id
                                repoIssueCommentExtendItem['issue_comment_id'] = issue_comment_id
                                repoIssueCommentExtendItem['platform'] = platform
                                repoIssueCommentExtendItem['issue_comment_body'] = issue_comment_body
                            except BaseException as e:
                                self.logger.error('repoIssueCommentExtendItem error! -- ' + current_url)
                            yield repoIssueCommentExtendItem

                        except BaseException as e:
                            self.logger.critical('repo issue comment crawl error! -- ' + current_url)
                            self.logger.critical(e)
        func_index = 1
        self.scrapy_indexes[func_index] += 1
        if self.scrapy_indexes[func_index] < len(self.scrapy_lists[func_index]):
            new_repo_id = int(self.scrapy_lists[func_index][self.scrapy_indexes[func_index]].split('/')[4])
            yield scrapy.Request(self.scrapy_lists[func_index][self.scrapy_indexes[func_index]],
                                 meta={"repo_id": new_repo_id, "platform": self.platform,
                                       "current_url": self.scrapy_lists[func_index][self.scrapy_indexes[func_index]]},
                                 callback=self.parse_issue_comment, dont_filter=True,
                                 headers=getGitHubHeader(self.token_index))

    def parse_pull(self,response):
        repos_data = json.loads(response.body.decode('utf-8'))
        repos_header = response.headers
        repo_id = response.meta['repo_id']
        platform = response.meta['platform']
        current_url = response.meta['current_url']
        self.logger.debug(current_url)
        if response.status in self.page_loss_status_list:
            self.logger.warning('404: page lost! -- ' + current_url)
        elif response.status in self.token_overtime_status_list:
            self.token_index = (self.token_index + 1) % GitHub_token_number
            self.logger.info('github token changed: token_index = ' + str(self.token_index) + ' -- ' +current_url)
            yield scrapy.Request(current_url,
                                 meta={"repo_id": repo_id, "platform": platform,
                                       "current_url": current_url},
                                 callback=self.parse_pull, dont_filter=True,
                                 headers=getGitHubHeader(self.token_index))
        else:
            try:
                page_start_time = datetime.datetime.strptime(repos_data[-1]['created_at'], self.fmt_GitHub)
                page_end_time = datetime.datetime.strptime(repos_data[0]['created_at'], self.fmt_GitHub)
            except BaseException as e:
                self.logger.error('page start/end time error! -- '+current_url)
                page_start_time = datetime.datetime.now()
                page_end_time = datetime.datetime.now()
            if page_end_time < page_start_time: # 页面数据排序错误
                self.logger.error('data order error! -- '+current_url)
            elif page_end_time < self.start_time: # 已经爬完所需时间段的数据
                self.logger.info('page time before period: ' + str(page_end_time) + ' < ' + str(self.start_time))
            else:
                if page_start_time > self.end_time: # 还没遍历到所需的时间段
                    self.logger.info('page time after period: '+str(page_start_time) + ' > ' + str(self.end_time))
                else:
                    for repos_per_data in repos_data:
                        try:
                            pull_id = repos_per_data['id']
                            pull_number = repos_per_data['number']
                            create_time = datetime.datetime.strptime(repos_per_data['created_at'], self.fmt_GitHub)
                            # ###这里只考虑了pull的时间，没有仔细考虑review和review comment的时间
                            if create_time > self.end_time: #还没到所需时间段的数据
                                continue
                            if create_time < self.start_time: # 爬完所需时间段的数据
                                break
                            create_time = create_time.strftime(self.fmt_MySQL)
                            update_time = datetime.datetime.strptime(repos_per_data['updated_at'], self.fmt_GitHub).strftime(self.fmt_MySQL)
                            if repos_per_data['closed_at'] is None:
                                close_time = self.null_time
                            else:
                                close_time = datetime.datetime.strptime(repos_per_data['closed_at'], self.fmt_GitHub).strftime(self.fmt_MySQL)
                            if repos_per_data['merged_at'] is None:
                                merge_time = self.null_time
                            else:
                                merge_time = datetime.datetime.strptime(repos_per_data['merged_at'], self.fmt_GitHub).strftime(self.fmt_MySQL)
                            pull_state = repos_per_data['state']
                            if pull_state is None:
                                pull_state = ''
                            pull_title = repos_per_data['title']
                            if pull_title is None:
                                pull_title = ''
                            pull_body = repos_per_data['body']
                            if pull_body is None:
                                pull_body = ''
                            if repos_per_data['user'] is None:
                                user_id = 0
                                # user_url = ''
                            else:
                                user_id = repos_per_data['user']['id']
                                # user_url = repos_per_data['user']['url']
                            author_association = repos_per_data['author_association']
                            if author_association is None:
                                author_association = ''
                            if author_association is None:
                                author_association = ''
                            if author_association == 'MEMBER' or author_association == 'COLLABORATOR':
                                is_core_pull = 1
                            else:
                                is_core_pull = 0
                            if repos_per_data['locked'] == 'true':
                                is_locked_pull = 1
                            else:
                                is_locked_pull = 0
                            if merge_time is None:
                                is_merged = 0
                            else:
                                is_merged = 1
                                repoPullMergedItem = RepoPullMergedItem()
                                try:
                                    repoPullMergedItem['repo_id'] = repo_id
                                    repoPullMergedItem['pull_id'] = pull_id
                                    repoPullMergedItem['platform'] = platform
                                    repoPullMergedItem['create_time'] = create_time
                                    repoPullMergedItem['merge_time'] = merge_time
                                    repoPullMergedItem['user_id'] = user_id
                                except BaseException as e:
                                    self.logger.error('repoPullMergedItem error! -- ' + current_url)
                                yield repoPullMergedItem

                            # 进入详情页，计算comment数量和review comment数量
                            s = requests.session()
                            s.keep_alive = False    #防止http connection太多
                            pull_detail_url = current_url.split('?')[0] + "/" + str(pull_number)
                            pull_detail_html_info = get_html_json(pull_detail_url,getGitHubHeader(self.token_index),verify=False)
                            if pull_detail_html_info[2] in self.token_overtime_status_list:
                                self.token_index = (self.token_index + 1) % GitHub_token_number
                                self.logger.info('github token changed: token_index = ' + str(self.token_index) +
                                                 ' -- '+ pull_detail_url)
                                pull_detail_html_info = get_html_json(pull_detail_url,
                                                                      getGitHubHeader(self.token_index), verify=False)
                                if pull_detail_html_info[2] in self.token_overtime_status_list:
                                    self.logger.critical(
                                        'something wrong with GitHub tokens happened! token_index = ' + str(self.token_index)
                                        + ' -- '+ pull_detail_url)
                            pull_detail_info = pull_detail_html_info[0]
                            try:
                                pull_comment_count = pull_detail_info['comments']
                                pull_review_comment_count = pull_detail_info['review_comments']
                            except BaseException as e:
                                self.logger.error('repo pull detail data crawl error! -- ' + pull_detail_url)
                                self.logger.error(e)
                                pull_comment_count = 0 ###
                                pull_review_comment_count = 0 ###

                            #查询review
                            s = requests.session()
                            s.keep_alive = False
                            pull_review_url = current_url.split('?')[0] + "/" + str(pull_number) + "/reviews"
                            pull_review_html_info = get_html_json(pull_review_url,getGitHubHeader(self.token_index),verify=False)
                            if pull_review_html_info[2] in self.token_overtime_status_list:
                                self.token_index = (self.token_index + 1) % GitHub_token_number
                                self.logger.info('github token changed: token_index = ' + str(self.token_index) + ' -- '
                                                 + pull_review_url)
                                pull_review_html_info = get_html_json(pull_review_url,getGitHubHeader(self.token_index),verify=False)
                                if pull_review_html_info[2] in self.token_overtime_status_list:
                                    self.logger.critical(
                                        'something wrong with GitHub tokens happened! token_index = ' + str(self.token_index) +
                                        ' -- '+ pull_review_url)
                            pull_review_info = pull_review_html_info[0]
                            core_review_count = 0
                            if pull_review_info is not None and len(pull_review_info) > 0: ### and "message" not in pull_review_info
                                is_reviewed = 1
                                for per_review in pull_review_info:
                                    try:
                                        pull_review_id = per_review['id']
                                        submit_time = datetime.datetime.strptime(per_review['submitted_at'], self.fmt_GitHub).strftime(self.fmt_MySQL)
                                        if per_review['user'] is None:
                                            review_user_id = 0
                                            # review_user_url = ''
                                        else:
                                            review_user_id = per_review['user']['id']
                                            # review_user_url = per_review['user']['url']
                                        review_author_association = per_review['author_association']
                                        if review_author_association is None:
                                            review_author_association = ''
                                        if review_author_association == 'MEMBER' or review_author_association == 'COLLABORATOR':
                                            core_review_count += 1
                                        repoReviewItem = RepoReviewItem()
                                        try:
                                            repoReviewItem['repo_id'] = repo_id
                                            repoReviewItem['pull_id'] = pull_id
                                            repoReviewItem['review_id'] = pull_review_id
                                            repoReviewItem['platform'] = platform
                                            repoReviewItem['submit_time'] = submit_time
                                            repoReviewItem['user_id'] = review_user_id
                                            repoReviewItem['author_association'] = review_author_association
                                        except BaseException as e:
                                            self.logger.error('repoReviewItem error! -- ' + current_url)
                                        yield repoReviewItem

                                    except BaseException as e:
                                        self.logger.critical('repo pull review data crawl error! -- ' + pull_review_url)
                                        self.logger.critical(e)
                            else:
                                is_reviewed = 0

                            # 查询review comment
                            core_review_comment_count = 0
                            if pull_review_comment_count > 0:
                                s = requests.session()
                                s.keep_alive = False
                                pull_review_comment_url = current_url.split('?')[0] + "/" + str(pull_number) + "/comments"
                                pull_review_comment_html_info = get_html_json(pull_review_comment_url,getGitHubHeader(self.token_index),verify=False)
                                if pull_review_comment_html_info[2] in self.token_overtime_status_list:
                                    self.token_index = (self.token_index + 1) % GitHub_token_number
                                    self.logger.info('github token changed: token_index = ' + str(self.token_index)
                                                     + ' -- ' + pull_review_comment_url)
                                    pull_review_comment_html_info = get_html_json(pull_review_url,
                                                                          getGitHubHeader(self.token_index),
                                                                          verify=False)
                                    if pull_review_comment_html_info[2] in self.token_overtime_status_list:
                                        self.logger.critical(
                                            'something wrong with GitHub tokens happened! token_index = ' + str(self.token_index)
                                            + ' -- ' + pull_review_comment_url)
                                pull_review_comment_info = pull_review_comment_html_info[0]
                                if pull_review_comment_info is not None and len(pull_review_comment_info)>0:### and "message" not in pull_review_comment_info
                                    for per_review_comment in pull_review_comment_info:
                                        try:
                                            pull_request_review_id = per_review_comment['pull_request_review_id']
                                            review_comment_id = per_review_comment['id']
                                            review_comment_create_time = datetime.datetime.strptime(per_review_comment['created_at'], self.fmt_GitHub).strftime(self.fmt_MySQL)
                                            if per_review_comment['user'] is None:
                                                review_comment_user_id = 0
                                                # review_comment_user_url = ''
                                            else:
                                                review_comment_user_id = per_review_comment['user']['id']
                                                # review_comment_user_url = per_review_comment['user']['url']
                                            review_comment_author_association = per_review_comment['author_association']
                                            if review_comment_author_association is None:
                                                review_comment_author_association = ''
                                            if review_comment_author_association == 'MEMBER' or review_comment_author_association == 'COLLABORATOR':
                                                core_review_comment_count += 1
                                            repoReviewCommentItem = RepoReviewCommentItem()
                                            try:
                                                repoReviewCommentItem['repo_id'] = repo_id
                                                repoReviewCommentItem['pull_id'] = pull_id
                                                repoReviewCommentItem['review_id'] = pull_request_review_id
                                                repoReviewCommentItem['review_comment_id'] = review_comment_id
                                                repoReviewCommentItem['platform'] = platform
                                                repoReviewCommentItem['create_time'] = review_comment_create_time
                                                repoReviewCommentItem['user_id'] = review_comment_user_id
                                                repoReviewCommentItem['author_association'] = review_comment_author_association
                                            except BaseException as e:
                                                self.logger.error('repoReviewCommentItem error! -- ' + current_url)
                                            yield repoReviewCommentItem

                                        except BaseException as e:
                                            self.logger.critical('repo pull review comment data crawl error! -- ' +
                                                                 pull_review_comment_url)
                                            self.logger.critical(e)
                            s = requests.session()
                            s.keep_alive = False

                            repoPullItem = RepoPullItem()
                            try:
                                repoPullItem['repo_id'] = repo_id
                                repoPullItem['platform'] = platform
                                repoPullItem['pull_id'] = pull_id
                                repoPullItem['pull_number'] = pull_number
                                repoPullItem['create_time'] = create_time
                                repoPullItem['update_time'] = update_time
                                repoPullItem['close_time'] = close_time
                                repoPullItem['merge_time'] = merge_time
                                repoPullItem['is_core_pull'] = is_core_pull
                                repoPullItem['is_locked_pull'] = is_locked_pull
                                repoPullItem['is_merged'] = is_merged
                                repoPullItem['is_reviewed'] = is_reviewed
                                repoPullItem['pull_state'] = pull_state
                                repoPullItem['pull_comment_count'] = pull_comment_count
                                repoPullItem['pull_review_comment_count'] = pull_review_comment_count
                                repoPullItem['core_review_count'] = core_review_count
                                repoPullItem['core_review_comment_count'] = core_review_comment_count
                                repoPullItem['user_id'] = user_id
                                repoPullItem['author_association'] = author_association
                            except BaseException as e:
                                self.logger.error('repoPullItem error! -- ' + current_url)
                            yield repoPullItem

                            repoPullExtendItem = RepoPullExtendItem()
                            try:
                                repoPullExtendItem['repo_id'] = repo_id
                                repoPullExtendItem['pull_id'] = pull_id
                                repoPullExtendItem['platform'] = platform
                                repoPullExtendItem['pull_title'] = pull_title
                                repoPullExtendItem['pull_body'] = pull_body
                            except BaseException as e:
                                self.logger.error('repoPullExtendItem error! -- ' + current_url)
                            yield repoPullExtendItem

                        except BaseException as e:
                            self.logger.critical('repo pull data crawl error! -- ' + current_url)
                            self.logger.critical(e)

        func_index = 2
        self.scrapy_indexes[func_index] += 1
        if self.scrapy_indexes[func_index] < len(self.scrapy_lists[func_index]):
            new_repo_id = int(self.scrapy_lists[func_index][self.scrapy_indexes[func_index]].split('/')[4])
            yield scrapy.Request(self.scrapy_lists[func_index][self.scrapy_indexes[func_index]],
                                 meta={"repo_id": new_repo_id, "platform": self.platform,
                                       "current_url": self.scrapy_lists[func_index][self.scrapy_indexes[func_index]]},
                                 callback=self.parse_pull, dont_filter=True,
                                 headers=getGitHubHeader(self.token_index))

    def parse_pull_detail(self, response):
        repos_data = json.loads(response.body.decode('utf-8'))
        repos_header = response.headers
        repo_id = response.meta['repo_id']
        platform = response.meta['platform']
        current_url = response.meta['current_url']
        self.logger.debug(current_url)
        if response.status in self.page_loss_status_list:
            self.logger.warning('404: page lost! -- ' + current_url)
        elif response.status in self.token_overtime_status_list:
            self.token_index = (self.token_index + 1) % GitHub_token_number
            self.logger.info('github token changed: token_index = ' + str(self.token_index) + ' -- ' + current_url)
            yield scrapy.Request(current_url,
                                 meta={"repo_id": repo_id, "platform": platform,
                                       "current_url": current_url},
                                 callback=self.parse_pull_detail, dont_filter=True,
                                 headers=getGitHubHeader(self.token_index))
        else:
            try:
                pull_id = repos_data['id']
                pull_number = repos_data['number']
                create_time = datetime.datetime.strptime(repos_data['created_at'], self.fmt_GitHub)
                create_time = create_time.strftime(self.fmt_MySQL)
                update_time = datetime.datetime.strptime(repos_data['updated_at'], self.fmt_GitHub).strftime(
                    self.fmt_MySQL)
                if repos_data['closed_at'] is None:
                    close_time = self.null_time
                else:
                    close_time = datetime.datetime.strptime(repos_data['closed_at'], self.fmt_GitHub).strftime(
                        self.fmt_MySQL)
                if repos_data['merged_at'] is None:
                    merge_time = self.null_time
                else:
                    merge_time = datetime.datetime.strptime(repos_data['merged_at'], self.fmt_GitHub).strftime(
                        self.fmt_MySQL)
                pull_state = repos_data['state']
                if pull_state is None:
                    pull_state = ''
                pull_title = repos_data['title']
                if pull_title is None:
                    pull_title = ''
                pull_body = repos_data['body']
                if pull_body is None:
                    pull_body = ''
                if repos_data['user'] is None:
                    user_id = 0
                else:
                    user_id = repos_data['user']['id']
                author_association = repos_data['author_association']
                if author_association is None:
                    author_association = ''
                if author_association == 'MEMBER' or author_association == 'COLLABORATOR':
                    is_core_pull = 1
                else:
                    is_core_pull = 0
                if repos_data['locked'] == 'true':
                    is_locked_pull = 1
                else:
                    is_locked_pull = 0
                if merge_time is None:
                    is_merged = 0
                else:
                    is_merged = 1
                    repoPullMergedItem = RepoPullMergedItem()
                    try:
                        repoPullMergedItem['repo_id'] = repo_id
                        repoPullMergedItem['pull_id'] = pull_id
                        repoPullMergedItem['platform'] = platform
                        repoPullMergedItem['create_time'] = create_time
                        repoPullMergedItem['merge_time'] = merge_time
                        repoPullMergedItem['user_id'] = user_id
                    except BaseException as e:
                        self.logger.error('repoPullMergedItem error! -- ' + current_url)
                    yield repoPullMergedItem

                pull_comment_count = repos_data['comments']
                pull_review_comment_count = repos_data['review_comments']

                # 查询review
                s = requests.session()
                s.keep_alive = False
                pull_review_url = current_url.split('?')[0] + "/reviews"
                pull_review_html_info = get_html_json(pull_review_url, getGitHubHeader(self.token_index), verify=False)
                if pull_review_html_info[2] in self.token_overtime_status_list:
                    self.token_index = (self.token_index + 1) % GitHub_token_number
                    self.logger.info('github token changed: token_index = ' + str(self.token_index) + ' -- '
                                     + pull_review_url)
                    pull_review_html_info = get_html_json(pull_review_url, getGitHubHeader(self.token_index),
                                                          verify=False)
                    if pull_review_html_info[2] in self.token_overtime_status_list:
                        self.logger.critical(
                            'something wrong with GitHub tokens happened! token_index = ' + str(self.token_index) +
                            ' -- ' + pull_review_url)
                pull_review_info = pull_review_html_info[0]
                core_review_count = 0
                if pull_review_info is not None and len(
                        pull_review_info) > 0:  ### and "message" not in pull_review_info
                    is_reviewed = 1
                    for per_review in pull_review_info:
                        try:
                            pull_review_id = per_review['id']
                            submit_time = datetime.datetime.strptime(per_review['submitted_at'],
                                                                     self.fmt_GitHub).strftime(self.fmt_MySQL)
                            if per_review['user'] is None:
                                review_user_id = 0
                                # review_user_url = ''
                            else:
                                review_user_id = per_review['user']['id']
                                # review_user_url = per_review['user']['url']
                            review_author_association = per_review['author_association']
                            if review_author_association is None:
                                review_author_association = ''
                            if review_author_association == 'MEMBER' or review_author_association == 'COLLABORATOR':
                                core_review_count += 1
                            repoReviewItem = RepoReviewItem()
                            try:
                                repoReviewItem['repo_id'] = repo_id
                                repoReviewItem['pull_id'] = pull_id
                                repoReviewItem['review_id'] = pull_review_id
                                repoReviewItem['platform'] = platform
                                repoReviewItem['submit_time'] = submit_time
                                repoReviewItem['user_id'] = review_user_id
                                repoReviewItem['author_association'] = review_author_association
                            except BaseException as e:
                                self.logger.error('repoReviewItem error! -- ' + current_url)
                            yield repoReviewItem

                        except BaseException as e:
                            self.logger.critical('repo pull review data crawl error! -- ' + pull_review_url)
                            self.logger.critical(e)
                else:
                    is_reviewed = 0

                # 查询review comment
                core_review_comment_count = 0
                if pull_review_comment_count > 0:
                    s = requests.session()
                    s.keep_alive = False
                    pull_review_comment_url = current_url.split('?')[0] + "/comments"
                    pull_review_comment_html_info = get_html_json(pull_review_comment_url,
                                                                  getGitHubHeader(self.token_index), verify=False)
                    if pull_review_comment_html_info[2] in self.token_overtime_status_list:
                        self.token_index = (self.token_index + 1) % GitHub_token_number
                        self.logger.info('github token changed: token_index = ' + str(self.token_index)
                                         + ' -- ' + pull_review_comment_url)
                        pull_review_comment_html_info = get_html_json(pull_review_url,
                                                                      getGitHubHeader(self.token_index),
                                                                      verify=False)
                        if pull_review_comment_html_info[2] in self.token_overtime_status_list:
                            self.logger.critical(
                                'something wrong with GitHub tokens happened! token_index = ' + str(self.token_index)
                                + ' -- ' + pull_review_comment_url)
                    pull_review_comment_info = pull_review_comment_html_info[0]
                    if pull_review_comment_info is not None and len(
                            pull_review_comment_info) > 0:  ### and "message" not in pull_review_comment_info
                        for per_review_comment in pull_review_comment_info:
                            try:
                                pull_request_review_id = per_review_comment['pull_request_review_id']
                                review_comment_id = per_review_comment['id']
                                review_comment_create_time = datetime.datetime.strptime(
                                    per_review_comment['created_at'], self.fmt_GitHub).strftime(self.fmt_MySQL)
                                if per_review_comment['user'] is None:
                                    review_comment_user_id = 0
                                    # review_comment_user_url = ''
                                else:
                                    review_comment_user_id = per_review_comment['user']['id']
                                    # review_comment_user_url = per_review_comment['user']['url']
                                review_comment_author_association = per_review_comment['author_association']
                                if review_comment_author_association is None:
                                    review_comment_author_association = ''
                                if review_comment_author_association == 'MEMBER' or review_comment_author_association == 'COLLABORATOR':
                                    core_review_comment_count += 1
                                repoReviewCommentItem = RepoReviewCommentItem()
                                try:
                                    repoReviewCommentItem['repo_id'] = repo_id
                                    repoReviewCommentItem['pull_id'] = pull_id
                                    repoReviewCommentItem['review_id'] = pull_request_review_id
                                    repoReviewCommentItem['review_comment_id'] = review_comment_id
                                    repoReviewCommentItem['platform'] = platform
                                    repoReviewCommentItem['create_time'] = review_comment_create_time
                                    repoReviewCommentItem['user_id'] = review_comment_user_id
                                    repoReviewCommentItem['author_association'] = review_comment_author_association
                                except BaseException as e:
                                    self.logger.error('repoReviewCommentItem error! -- ' + current_url)
                                yield repoReviewCommentItem

                            except BaseException as e:
                                self.logger.critical('repo pull review comment data crawl error! -- ' +
                                                     pull_review_comment_url)
                                self.logger.critical(e)

                repoPullItem = RepoPullItem()
                try:
                    repoPullItem['repo_id'] = repo_id
                    repoPullItem['platform'] = platform
                    repoPullItem['pull_id'] = pull_id
                    repoPullItem['pull_number'] = pull_number
                    repoPullItem['create_time'] = create_time
                    repoPullItem['update_time'] = update_time
                    repoPullItem['close_time'] = close_time
                    repoPullItem['merge_time'] = merge_time
                    repoPullItem['is_core_pull'] = is_core_pull
                    repoPullItem['is_locked_pull'] = is_locked_pull
                    repoPullItem['is_merged'] = is_merged
                    repoPullItem['is_reviewed'] = is_reviewed
                    repoPullItem['pull_state'] = pull_state
                    repoPullItem['pull_comment_count'] = pull_comment_count
                    repoPullItem['pull_review_comment_count'] = pull_review_comment_count
                    repoPullItem['core_review_count'] = core_review_count
                    repoPullItem['core_review_comment_count'] = core_review_comment_count
                    repoPullItem['user_id'] = user_id
                    repoPullItem['author_association'] = author_association
                except BaseException as e:
                    self.logger.error('repoPullItem error! -- ' + current_url)
                yield repoPullItem

                repoPullExtendItem = RepoPullExtendItem()
                try:
                    repoPullExtendItem['repo_id'] = repo_id
                    repoPullExtendItem['pull_id'] = pull_id
                    repoPullExtendItem['platform'] = platform
                    repoPullExtendItem['pull_title'] = pull_title
                    repoPullExtendItem['pull_body'] = pull_body
                except BaseException as e:
                    self.logger.error('repoPullExtendItem error! -- ' + current_url)
                yield repoPullExtendItem

            except BaseException as e:
                self.logger.critical('repo pull data crawl error! -- ' + current_url)
                self.logger.critical(e)
        func_index = 8
        self.scrapy_indexes[func_index] += 1
        if self.scrapy_indexes[func_index] < len(self.scrapy_lists[func_index]):
            new_repo_id = int(self.scrapy_lists[func_index][self.scrapy_indexes[func_index]].split('/')[4])
            yield scrapy.Request(self.scrapy_lists[func_index][self.scrapy_indexes[func_index]],
                                 meta={"repo_id": new_repo_id, "platform": self.platform,
                                       "current_url": self.scrapy_lists[func_index][self.scrapy_indexes[func_index]]},
                                 callback=self.parse_pull_detail, dont_filter=True,
                                 headers=getGitHubHeader(self.token_index))



    def parse_commit(self,response):
        repos_data = json.loads(response.body.decode('utf-8'))
        repos_header = response.headers
        repo_id = response.meta['repo_id']
        platform = response.meta['platform']
        current_url = response.meta['current_url']
        self.logger.debug(current_url)
        if response.status in self.page_loss_status_list:
            self.logger.warning('404: page lost! -- ' + current_url)
        elif response.status in self.token_overtime_status_list:
            self.token_index = (self.token_index + 1) % GitHub_token_number
            self.logger.info('github token changed: token_index = ' + str(self.token_index) + ' -- ' +current_url)
            yield scrapy.Request(current_url,
                                 meta={"repo_id": repo_id, "platform": platform,
                                       "current_url": current_url},
                                 callback=self.parse_commit, dont_filter=True,
                                 headers=getGitHubHeader(self.token_index))
        else:
            try:
                #API排序是根据committer的时间进行排序的，但获取的是author的时间
                page_start_time = datetime.datetime.strptime(repos_data[-1]['commit']['committer']['date'], self.fmt_GitHub)
                page_end_time = datetime.datetime.strptime(repos_data[0]['commit']['committer']['date'], self.fmt_GitHub)
            except BaseException as e:
                self.logger.error('page start/end time error! -- '+current_url)
                page_start_time = datetime.datetime.now()
                page_end_time = datetime.datetime.now()
            if page_end_time < page_start_time: # 页面数据排序错误
                self.logger.error('data order error! -- '+current_url)
            elif page_end_time < self.start_time: # 已经爬完所需时间段的数据
                self.logger.info('page time before period: ' + str(page_end_time) + ' < ' + str(self.start_time))
            else:
                if page_start_time > self.end_time: # 还没遍历到所需的时间段
                    self.logger.info('page time after period: '+str(page_start_time) + ' > ' + str(self.end_time))
                else:
                    for repos_per_data in repos_data:
                        try:
                            commit_id = repos_per_data['sha']
                            commit_time = datetime.datetime.strptime(repos_per_data['commit']['author']['date'], self.fmt_GitHub)
                            if commit_time > self.end_time: #还没到所需时间段的数据
                                continue
                            if commit_time < self.start_time: # 爬完所需时间段的数据
                                break
                            commit_time = commit_time.strftime(self.fmt_MySQL)
                            # API中可能缺少对应信息###
                            if repos_per_data['author'] is None:
                                user_id = 0
                                # user_url = ''
                            elif 'id' in repos_per_data['author']:########################
                                user_id = repos_per_data['author']['id']
                            else:
                                user_id = 0

                            commit_message = repos_per_data['commit']['message']
                            if commit_message is None:
                                commit_message = ''
                            repoCommitItem = RepoCommitItem()
                            try:
                                repoCommitItem['repo_id'] = repo_id
                                repoCommitItem['commit_id'] = commit_id
                                repoCommitItem['platform'] = platform
                                repoCommitItem['commit_time'] = commit_time
                                repoCommitItem['user_id'] = user_id
                                repoCommitItem['commit_message'] = commit_message
                            except BaseException as e:
                                self.logger.error('repoCommitItem error! -- ' + current_url)
                            yield repoCommitItem

                        except BaseException as e:
                            self.logger.critical('repo commit data crawl error! -- ' + current_url)
                            self.logger.critical(e)
                            # self.logger.critical(str(repos_per_data))
        func_index = 3
        self.scrapy_indexes[func_index] += 1
        if self.scrapy_indexes[func_index] < len(self.scrapy_lists[func_index]):
            new_repo_id = int(self.scrapy_lists[func_index][self.scrapy_indexes[func_index]].split('/')[4])
            yield scrapy.Request(self.scrapy_lists[func_index][self.scrapy_indexes[func_index]],
                                 meta={"repo_id": new_repo_id, "platform": self.platform,
                                       "current_url": self.scrapy_lists[func_index][self.scrapy_indexes[func_index]]},
                                 callback=self.parse_commit, dont_filter=True,
                                 headers=getGitHubHeader(self.token_index))

    def parse_commit_comment(self,response):
        repos_data = json.loads(response.body.decode('utf-8'))
        repos_header = response.headers
        repo_id = response.meta['repo_id']
        platform = response.meta['platform']
        current_url = response.meta['current_url']
        self.logger.debug(current_url)
        if response.status in self.page_loss_status_list:
            self.logger.warning('404: page lost! -- ' + current_url)
        elif response.status in self.token_overtime_status_list:
            self.token_index = (self.token_index + 1) % GitHub_token_number
            self.logger.info('github token changed: token_index = ' + str(self.token_index) + ' -- ' +current_url)
            yield scrapy.Request(current_url,
                                 meta={"repo_id": repo_id, "platform": platform,
                                       "current_url": current_url},
                                 callback=self.parse_commit_comment, dont_filter=True,
                                 headers=getGitHubHeader(self.token_index))
        else:
            try:
                page_start_time = datetime.datetime.strptime(repos_data[0]['created_at'], self.fmt_GitHub)
                page_end_time = datetime.datetime.strptime(repos_data[-1]['created_at'], self.fmt_GitHub)
            except BaseException as e:
                self.logger.error('page start/end time error! -- '+current_url)
                page_start_time = datetime.datetime.now()
                page_end_time = datetime.datetime.now()
            if page_end_time < page_start_time: # 页面数据排序错误
                self.logger.error('data order error! -- '+current_url)
            elif page_end_time < self.start_time: # 已经爬完所需时间段的数据
                self.logger.info('page time before period: ' + str(page_end_time) + ' < ' + str(self.start_time))
            else:
                if page_start_time > self.end_time: # 还没遍历到所需的时间段
                    self.logger.info('page time after period: '+str(page_start_time) + ' > ' + str(self.end_time))
                else:
                    for i in range(len(repos_data) - 1, -1, -1):
                        repos_per_data = repos_data[i]
                        try:
                            comment_time = datetime.datetime.strptime(repos_per_data['created_at'],self.fmt_GitHub)
                            if comment_time > self.end_time: #还没到所需时间段的数据
                                continue
                            if comment_time < self.start_time: # 爬完所需时间段的数据
                                break
                            comment_time = comment_time.strftime(self.fmt_MySQL)
                            if repos_per_data['user'] is None:
                                user_id = 0
                                # user_url = ''
                            else:
                                user_id = repos_per_data['user']['id']
                                # user_url = repos_per_data['user']['url']
                            commit_id = repos_per_data['commit_id']
                            comment_id = repos_per_data['id']
                            author_association = repos_per_data['author_association']
                            if author_association is None:
                                author_association = ''
                            if author_association == 'MEMBER' or author_association == 'COLLABORATOR':
                                is_core_comment = 1
                            else:
                                is_core_comment = 0
                            body = repos_per_data['body']
                            if body is None:
                                body = ''
                            repoCommitCommentItem = RepoCommitCommentItem()
                            try:
                                repoCommitCommentItem['repo_id'] = repo_id
                                repoCommitCommentItem['user_id'] = user_id
                                repoCommitCommentItem['commit_id'] = commit_id
                                repoCommitCommentItem['comment_id'] = comment_id
                                repoCommitCommentItem['platform'] = platform
                                repoCommitCommentItem['comment_time'] = comment_time
                                repoCommitCommentItem['is_core_comment'] = is_core_comment
                                repoCommitCommentItem['author_association'] = author_association
                            except BaseException as e:
                                self.logger.error('repoCommitCommentItem error! -- ' + current_url)
                            yield repoCommitCommentItem

                            repoCommitCommentExtendItem = RepoCommitCommentExtendItem()
                            try:
                                repoCommitCommentExtendItem['repo_id'] = repo_id
                                repoCommitCommentExtendItem['comment_id'] = comment_id
                                repoCommitCommentExtendItem['platform'] = platform
                                repoCommitCommentExtendItem['body'] = body
                            except BaseException as e:
                                self.logger.error('repoCommitCommentExtendItem error! -- ' + current_url)
                            yield repoCommitCommentExtendItem

                        except BaseException as e:
                            self.logger.critical('repo commit comment data crawl error! -- '+current_url)
                            self.logger.critical(e)
        func_index = 4
        self.scrapy_indexes[func_index] += 1
        if self.scrapy_indexes[func_index] < len(self.scrapy_lists[func_index]):
            new_repo_id = int(self.scrapy_lists[func_index][self.scrapy_indexes[func_index]].split('/')[4])
            yield scrapy.Request(self.scrapy_lists[func_index][self.scrapy_indexes[func_index]],
                                 meta={"repo_id": new_repo_id, "platform": self.platform,
                                       "current_url": self.scrapy_lists[func_index][self.scrapy_indexes[func_index]]},
                                 callback=self.parse_commit_comment, dont_filter=True,
                                 headers=getGitHubHeader(self.token_index))

    def parse_fork(self,response):
        repos_data = json.loads(response.body.decode('utf-8'))
        repos_header = response.headers
        repo_id = response.meta['repo_id']
        platform = response.meta['platform']
        current_url = response.meta['current_url']
        self.logger.debug(current_url)
        if response.status in self.page_loss_status_list:
            self.logger.warning('404: page lost! -- ' + current_url)
        elif response.status in self.token_overtime_status_list:
            self.token_index = (self.token_index + 1) % GitHub_token_number
            self.logger.info('github token changed: token_index = ' + str(self.token_index) + ' -- ' +current_url)
            yield scrapy.Request(current_url,
                                 meta={"repo_id": repo_id, "platform": platform,
                                       "current_url": current_url},
                                 callback=self.parse_fork, dont_filter=True,
                                 headers=getGitHubHeader(self.token_index))
        else:
            try:
                page_start_time = datetime.datetime.strptime(repos_data[-1]['created_at'], self.fmt_GitHub)
                page_end_time = datetime.datetime.strptime(repos_data[0]['created_at'], self.fmt_GitHub)
            except BaseException as e:
                self.logger.error('page start/end time error! -- '+current_url)
                page_start_time = datetime.datetime.now()
                page_end_time = datetime.datetime.now()
            if page_end_time < page_start_time: # 页面数据排序错误
                self.logger.error('data order error! -- '+current_url)
            elif page_end_time < self.start_time: # 已经爬完所需时间段的数据
                self.logger.info('page time before period: ' + str(page_end_time) + ' < ' + str(self.start_time))
            else:
                if page_start_time > self.end_time: # 还没遍历到所需的时间段
                    self.logger.info('page time after period: '+str(page_start_time) + ' > ' + str(self.end_time))
                else:
                    for repos_per_data in repos_data:
                        try:
                            fork_id = repos_per_data['id']
                            fork_full_name = repos_per_data['full_name']
                            if fork_full_name is None:
                                fork_full_name = ''
                            create_time = datetime.datetime.strptime(repos_per_data['created_at'], self.fmt_GitHub)
                            if create_time > self.end_time: #还没到所需时间段的数据
                                continue
                            if create_time < self.start_time: # 爬完所需时间段的数据
                                break
                            create_time = create_time.strftime(self.fmt_MySQL)
                            if repos_per_data['owner'] is None:
                                user_id = 0
                                # user_url = ''
                            else:
                                user_id = repos_per_data['owner']['id']
                                # user_url = repos_per_data['owner']['url']
                            repoForkItem = RepoForkItem()
                            try:
                                repoForkItem['repo_id'] = repo_id
                                repoForkItem['platform'] = platform
                                repoForkItem['fork_id'] = fork_id
                                repoForkItem['create_time'] = create_time
                                repoForkItem['user_id'] = user_id
                                repoForkItem['fork_full_name'] = fork_full_name
                            except BaseException as e:
                                self.logger.error('repoForkItem error! -- ' + current_url)
                            yield repoForkItem

                        except BaseException as e:
                            self.logger.critical('repo fork data crawl error! -- '+current_url)
                            self.logger.critical(e)
        func_index = 5
        self.scrapy_indexes[func_index] += 1
        if self.scrapy_indexes[func_index] < len(self.scrapy_lists[func_index]):
            new_repo_id = int(self.scrapy_lists[func_index][self.scrapy_indexes[func_index]].split('/')[4])
            yield scrapy.Request(self.scrapy_lists[func_index][self.scrapy_indexes[func_index]],
                                 meta={"repo_id": new_repo_id, "platform": self.platform,
                                       "current_url": self.scrapy_lists[func_index][self.scrapy_indexes[func_index]]},
                                 callback=self.parse_fork, dont_filter=True,
                                 headers=getGitHubHeader(self.token_index))

    def parse_star(self,response):
        repos_data = json.loads(response.body.decode('utf-8'))
        repos_header = response.headers
        repo_id = response.meta['repo_id']
        platform = response.meta['platform']
        current_url = response.meta['current_url']
        self.logger.debug(current_url)
        if response.status in self.page_loss_status_list:
            self.logger.warning('404: page  lost! -- ' + current_url)
        elif response.status in self.token_overtime_status_list:
            self.token_index = (self.token_index + 1) % GitHub_token_number
            self.logger.info('github token changed: token_index = ' + str(self.token_index) + ' -- ' +current_url)
            yield scrapy.Request(current_url,
                                 meta={"repo_id": repo_id, "platform": platform,
                                       "current_url": current_url},
                                 callback=self.parse_star, dont_filter=True,
                                 headers=getGitHubHeader(self.token_index))
        else:
            try:
                page_start_time = datetime.datetime.strptime(repos_data[0]['starred_at'], self.fmt_GitHub)
                page_end_time = datetime.datetime.strptime(repos_data[-1]['starred_at'], self.fmt_GitHub)
            except BaseException as e:
                self.logger.error('page start/end time error! -- '+current_url)
                page_start_time = datetime.datetime.now()
                page_end_time = datetime.datetime.now()
            if page_end_time < page_start_time: # 页面数据排序错误
                self.logger.error('data order error! -- '+current_url)
            elif page_end_time < self.start_time: # 已经爬完所需时间段的数据
                self.logger.info('page time before period: ' + str(page_end_time) + ' < ' + str(self.start_time))
            else:
                if page_start_time > self.end_time: # 还没遍历到所需的时间段
                    self.logger.info('page time after period: '+str(page_start_time) + ' > ' + str(self.end_time))
                else:
                    for i in range(len(repos_data) - 1, -1, -1):
                        repos_per_data = repos_data[i]
                        try:
                            if repos_per_data['user'] is None:
                                user_id = 0
                                # user_url = ''
                            else:
                                user_id = repos_per_data['user']['id']
                                # user_url = repos_per_data['user']['url']
                            star_time = datetime.datetime.strptime(repos_per_data['starred_at'], self.fmt_GitHub)
                            if star_time > self.end_time: #还没到所需时间段的数据
                                continue
                            if star_time < self.start_time: # 爬完所需时间段的数据
                                break
                            star_time = star_time.strftime(self.fmt_MySQL)
                            repoStarItem = RepoStarItem()
                            try:
                                repoStarItem['repo_id'] = repo_id
                                repoStarItem['user_id'] = user_id
                                repoStarItem['platform'] = platform
                                repoStarItem['star_time'] = star_time
                            except BaseException as e:
                                self.logger.error('repoStarItem error! -- ' + current_url)
                            yield repoStarItem

                        except BaseException as e:
                            self.logger.critical('repo star data crawl error! -- '+current_url)
                            self.logger.critical(e)
        func_index = 6
        self.scrapy_indexes[func_index] += 1
        if self.scrapy_indexes[func_index] < len(self.scrapy_lists[func_index]):
            new_repo_id = int(self.scrapy_lists[func_index][self.scrapy_indexes[func_index]].split('/')[4])
            yield scrapy.Request(self.scrapy_lists[func_index][self.scrapy_indexes[func_index]],
                                 meta={"repo_id": new_repo_id, "platform": self.platform,
                                       "current_url": self.scrapy_lists[func_index][self.scrapy_indexes[func_index]]},
                                 callback=self.parse_star, dont_filter=True,
                                 headers=getGitHubHeader(self.token_index))

    def parse_user(self,response):
        repos_data = json.loads(response.body.decode('utf-8'))
        repos_header = response.headers
        platform = response.meta['platform']
        current_url = response.meta['current_url']
        self.logger.debug(current_url)
        if response.status in self.page_loss_status_list:
            self.logger.warning('404: user page lost! -- '+current_url)
        elif response.status in self.token_overtime_status_list:
            self.token_index = (self.token_index + 1) % GitHub_token_number
            self.logger.info('github token changed: token_index = ' + str(self.token_index) + ' -- ' +current_url)
            yield scrapy.Request(current_url,
                                 meta={"platform": platform, "current_url": current_url},
                                 callback=self.parse_user, headers=getGitHubHeader(self.token_index),
                                 dont_filter=True)
        else:
            try:
                user_id = repos_data['id']
                user_login = repos_data['login']
                user_name = repos_data['name']
                if user_name is None:
                    user_name = ''
                followers_count = repos_data['followers']
                following_count = repos_data['following']
                public_repos_count = repos_data['public_repos']
                user_type = repos_data['type']
                if user_type is None:
                    user_type = ''
                user_company = repos_data['company']
                if user_company is None:
                    user_company = ''
                user_location = repos_data['location']
                if user_location is None:
                    user_location = ''
                user_email = repos_data['email']
                if user_email is None:
                    user_email = ''
                user_blog = repos_data['blog']
                if user_blog is None:
                    user_blog = ''
                create_time = datetime.datetime.strptime(repos_data['created_at'], self.fmt_GitHub).strftime(
                    self.fmt_MySQL)
                update_time = datetime.datetime.strptime(repos_data['updated_at'], self.fmt_GitHub).strftime(
                    self.fmt_MySQL)
                userDataItem = UserDataItem()
                try:
                    userDataItem['user_id'] = user_id
                    userDataItem['platform'] = platform
                    userDataItem['user_login'] = user_login
                    userDataItem['user_name'] = user_name
                    userDataItem['followers_count'] = followers_count
                    userDataItem['following_count'] = following_count
                    userDataItem['public_repos_count'] = public_repos_count
                    userDataItem['user_type'] = user_type
                    userDataItem['create_time'] = create_time
                    userDataItem['update_time'] = update_time
                    userDataItem['user_company'] = user_company
                    userDataItem['user_location'] = user_location
                    userDataItem['user_email'] = user_email
                    userDataItem['user_blog'] = user_blog
                except BaseException as e:
                    self.logger.error('userDataItem error! -- ' + current_url)
                yield userDataItem
            except BaseException as e:
                self.logger.critical('user data crawl error! -- '+current_url)
                self.logger.critical(e)
        func_index = 7
        self.scrapy_indexes[func_index] += 1
        if self.scrapy_indexes[func_index] < len(self.scrapy_lists[func_index]):
            yield scrapy.Request(self.scrapy_lists[func_index][self.scrapy_indexes[func_index]],
                                 meta={"platform": self.platform,
                                       "current_url": self.scrapy_lists[func_index][self.scrapy_indexes[func_index]]},
                                 callback=self.parse_user, dont_filter=True,
                                 headers=getGitHubHeader(self.token_index))

    def parse_data_scope(self,response):
        pass