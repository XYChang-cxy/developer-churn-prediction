import scrapy
import pymysql
from data_crawl_spider.churnSpider.churnSpider import settings
from data_crawl_spider.churnSpider.churnSpider.spiders.request_header import *
from data_crawl_spider.churnSpider.churnSpider.items import *
import datetime
import re
import logging
import logging.handlers
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

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


class GithubSpider(scrapy.Spider):
    name = 'GitHub'
    allowed_domains = ['api.github.com']

    scrapyed_list = []
    dbObject = dbHandle()
    cursor = dbObject.cursor()
    cursor.execute("select repo_name from churn_search_repos_final where id <= 5")#############
    # cursor.execute("select repo_name from churn_search_repos_final where repo_id = 7276954")
    repo_names = cursor.fetchall()
    for repo_name in repo_names:
        scrapyed_list.append('https://api.github.com/repos/'+repo_name[0])

    repo_index = 0  # indicate the index of the repo crawled
    start_urls = [scrapyed_list[0]]

    proxy = '218.203.132.117:808'###??????
    proxies = {
        'http': 'http://175.4.68.43:8118',
        'https': 'https://218.203.132.117:808',
    }

    skip_http_status_list = [401, 404, 500]     #如果某个仓库主信息api获取失败，则跳过这一仓库
    page_loss_status_list = [404]   #缺页情况，需要手动查找下一页
    token_overtime_status_list = [403]  #token每小时访问次数5000已用完,API rate limit exceeded for user ID xxxxxxxx
    token_index = 0

    # 日志
    logger = logging.getLogger('mylogger')
    logger.setLevel(logging.DEBUG)
    all_handler = logging.handlers.TimedRotatingFileHandler('../logs/all.log', when='H', interval=5, backupCount=30)
    all_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"))
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter("%(asctime)s \t %(levelname)s \t %(funcName)s \t %(message)s"))
    # error_handler = logging.FileHandler('../logs/error.log')
    error_handler = logging.handlers.TimedRotatingFileHandler('../logs/error.log', when='H', interval=24, backupCount=30)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(funcName)s[:%(lineno)d] - %(message)s"))
    logger.addHandler(all_handler)
    logger.addHandler(stream_handler)
    logger.addHandler(error_handler)

    # 爬取的数据的时间段
    # start_time = '2020-01-01 00:00:00'###########
    # end_time = '2022-01-01 23:59:59'##############
    # start_time = '2018-07-01 00:00:00'  ###########
    # end_time = '2020-01-01 23:59:59'  ##############
    start_time = '2012-12-01 00:00:00'  ###########
    end_time = '2017-01-01 23:59:59'  ##############

    fmt_GitHub = '%Y-%m-%dT%H:%M:%SZ'
    fmt_MySQL = '%Y-%m-%d %H:%M:%S'
    null_time = '1000-01-01 00:00:00'
    start_time = datetime.datetime.strptime(start_time, fmt_MySQL)
    end_time = datetime.datetime.strptime(end_time, fmt_MySQL)

    def __init__(self, repo=None, *args, **kwargs):
        super(GithubSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        if response.status in self.skip_http_status_list:
            self.repo_index = self.repo_index + 1
            if self.repo_index <= len(self.scrapyed_list) - 1:
                yield scrapy.Request(self.scrapyed_list[self.repo_index],callback=self.parse,
                                     headers=getGitHubHeader(self.token_index),dont_filter=True)
        # API rate limit exceeded for user ID xxxxxxxx, 调整token，然后重新爬取
        elif response.status in self.token_overtime_status_list:
            self.token_index = (self.token_index+1) % GitHub_token_number
            self.logger.info('github token changed: token_index = '+str(self.token_index)+'; repo_index = '+str(self.repo_index))
            yield scrapy.Request(self.scrapyed_list[self.repo_index], callback=self.parse, dont_filter=True,
                                 headers=getGitHubHeader(self.token_index))
        else:
            try:
                repos_data = json.loads(response.body.decode('utf-8'))
                repo_id = repos_data['id']
                repo_full_name = repos_data['full_name']
                if repo_full_name is None:
                    repo_full_name = ''
                    community_name = ''
                else:
                    community_name = repo_full_name.split('/')[0]
                repo_name = repos_data['name']
                if repo_name is None:
                    repo_name = ''
                platform = 'GitHub'
                if repos_data['owner'] is None:
                    owner_id = 0
                    owner_type = ''
                else:
                    owner_id = repos_data['owner']['id']
                    owner_type = repos_data['owner']['type']
                    if owner_type is None:
                        owner_type = ''
                repo_description = repos_data['description']
                if repo_description is None:
                    repo_description = ''
                main_language = repos_data['language']
                if main_language is None:
                    main_language = ''
                languages_url = repos_data['languages_url']
                if languages_url is not None:
                    try:
                        languages_html_info = get_html_json(languages_url,getGitHubHeader(self.token_index),verify=False)
                        if languages_html_info[2] in self.token_overtime_status_list:
                            self.token_index = (self.token_index + 1) % GitHub_token_number
                            self.logger.info('github token changed: token_index = ' + str(self.token_index)
                                             +' -- '+ languages_url)
                            languages_html_info = get_html_json(languages_url, getGitHubHeader(self.token_index),
                                                                verify=False)
                            if languages_html_info[2] in self.token_overtime_status_list:
                                self.logger.critical(
                                    'something wrong with GitHub tokens happened! token_index = ' + str(self.token_index)
                                    +' -- '+ languages_url)
                        languages = str(languages_html_info[0])
                        languages_count = languages.count(':')
                    except BaseException as e:
                        languages = ''
                        languages_count = 0
                        self.logger.error('Languages url error! -- '+languages_url)
                stars_count = repos_data['stargazers_count']
                forks_count = repos_data['forks_count']
                subscribers_count = repos_data['subscribers_count']
                size = repos_data['size']
                create_time = datetime.datetime.strptime(repos_data['created_at'], self.fmt_GitHub).strftime(self.fmt_MySQL)
                update_time = datetime.datetime.strptime(repos_data['updated_at'], self.fmt_GitHub).strftime(self.fmt_MySQL)
                repo_homepage = repos_data['homepage']
                if repo_homepage is None:
                    repo_homepage = ''
                repo_license = repos_data['license']['name']
                if repo_license is None:
                    repo_license = ''

                repoMetadataItem = RepoMetadataItem()
                try:
                    repoMetadataItem['repo_id'] = repo_id
                    repoMetadataItem['repo_full_name'] = repo_full_name
                    repoMetadataItem['repo_name'] = repo_name
                    repoMetadataItem['community_name'] = community_name
                    repoMetadataItem['platform'] = platform
                    repoMetadataItem['owner_id'] = owner_id
                    repoMetadataItem['owner_type'] = owner_type
                    repoMetadataItem['repo_description'] = repo_description
                    repoMetadataItem['main_language'] = main_language
                    repoMetadataItem['languages'] = languages
                    repoMetadataItem['languages_count'] = languages_count
                    repoMetadataItem['stars_count'] = stars_count
                    repoMetadataItem['forks_count'] = forks_count
                    repoMetadataItem['subscribers_count'] = subscribers_count
                    repoMetadataItem['size'] = size
                    repoMetadataItem['create_time'] = create_time
                    repoMetadataItem['update_time'] = update_time
                    repoMetadataItem['repo_homepage'] = repo_homepage
                    repoMetadataItem['repo_license'] = repo_license
                except BaseException as e:
                    self.logger.error('repoMetadataItem error! repo_index = '+str(self.repo_index))
                yield repoMetadataItem

                # issues data crawl
                issues_url = repos_data["issues_url"][0:-9] + "?state=all&sort=created&direction=desc&per_page=100"
                yield scrapy.Request(issues_url,
                                     meta={"repo_id": repo_id,"platform":platform,"is_first":1,"current_url":issues_url},
                                     callback=self.parse_issue, headers=getGitHubHeader(self.token_index),
                                     dont_filter=True)
                # issues comment data crawl
                issues_comment_url = repos_data["issue_comment_url"][0:-9] + "?sort=created&direction=desc&per_page=100"
                yield scrapy.Request(issues_comment_url,
                                     meta={"repo_id": repo_id,"platform":platform,"is_first":1,"current_url":issues_comment_url},
                                     callback=self.parse_issue_comment,headers=getGitHubHeader(self.token_index),
                                     dont_filter=True)
                # pulls data crawl
                pulls_url = repos_data["pulls_url"][0:-9] + "?state=all&sort=created&direction=desc&per_page=100"
                yield scrapy.Request(pulls_url,
                                     meta={"repo_id": repo_id,"platform":platform,"is_first":1,"current_url":pulls_url},
                                     callback=self.parse_pull, headers=getGitHubHeader(self.token_index),
                                     dont_filter=True)

                # commit data crawl
                commit_url = repos_data['commits_url'][0:-6] + "?sort=created&direction=desc&per_page=100"
                yield scrapy.Request(commit_url,
                                     meta={"repo_id": repo_id,"platform":platform,"is_first":1,"current_url":commit_url},
                                     callback=self.parse_commit,headers=getGitHubHeader(self.token_index),
                                     dont_filter=True)

                #commit comment data crawl  #自动根据创建时间排序，无sort功能，需要从后往前遍历
                commit_comment_url_0 = repos_data["comments_url"][0:-9] + "?page=1000&per_page=100"
                commit_comment_html_info = get_html_json(commit_comment_url_0,getGitHubHeader(self.token_index),verify=False)
                if commit_comment_html_info[2] in self.token_overtime_status_list:
                    self.token_index = (self.token_index + 1) % GitHub_token_number
                    self.logger.info('github token changed: token_index = ' + str(self.token_index) + ' -- '+commit_comment_url_0)
                    commit_comment_html_info = get_html_json(commit_comment_url_0, getGitHubHeader(self.token_index),
                                                             verify=False)
                    if commit_comment_html_info[2] in self.token_overtime_status_list:
                        self.logger.critical('something wrong with GitHub tokens happened! token_index = '+str(self.token_index)
                                             +' -- '+commit_comment_url_0)
                commit_comment_header = commit_comment_html_info[1]
                commit_comment_urls = re.findall(r'(?<=<).[^<]*(?=>; rel=\"last)', str(commit_comment_header))
                if len(commit_comment_urls) > 0:
                    yield scrapy.Request(commit_comment_urls[0],
                                         meta={"repo_id": repo_id, "platform": platform, "is_first": 1,
                                               "current_url": commit_comment_urls[0]},
                                         callback=self.parse_commit_comment,
                                         headers=getGitHubHeader(self.token_index),
                                         dont_filter=True)
                else:
                    self.logger.error('commit comments url not found! repo_index = ' + str(self.repo_index))


                # fork data crawl
                fork_url = repos_data["forks_url"] + "?per_page=100&sort=newest"
                yield scrapy.Request(fork_url,
                                     meta={"repo_id": repo_id,"platform":platform,"is_first":1,"current_url":fork_url},
                                     callback=self.parse_fork, headers=getGitHubHeader(self.token_index),
                                     dont_filter=True)

                # star data crawl   #自动根据创建时间排序，无sort功能,需要从后往前遍历, pagination is limited for this resource
                star_url_0 = repos_data['stargazers_url'] + "?per_page=100"
                star_html_info = get_html_json(star_url_0,getGitHubStarHeader(self.token_index),verify=False)
                if star_html_info[2] in self.token_overtime_status_list:
                    self.token_index = (self.token_index + 1) % GitHub_token_number
                    self.logger.info('github token changed: token_index = ' + str(self.token_index) + ' -- '+star_url_0)
                    star_html_info = get_html_json(star_url_0, getGitHubStarHeader(self.token_index), verify=False)
                    if star_html_info[2] in self.token_overtime_status_list:
                        self.logger.critical('something wrong with GitHub tokens happened! token_index = ' + str(self.token_index)
                                             + ' -- '+star_url_0)
                star_header = star_html_info[1]
                star_urls = re.findall(r'(?<=<).[^<]*(?=>; rel=\"last)', str(star_header))
                if len(star_urls)>0:
                    yield scrapy.Request(star_urls[0],
                                         meta={"repo_id": repo_id,"platform":platform,"is_first":1,"current_url":star_urls[0]},
                                         callback=self.parse_star, headers=getGitHubStarHeader(self.token_index),
                                         dont_filter=True)
                else:
                    self.logger.error('stargazers url not found! repo_index = ' + str(self.repo_index))

            except BaseException as e:
                self.logger.critical('repo metadata crawl error! repo_index = ' + str(self.repo_index))
                self.logger.critical(e)
            finally:
                self.repo_index = self.repo_index + 1
                if self.repo_index <= len(self.scrapyed_list) - 1:
                    yield scrapy.Request(self.scrapyed_list[self.repo_index], callback=self.parse,
                                         headers=getGitHubHeader(self.token_index),dont_filter=True)

    def parse_issue(self, response):
        repos_data = json.loads(response.body.decode('utf-8'))
        repos_header = response.headers
        repo_id = response.meta['repo_id']
        platform = response.meta['platform']
        current_url = response.meta['current_url']
        is_first = response.meta['is_first']
        if response.status in self.page_loss_status_list: # page loss in this API
            page_index = current_url.find('?page=')
            if page_index == -1:
                page_index = current_url.find('&page=')
            self.logger.warning('404: page '+page_index+' is lost! -- '+ current_url)
            if is_first==1:
                self.logger.error('First page lost! -- '+current_url)
            elif page_index!= -1: #不是第一页，手动查找下一页
                j = page_index + 6
                for i in range(page_index + 6, len(current_url)):
                    if current_url[i] < '0' or current_url[i] > '9':
                        j = i
                        break
                #下一页面
                next_url = current_url.replace(current_url[page_index:j],
                                               current_url[page_index:page_index + 6] +
                                               str(int(current_url[page_index + 6:j]) + 1))
                self.logger.warning("current_url:", current_url, "\nnext_url:", next_url)
                yield scrapy.Request(next_url,
                                     meta={"repo_id": repo_id, "platform": platform, "is_first": 0, "current_url": next_url},
                                     callback=self.parse_issue, headers=getGitHubHeader(self.token_index),
                                     dont_filter=True)
        elif response.status in self.token_overtime_status_list: # github token is overtime and can be used after an hour
            self.token_index = (self.token_index + 1) % GitHub_token_number
            self.logger.info('github token changed: token_index = ' + str(self.token_index) + ' -- ' +current_url)
            yield scrapy.Request(current_url,
                                 meta={"repo_id": repo_id, "platform": platform, "is_first": is_first,"current_url":current_url},
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
                                user_url = ''
                            else:
                                user_id = repos_per_data['user']['id']
                                user_url = repos_per_data['user']['url']
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

                            if user_url != '':
                                yield scrapy.Request(user_url, meta={"platform":platform,"current_url":user_url},
                                                     callback=self.parse_user, headers=getGitHubHeader(self.token_index),
                                                     dont_filter=True)
                        except BaseException as e:
                            self.logger.critical('repo issue crawl error! -- ' + current_url)
                            self.logger.critical(e)

                #查找issue数据的下一页
                listLink_next_url = re.findall(r'(?<=<).[^<]*(?=>; rel=\"next)',
                                               str(repos_header))  # 匹配“<”后面,“>;rel='next”前面的字符串,“.”表示任意非换行字符,“[^<]”表示任意非"<"的字符
                if len(listLink_next_url) > 0:
                    yield scrapy.Request(listLink_next_url[0],
                                         meta={"repo_id": repo_id,"platform":platform,"is_first":0,"current_url":listLink_next_url[0]},
                                         callback=self.parse_issue, headers=getGitHubHeader(self.token_index),
                                         dont_filter=True)

    def parse_issue_comment(self,response):
        repos_data = json.loads(response.body.decode('utf-8'))
        repos_header = response.headers
        repo_id = response.meta['repo_id']
        platform = response.meta['platform']
        current_url = response.meta['current_url']
        is_first = response.meta['is_first']
        if response.status in self.page_loss_status_list:
            page_index = current_url.find('?page=')
            if page_index == -1:
                page_index = current_url.find('&page=')
            self.logger.warning('404: page ' + page_index + ' is lost! -- ' + current_url)
            if is_first == 1:
                self.logger.error('First page lost! -- ' + current_url)
            elif page_index != -1:  # 不是第一页，手动查找下一页
                j = page_index + 6
                for i in range(page_index + 6, len(current_url)):
                    if current_url[i] < '0' or current_url[i] > '9':
                        j = i
                        break
                # 下一页面
                next_url = current_url.replace(current_url[page_index:j],
                                               current_url[page_index:page_index + 6] +
                                               str(int(current_url[page_index + 6:j]) + 1))
                self.logger.warning("current_url:", current_url, "\nnext_url:", next_url)
                yield scrapy.Request(next_url,
                                     meta={"repo_id": repo_id, "platform": platform, "is_first": 0,
                                           "current_url": next_url},
                                     callback=self.parse_issue_comment, headers=getGitHubHeader(self.token_index),
                                     dont_filter=True)
        elif response.status in self.token_overtime_status_list:
            self.token_index = (self.token_index + 1) % GitHub_token_number
            self.logger.info('github token changed: token_index = ' + str(self.token_index) + ' -- ' +current_url)
            yield scrapy.Request(current_url,
                                 meta={"repo_id": repo_id, "platform": platform, "is_first": is_first,
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
                                user_url = ''
                            else:
                                user_id = repos_per_data['user']['id']
                                user_url = repos_per_data['user']['url']
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

                            if user_url != '':
                                yield scrapy.Request(user_url,
                                                 meta={"platform":platform,"current_url":user_url},
                                                 callback=self.parse_user, headers=getGitHubHeader(self.token_index),
                                                 dont_filter=True)
                        except BaseException as e:
                            self.logger.critical('repo issue comment crawl error! -- ' + current_url)
                            self.logger.critical(e)
                listLink_next_url = re.findall(r'(?<=<).[^<]*(?=>; rel=\"next)', str(repos_header))
                if len(listLink_next_url) > 0:
                    yield scrapy.Request(listLink_next_url[0],
                                         meta={"repo_id": repo_id,"platform":platform,"is_first":0,"current_url":listLink_next_url[0]},
                                         callback=self.parse_issue_comment, headers=getGitHubHeader(self.token_index),
                                         dont_filter=True)

    def parse_pull(self,response):
        repos_data = json.loads(response.body.decode('utf-8'))
        repos_header = response.headers
        repo_id = response.meta['repo_id']
        platform = response.meta['platform']
        current_url = response.meta['current_url']
        is_first = response.meta['is_first']
        if response.status in self.page_loss_status_list:
            page_index = current_url.find('?page=')
            if page_index == -1:
                page_index = current_url.find('&page=')
            self.logger.warning('404: page ' + page_index + ' is lost! -- ' + current_url)
            if is_first == 1:
                self.logger.error('First page lost! -- ' + current_url)
            elif page_index != -1:  # 不是第一页，手动查找下一页
                j = page_index + 6
                for i in range(page_index + 6, len(current_url)):
                    if current_url[i] < '0' or current_url[i] > '9':
                        j = i
                        break
                # 下一页面
                next_url = current_url.replace(current_url[page_index:j],
                                               current_url[page_index:page_index + 6] +
                                               str(int(current_url[page_index + 6:j]) + 1))
                self.logger.warning("current_url:", current_url, "\nnext_url:", next_url)
                yield scrapy.Request(next_url,
                                     meta={"repo_id": repo_id, "platform": platform, "is_first": 0,
                                           "current_url": next_url},
                                     callback=self.parse_pull, headers=getGitHubHeader(self.token_index),
                                     dont_filter=True)
        elif response.status in self.token_overtime_status_list:
            self.token_index = (self.token_index + 1) % GitHub_token_number
            self.logger.info('github token changed: token_index = ' + str(self.token_index) + ' -- ' +current_url)
            yield scrapy.Request(current_url,
                                 meta={"repo_id": repo_id, "platform": platform, "is_first": is_first,
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
                                user_url = ''
                            else:
                                user_id = repos_per_data['user']['id']
                                user_url = repos_per_data['user']['url']
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
                                            review_user_url = ''
                                        else:
                                            review_user_id = per_review['user']['id']
                                            review_user_url = per_review['user']['url']
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

                                        if review_user_url != '':
                                            yield scrapy.Request(review_user_url,
                                                                 meta={"platform":platform,"current_url":review_user_url},
                                                                 callback=self.parse_user, headers=getGitHubHeader(self.token_index),
                                                                 dont_filter=True)
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
                                                review_comment_user_url = ''
                                            else:
                                                review_comment_user_id = per_review_comment['user']['id']
                                                review_comment_user_url = per_review_comment['user']['url']
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

                                            if review_comment_user_url != '':
                                                yield scrapy.Request(review_comment_user_url,
                                                                 meta={"platform":platform,"current_url":review_comment_user_url},
                                                                 callback=self.parse_user, headers=getGitHubHeader(self.token_index),
                                                                 dont_filter=True)
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

                            if user_url!= '':
                                yield scrapy.Request(user_url,
                                                 meta={"platform":platform,"current_url":user_url},
                                                 callback=self.parse_user, headers=getGitHubHeader(self.token_index),
                                                 dont_filter=True)
                        except BaseException as e:
                            self.logger.critical('repo pull data crawl error! -- ' + current_url)
                            self.logger.critical(e)

                listLink_next_url = re.findall(r'(?<=<).[^<]*(?=>; rel=\"next)', str(repos_header))
                if len(listLink_next_url) > 0:
                    yield scrapy.Request(listLink_next_url[0],
                                         meta={"repo_id": repo_id,"platform":platform,"is_first":0,"current_url":listLink_next_url[0]},
                                         callback=self.parse_pull, headers=getGitHubHeader(self.token_index),
                                         dont_filter=True)

    def parse_commit(self,response):
        repos_data = json.loads(response.body.decode('utf-8'))
        repos_header = response.headers
        repo_id = response.meta['repo_id']
        platform = response.meta['platform']
        current_url = response.meta['current_url']
        is_first = response.meta['is_first']
        if response.status in self.page_loss_status_list:
            page_index = current_url.find('?page=')
            if page_index == -1:
                page_index = current_url.find('&page=')
            self.logger.warning('404: page ' + page_index + ' is lost! -- ' + current_url)
            if is_first == 1:
                self.logger.error('First page lost! -- ' + current_url)
            elif page_index != -1:  # 不是第一页，手动查找下一页
                j = page_index + 6
                for i in range(page_index + 6, len(current_url)):
                    if current_url[i] < '0' or current_url[i] > '9':
                        j = i
                        break
                # 下一页面
                next_url = current_url.replace(current_url[page_index:j],
                                               current_url[page_index:page_index + 6] +
                                               str(int(current_url[page_index + 6:j]) + 1))
                self.logger.warning("current_url:", current_url, "\nnext_url:", next_url)
                yield scrapy.Request(next_url,
                                     meta={"repo_id": repo_id, "platform": platform, "is_first": 0,
                                           "current_url": next_url},
                                     callback=self.parse_commit, headers=getGitHubHeader(self.token_index),
                                     dont_filter=True)
        elif response.status in self.token_overtime_status_list:
            self.token_index = (self.token_index + 1) % GitHub_token_number
            self.logger.info('github token changed: token_index = ' + str(self.token_index) + ' -- ' +current_url)
            yield scrapy.Request(current_url,
                                 meta={"repo_id": repo_id, "platform": platform, "is_first": is_first,
                                       "current_url": current_url},
                                 callback=self.parse_commit, dont_filter=True,
                                 headers=getGitHubHeader(self.token_index))
        else:
            try:
                page_start_time = datetime.datetime.strptime(repos_data[-1]['commit']['author']['date'], self.fmt_GitHub)
                page_end_time = datetime.datetime.strptime(repos_data[0]['commit']['author']['date'], self.fmt_GitHub)
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
                                user_url = ''
                            else:
                                user_id = repos_per_data['author']['id']
                                user_url = repos_per_data['author']['url']

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

                            if user_url != '':
                                yield scrapy.Request(user_url,
                                                     meta={"platform":platform,"current_url":user_url},
                                                     callback=self.parse_user, headers=getGitHubHeader(self.token_index),
                                                     dont_filter=True)
                        except BaseException as e:
                            self.logger.critical('repo commit data crawl error! -- ' + current_url)
                            self.logger.critical(e)
                            # self.logger.critical(str(repos_per_data))
                listLink_next_url = re.findall(r'(?<=<).[^<]*(?=>; rel=\"next)', str(repos_header))
                if len(listLink_next_url) > 0:
                    yield scrapy.Request(listLink_next_url[0],
                                         meta={"repo_id": repo_id,"platform":platform,"is_first":0,"current_url":listLink_next_url[0]},
                                         callback=self.parse_commit, headers=getGitHubHeader(self.token_index),
                                         dont_filter=True)

    def parse_commit_comment(self,response):
        repos_data = json.loads(response.body.decode('utf-8'))
        repos_header = response.headers
        repo_id = response.meta['repo_id']
        platform = response.meta['platform']
        current_url = response.meta['current_url']
        is_first = response.meta['is_first']
        if response.status in self.page_loss_status_list:
            page_index = current_url.find('?page=')
            if page_index == -1:
                page_index = current_url.find('&page=')
            self.logger.warning('404: page ' + page_index + ' is lost! -- ' + current_url)
            if is_first == 1:
                self.logger.error('First page lost! -- ' + current_url)
            elif page_index != -1:  # 不是第一页，手动查找下一页
                j = page_index + 6
                for i in range(page_index + 6, len(current_url)):
                    if current_url[i] < '0' or current_url[i] > '9':
                        j = i
                        break
                # 下一页面
                next_url = current_url.replace(current_url[page_index:j],
                                               current_url[page_index:page_index + 6] +
                                               str(int(current_url[page_index + 6:j]) + 1))
                self.logger.warning("current_url:", current_url, "\nnext_url:", next_url)
                yield scrapy.Request(next_url,
                                     meta={"repo_id": repo_id, "platform": platform, "is_first": 0,
                                           "current_url": next_url},
                                     callback=self.parse_commit_comment, headers=getGitHubHeader(self.token_index),
                                     dont_filter=True)
        elif response.status in self.token_overtime_status_list:
            self.token_index = (self.token_index + 1) % GitHub_token_number
            self.logger.info('github token changed: token_index = ' + str(self.token_index) + ' -- ' +current_url)
            yield scrapy.Request(current_url,
                                 meta={"repo_id": repo_id, "platform": platform, "is_first": is_first,
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
                                user_url = ''
                            else:
                                user_id = repos_per_data['user']['id']
                                user_url = repos_per_data['user']['url']
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

                            if user_url != '':
                                yield scrapy.Request(user_url,
                                                     meta={"platform":platform,"current_url":user_url},
                                                     callback=self.parse_user, headers=getGitHubHeader(self.token_index),
                                                     dont_filter=True)
                        except BaseException as e:
                            self.logger.critical('repo commit comment data crawl error! -- '+current_url)
                            self.logger.critical(e)
                listLink_next_url = re.findall(r'(?<=<).[^<]*(?=>; rel=\"prev)', str(repos_header))
                if len(listLink_next_url) > 0:
                    yield scrapy.Request(listLink_next_url[0],
                                         meta={"repo_id": repo_id,"platform":platform,"is_first":0,"current_url":listLink_next_url[0]},
                                         callback=self.parse_commit_comment, headers=getGitHubHeader(self.token_index),
                                         dont_filter=True)

    def parse_fork(self,response):
        repos_data = json.loads(response.body.decode('utf-8'))
        repos_header = response.headers
        repo_id = response.meta['repo_id']
        platform = response.meta['platform']
        current_url = response.meta['current_url']
        is_first = response.meta['is_first']
        if response.status in self.page_loss_status_list:
            page_index = current_url.find('?page=')
            if page_index == -1:
                page_index = current_url.find('&page=')
            self.logger.warning('404: page ' + page_index + ' is lost! -- ' + current_url)
            if is_first == 1:
                self.logger.error('First page lost! -- ' + current_url)
            elif page_index != -1:  # 不是第一页，手动查找下一页
                j = page_index + 6
                for i in range(page_index + 6, len(current_url)):
                    if current_url[i] < '0' or current_url[i] > '9':
                        j = i
                        break
                # 下一页面
                next_url = current_url.replace(current_url[page_index:j],
                                               current_url[page_index:page_index + 6] +
                                               str(int(current_url[page_index + 6:j]) + 1))
                self.logger.warning("current_url:", current_url, "\nnext_url:", next_url)
                yield scrapy.Request(next_url,
                                     meta={"repo_id": repo_id, "platform": platform, "is_first": 0,
                                           "current_url": next_url},
                                     callback=self.parse_fork, headers=getGitHubHeader(self.token_index),
                                     dont_filter=True)
        elif response.status in self.token_overtime_status_list:
            self.token_index = (self.token_index + 1) % GitHub_token_number
            self.logger.info('github token changed: token_index = ' + str(self.token_index) + ' -- ' +current_url)
            yield scrapy.Request(current_url,
                                 meta={"repo_id": repo_id, "platform": platform, "is_first": is_first,
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

                            # if user_url != '':
                            #     yield scrapy.Request(user_url, meta={"platform":platform,"current_url":user_url},
                            #     callback=self.parse_user, headers=getGitHubHeader(self.token_index),dont_filter=True)
                        except BaseException as e:
                            self.logger.critical('repo fork data crawl error! -- '+current_url)
                            self.logger.critical(e)
                listLink_next_url = re.findall(r'(?<=<).[^<]*(?=>; rel=\"next)', str(repos_header))
                if len(listLink_next_url) > 0:
                    yield scrapy.Request(listLink_next_url[0],
                                         meta={"repo_id": repo_id,"platform":platform,"is_first":0,"current_url":listLink_next_url[0]},
                                         callback=self.parse_fork, headers=getGitHubHeader(self.token_index),
                                         dont_filter=True)

    def parse_star(self,response):
        repos_data = json.loads(response.body.decode('utf-8'))
        repos_header = response.headers
        repo_id = response.meta['repo_id']
        platform = response.meta['platform']
        current_url = response.meta['current_url']
        is_first = response.meta['is_first']
        if response.status in self.page_loss_status_list:
            page_index = current_url.find('?page=')
            if page_index == -1:
                page_index = current_url.find('&page=')
            self.logger.warning('404: page ' + page_index + ' is lost! -- ' + current_url)
            if is_first == 1:
                self.logger.error('First page lost! -- ' + current_url)
            elif page_index != -1:  # 不是第一页，手动查找下一页
                j = page_index + 6
                for i in range(page_index + 6, len(current_url)):
                    if current_url[i] < '0' or current_url[i] > '9':
                        j = i
                        break
                # 下一页面
                next_url = current_url.replace(current_url[page_index:j],
                                               current_url[page_index:page_index + 6] +
                                               str(int(current_url[page_index + 6:j]) + 1))
                self.logger.warning("current_url:", current_url, "\nnext_url:", next_url)
                yield scrapy.Request(next_url,
                                     meta={"repo_id": repo_id, "platform": platform, "is_first": 0,
                                           "current_url": next_url},
                                     callback=self.parse_star, headers=getGitHubHeader(self.token_index),
                                     dont_filter=True)
        elif response.status in self.token_overtime_status_list:
            self.token_index = (self.token_index + 1) % GitHub_token_number
            self.logger.info('github token changed: token_index = ' + str(self.token_index) + ' -- ' +current_url)
            yield scrapy.Request(current_url,
                                 meta={"repo_id": repo_id, "platform": platform, "is_first": is_first,
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

                            # if user_url != '':
                            #     yield scrapy.Request(user_url, callback=self.parse_user, meta={"platform":platform,
                            #     "current_url":user_url}, headers=getGitHubHeader(self.token_index),dont_filter=True)
                        except BaseException as e:
                            self.logger.critical('repo star data crawl error! -- '+current_url)
                            self.logger.critical(e)
                listLink_next_url = re.findall(r'(?<=<).[^<]*(?=>; rel=\"prev)', str(repos_header))
                if len(listLink_next_url) > 0:
                    yield scrapy.Request(listLink_next_url[0],
                                         meta={"repo_id": repo_id,"platform":platform,"is_first":0,"current_url":listLink_next_url[0]},
                                         callback=self.parse_star,headers=getGitHubStarHeader(self.token_index),
                                         dont_filter=True)

    def parse_user(self,response):
        repos_data = json.loads(response.body.decode('utf-8'))
        repos_header = response.headers
        platform = response.meta['platform']
        current_url = response.meta['current_url']
        if response.status in self.page_loss_status_list:
            self.logger.warning('404: user page is lost! -- '+current_url)
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

    def parse_data_scope(self,response):
        pass

