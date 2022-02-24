# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
from data_crawl_spider.dataCrawler.additionSpider.additionSpider import settings
from data_crawl_spider.dataCrawler.additionSpider.additionSpider.items import *


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


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class AdditionspiderPipeline:
    def process_item(self, item, spider):
        dbObject = dbHandle()
        cursor = dbObject.cursor()
        if isinstance(item, RepoMetadataItem):
            cursor.execute("select * from repo_metadata where repo_id = %s and platform = %s",
                           (item['repo_id'], item['platform']))
            result = cursor.fetchone()
            if result:
                sql = "update repo_metadata set repo_full_name = %s, repo_name = %s, " \
                      "community_name = %s, owner_id = %s, owner_type = %s, repo_description = %s, " \
                      "main_language = %s, languages = %s, languages_count = %s, stars_count = %s, " \
                      "forks_count = %s, subscribers_count = %s, size = %s, create_time = %s, " \
                      "update_time = %s, repo_homepage = %s, repo_license = %s " \
                      "where repo_id = %s and platform = %s"
                try:
                    cursor.execute(sql, (
                        item['repo_full_name'], item['repo_name'], item['community_name'], item['owner_id'],
                        item['owner_type'], item['repo_description'], item['main_language'], item['languages'],
                        item['languages_count'], item['stars_count'], item['forks_count'], item['subscribers_count'],
                        item['size'], item['create_time'], item['update_time'], item['repo_homepage'],
                        item['repo_license'],item['repo_id'], item['platform']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
            else:
                sql = "insert into repo_metadata(repo_id, platform, repo_full_name, " \
                      "repo_name, community_name, owner_id, owner_type, repo_description, " \
                      "main_language, languages, languages_count, stars_count, forks_count, " \
                      "subscribers_count, size, create_time, update_time, repo_homepage, repo_license) " \
                      "values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                try:
                    cursor.execute(sql, (
                        item['repo_id'], item['platform'], item['repo_full_name'], item['repo_name'],
                        item['community_name'], item['owner_id'], item['owner_type'],
                        item['repo_description'], item['main_language'], item['languages'],
                        item['languages_count'], item['stars_count'], item['forks_count'],
                        item['subscribers_count'], item['size'], item['create_time'],
                        item['update_time'], item['repo_homepage'], item['repo_license']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
        elif isinstance(item, UserDataItem):
            cursor.execute("select * from user_data where user_id = %s and platform = %s",
                           (item['user_id'], item['platform']))
            result = cursor.fetchone()
            if result:
                sql = "update user_data set user_login = %s, user_name = %s, " \
                      "followers_count = %s, following_count = %s, public_repos_count = %s, " \
                      "user_type = %s, create_time = %s, update_time = %s, user_company = %s, " \
                      "user_location = %s, user_email = %s, user_blog = %s " \
                      "where user_id = %s and platform = %s"
                try:
                    cursor.execute(sql, (
                        item['user_login'], item['user_name'], item['followers_count'], item['following_count'],
                        item['public_repos_count'], item['user_type'], item['create_time'], item['update_time'],
                        item['user_company'], item['user_location'], item['user_email'], item['user_blog'],
                        item['user_id'], item['platform']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
            else:
                sql = "insert into user_data(user_id, platform, user_login, " \
                      "user_name, followers_count, following_count, public_repos_count, " \
                      "user_type, create_time, update_time, user_company, user_location, " \
                      "user_email, user_blog) " \
                      "values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                try:
                    cursor.execute(sql, (
                        item['user_id'], item['platform'], item['user_login'], item['user_name'],
                        item['followers_count'],
                        item['following_count'], item['public_repos_count'], item['user_type'], item['create_time'],
                        item['update_time'], item['user_company'], item['user_location'], item['user_email'],
                        item['user_blog']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
        elif isinstance(item, RepoDataScopeItem):
            cursor.execute("select * from repo_data_scope where repo_id = %s and platform = %s",
                           (item['repo_id'], item['platform']))
            result = cursor.fetchone()
            if result:
                sql = "update repo_data_scope set repo_issue_scope = %s, " \
                      "repo_issue_closed_scope = %s, repo_issue_comment_scope = %s, " \
                      "repo_pull_scope = %s, repo_pull_merged_scope = %s, " \
                      "repo_review_scope = %s, repo_review_comment_scope = %s, " \
                      "repo_commit_scope = %s, repo_commit_comment_scope = %s, " \
                      "repo_fork_scope = %s, repo_star_scope = %s " \
                      "where repo_id = %s and platform = %s"
                try:
                    cursor.execute(sql, (
                        item['repo_issue_scope'], item['repo_issue_closed_scope'], item['repo_issue_comment_scope'],
                        item['repo_pull_scope'], item['repo_pull_merged_scope'], item['repo_review_scope'],
                        item['repo_review_comment_scope'], item['repo_commit_scope'], item['repo_commit_comment_scope'],
                        item['repo_fork_scope'], item['repo_star_scope'],item['repo_id'], item['platform']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
            else:
                sql = "insert into repo_data_scope(repo_id, platform, repo_issue_scope, " \
                      "repo_issue_closed_scope, repo_issue_comment_scope, repo_pull_scope, " \
                      "repo_pull_merged_scope, repo_review_scope, repo_review_comment_scope, " \
                      "repo_commit_scope, repo_commit_comment_scope, repo_fork_scope, repo_star_scope) " \
                      "values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                try:
                    cursor.execute(sql, (
                        item['repo_id'], item['platform'], item['repo_issue_scope'], item['repo_issue_closed_scope'],
                        item['repo_issue_comment_scope'], item['repo_pull_scope'], item['repo_pull_merged_scope'],
                        item['repo_review_scope'], item['repo_review_comment_scope'], item['repo_commit_scope'],
                        item['repo_commit_comment_scope'], item['repo_fork_scope'], item['repo_star_scope']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
        elif isinstance(item, RepoIssueItem):
            cursor.execute("select * from repo_issue where repo_id = %s and platform = %s and issue_id = %s",
                           (item['repo_id'], item['platform'], item['issue_id']))
            result = cursor.fetchone()
            if result:
                sql = "update repo_issue set issue_number = %s, create_time = %s, " \
                      "update_time = %s, close_time = %s, is_core_issue = %s, " \
                      "is_locked_issue = %s, issue_state = %s, issue_comment_count = %s, " \
                      "user_id = %s, author_association = %s " \
                      "where repo_id = %s and platform = %s and issue_id = %s"
                try:
                    cursor.execute(sql, (
                        item['issue_number'], item['create_time'], item['update_time'], item['close_time'],
                        item['is_core_issue'], item['is_locked_issue'], item['issue_state'],
                        item['issue_comment_count'],
                        item['user_id'], item['author_association'],
                        item['repo_id'], item['platform'], item['issue_id']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
            else:
                sql = "insert into repo_issue(repo_id, platform, issue_id, issue_number, " \
                      "create_time, update_time, close_time, is_core_issue, is_locked_issue, " \
                      "issue_state, issue_comment_count, user_id, author_association) " \
                      "values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                try:
                    cursor.execute(sql, (
                        item['repo_id'], item['platform'], item['issue_id'], item['issue_number'], item['create_time'],
                        item['update_time'], item['close_time'], item['is_core_issue'], item['is_locked_issue'],
                        item['issue_state'], item['issue_comment_count'], item['user_id'], item['author_association']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
        elif isinstance(item, RepoIssueExtendItem):
            cursor.execute("select * from repo_issue_extend where repo_id = %s and issue_id = %s and platform = %s",
                           (item['repo_id'], item['issue_id'], item['platform']))
            result = cursor.fetchone()
            if result:
                sql = "update repo_issue_extend set issue_labels = %s, issue_title = %s, issue_body = %s " \
                      "where repo_id = %s and issue_id = %s and platform = %s"
                try:
                    cursor.execute(sql, (item['issue_labels'], item['issue_title'], item['issue_body'],
                                         item['repo_id'], item['issue_id'], item['platform']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
            else:
                sql = "insert into repo_issue_extend(repo_id, issue_id, platform, " \
                      "issue_labels, issue_title, issue_body) " \
                      "values(%s, %s, %s, %s, %s, %s)"
                try:
                    cursor.execute(sql, (
                        item['repo_id'], item['issue_id'], item['platform'], item['issue_labels'], item['issue_title'],
                        item['issue_body']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
        elif isinstance(item, RepoIssueClosedItem):
            cursor.execute("select * from repo_issue_closed where repo_id = %s and issue_id = %s and platform = %s",
                           (item['repo_id'], item['issue_id'], item['platform']))
            result = cursor.fetchone()
            if result:
                sql = "update repo_issue_closed set create_time = %s, close_time = %s, user_id = %s " \
                      "where repo_id = %s and issue_id = %s and platform = %s"
                try:
                    cursor.execute(sql, (item['create_time'], item['close_time'], item['user_id'],
                                         item['repo_id'], item['issue_id'], item['platform']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
            else:
                sql = "insert into repo_issue_closed(repo_id, issue_id, platform, " \
                      "create_time, close_time, user_id) " \
                      "values(%s, %s, %s, %s, %s, %s)"
                try:
                    cursor.execute(sql, (
                        item['repo_id'], item['issue_id'], item['platform'], item['create_time'], item['close_time'],
                        item['user_id']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
        elif isinstance(item, RepoIssueCommentItem):
            cursor.execute(
                "select * from repo_issue_comment where repo_id = %s and platform = %s and issue_comment_id = %s",
                (item['repo_id'], item['platform'], item['issue_comment_id']))
            result = cursor.fetchone()
            if result:
                sql = "update repo_issue_comment set issue_number = %s, create_time = %s, " \
                      "update_time = %s, user_id = %s, author_association = %s, polarity = %s, " \
                      "is_core_issue_comment = %s " \
                      "where repo_id = %s and platform = %s and issue_comment_id = %s"
                try:
                    cursor.execute(sql, (
                        item['issue_number'], item['create_time'], item['update_time'], item['user_id'],
                        item['author_association'], item['polarity'], item['is_core_issue_comment'],
                        item['repo_id'], item['platform'], item['issue_comment_id']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
            else:
                sql = "insert into repo_issue_comment(repo_id, platform, issue_comment_id, " \
                      "issue_number, create_time, update_time, user_id, author_association, " \
                      "polarity, is_core_issue_comment) " \
                      "values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                try:
                    cursor.execute(sql, (
                        item['repo_id'], item['platform'], item['issue_comment_id'], item['issue_number'],
                        item['create_time'], item['update_time'], item['user_id'], item['author_association'],
                        item['polarity'], item['is_core_issue_comment']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
        elif isinstance(item, RepoIssueCommentExtendItem):
            cursor.execute(
                "select * from repo_issue_comment_extend where repo_id = %s and issue_comment_id = %s and platform = %s",
                (item['repo_id'], item['issue_comment_id'], item['platform']))
            result = cursor.fetchone()
            if result:
                sql = "update repo_issue_comment_extend set issue_comment_body = %s " \
                      "where repo_id = %s and issue_comment_id = %s and platform = %s"
                try:
                    cursor.execute(sql, (item['issue_comment_body'],item['repo_id'],
                                         item['issue_comment_id'], item['platform']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
            else:
                sql = "insert into repo_issue_comment_extend(repo_id, issue_comment_id, " \
                      "platform, issue_comment_body) " \
                      "values(%s, %s, %s, %s)"
                try:
                    cursor.execute(sql, (
                        item['repo_id'], item['issue_comment_id'], item['platform'], item['issue_comment_body']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
        elif isinstance(item, RepoPullItem):
            cursor.execute("select * from repo_pull where repo_id = %s and platform = %s and pull_id = %s",
                           (item['repo_id'], item['platform'], item['pull_id']))
            result = cursor.fetchone()
            if result:
                sql = "update repo_pull set pull_number = %s, create_time = %s, " \
                      "update_time = %s, close_time = %s, merge_time = %s, is_core_pull = %s, " \
                      "is_locked_pull = %s, is_merged = %s, is_reviewed = %s, pull_state = %s, " \
                      "pull_comment_count = %s, pull_review_comment_count = %s, " \
                      "core_review_count = %s, core_review_comment_count = %s, " \
                      "user_id = %s, author_association = %s " \
                      "where repo_id = %s and platform = %s and pull_id = %s"
                try:
                    cursor.execute(sql, (
                        item['pull_number'], item['create_time'], item['update_time'], item['close_time'],
                        item['merge_time'], item['is_core_pull'], item['is_locked_pull'], item['is_merged'],
                        item['is_reviewed'], item['pull_state'], item['pull_comment_count'],
                        item['pull_review_comment_count'], item['core_review_count'], item['core_review_comment_count'],
                        item['user_id'], item['author_association'],
                        item['repo_id'], item['platform'], item['pull_id']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
            else:
                sql = "insert into repo_pull(repo_id, platform, pull_id, pull_number, create_time, " \
                      "update_time, close_time, merge_time, is_core_pull, is_locked_pull, is_merged, " \
                      "is_reviewed, pull_state, pull_comment_count, pull_review_comment_count, " \
                      "core_review_count, core_review_comment_count, user_id, author_association) " \
                      "values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                try:
                    cursor.execute(sql, (
                        item['repo_id'], item['platform'], item['pull_id'], item['pull_number'], item['create_time'],
                        item['update_time'], item['close_time'], item['merge_time'], item['is_core_pull'],
                        item['is_locked_pull'], item['is_merged'], item['is_reviewed'], item['pull_state'],
                        item['pull_comment_count'], item['pull_review_comment_count'], item['core_review_count'],
                        item['core_review_comment_count'], item['user_id'], item['author_association']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
        elif isinstance(item, RepoPullExtendItem):
            cursor.execute("select * from repo_pull_extend where repo_id = %s and pull_id = %s and platform = %s",
                           (item['repo_id'], item['pull_id'], item['platform']))
            result = cursor.fetchone()
            if result:
                sql = "update repo_pull_extend set pull_title = %s, pull_body = %s where repo_id = %s and pull_id = %s and platform = %s"
                try:
                    cursor.execute(sql, (item['pull_title'], item['pull_body'],
                                         item['repo_id'], item['pull_id'], item['platform']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
            else:
                sql = "insert into repo_pull_extend(repo_id, pull_id, platform, pull_title, pull_body) values(%s, %s, %s, %s, %s)"
                try:
                    cursor.execute(sql, (
                    item['repo_id'], item['pull_id'], item['platform'], item['pull_title'], item['pull_body']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
        elif isinstance(item, RepoPullMergedItem):
            cursor.execute("select * from repo_pull_merged where repo_id = %s and pull_id = %s and platform = %s",
                           (item['repo_id'], item['pull_id'], item['platform']))
            result = cursor.fetchone()
            if result:
                sql = "update repo_pull_merged set create_time = %s, merge_time = %s, user_id = %s " \
                      "where repo_id = %s and pull_id = %s and platform = %s"
                try:
                    cursor.execute(sql, (item['create_time'], item['merge_time'], item['user_id'],
                                         item['repo_id'], item['pull_id'], item['platform']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
            else:
                sql = "insert into repo_pull_merged(repo_id, pull_id, platform, create_time, merge_time, user_id) " \
                      "values(%s, %s, %s, %s, %s, %s)"
                try:
                    cursor.execute(sql, (
                        item['repo_id'], item['pull_id'], item['platform'], item['create_time'], item['merge_time'],
                        item['user_id']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
        elif isinstance(item, RepoReviewItem):
            cursor.execute("select * from repo_review where repo_id = %s and review_id = %s and platform = %s",
                           (item['repo_id'], item['review_id'], item['platform']))
            result = cursor.fetchone()
            if result:
                sql = "update repo_review set pull_id = %s, submit_time = %s, " \
                      "user_id = %s, author_association = %s " \
                      "where repo_id = %s and review_id = %s and platform = %s"
                try:
                    cursor.execute(sql,
                                   (item['pull_id'], item['submit_time'], item['user_id'], item['author_association'],
                                    item['repo_id'], item['review_id'], item['platform']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
            else:
                sql = "insert into repo_review(repo_id, review_id, platform, pull_id, " \
                      "submit_time, user_id, author_association) " \
                      "values(%s, %s, %s, %s, %s, %s, %s)"
                try:
                    cursor.execute(sql, (
                        item['repo_id'], item['review_id'], item['platform'], item['pull_id'], item['submit_time'],
                        item['user_id'], item['author_association']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
        elif isinstance(item, RepoReviewCommentItem):
            cursor.execute(
                "select * from repo_review_comment where repo_id = %s and platform = %s and review_comment_id = %s",
                (item['repo_id'], item['platform'], item['review_comment_id']))
            result = cursor.fetchone()
            if result:
                sql = "update repo_review_comment set pull_id = %s, review_id = %s, " \
                      "create_time = %s, user_id = %s, author_association = %s " \
                      "where repo_id = %s and platform = %s and review_comment_id = %s"
                try:
                    cursor.execute(sql, (item['pull_id'], item['review_id'], item['create_time'], item['user_id'],
                                         item['author_association'],item['repo_id'], item['platform'],
                                         item['review_comment_id']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
            else:
                sql = "insert into repo_review_comment(repo_id, platform, review_comment_id, " \
                      "pull_id, review_id, create_time, user_id, author_association) " \
                      "values(%s, %s, %s, %s, %s, %s, %s, %s)"
                try:
                    cursor.execute(sql, (
                        item['repo_id'], item['platform'], item['review_comment_id'], item['pull_id'],
                        item['review_id'],
                        item['create_time'], item['user_id'], item['author_association']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
        elif isinstance(item, RepoCommitItem):
            cursor.execute("select * from repo_commit where repo_id = %s and commit_id = %s and platform = %s",
                           (item['repo_id'], item['commit_id'], item['platform']))
            result = cursor.fetchone()
            if result:
                sql = "update repo_commit set commit_time = %s, user_id = %s, commit_message = %s " \
                      "where repo_id = %s and commit_id = %s and platform = %s"
                try:
                    cursor.execute(sql, (item['commit_time'], item['user_id'], item['commit_message'],
                                         item['repo_id'], item['commit_id'], item['platform']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
            else:
                sql = "insert into repo_commit(repo_id, commit_id, platform, " \
                      "commit_time, user_id, commit_message) " \
                      "values(%s, %s, %s, %s, %s, %s)"
                try:
                    cursor.execute(sql, (
                        item['repo_id'], item['commit_id'], item['platform'], item['commit_time'], item['user_id'],
                        item['commit_message']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
        elif isinstance(item, RepoCommitCommentItem):
            cursor.execute("select * from repo_commit_comment where repo_id = %s and platform = %s and comment_id = %s",
                           (item['repo_id'], item['platform'], item['comment_id']))
            result = cursor.fetchone()
            if result:
                sql = "update repo_commit_comment set user_id = %s, commit_id = %s, " \
                      "comment_time = %s, is_core_comment = %s, author_association = %s " \
                      "where repo_id = %s and platform = %s and comment_id = %s"
                try:
                    cursor.execute(sql, (
                        item['user_id'], item['commit_id'], item['comment_time'], item['is_core_comment'],
                        item['author_association'],
                        item['repo_id'], item['platform'], item['comment_id']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
            else:
                sql = "insert into repo_commit_comment(repo_id, platform, comment_id, " \
                      "user_id, commit_id, comment_time, is_core_comment, author_association) " \
                      "values(%s, %s, %s, %s, %s, %s, %s, %s)"
                try:
                    cursor.execute(sql, (
                        item['repo_id'], item['platform'], item['comment_id'], item['user_id'], item['commit_id'],
                        item['comment_time'], item['is_core_comment'], item['author_association']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
        elif isinstance(item, RepoCommitCommentExtendItem):
            cursor.execute(
                "select * from repo_commit_comment_extend where repo_id = %s and comment_id = %s and platform = %s",
                (item['repo_id'], item['comment_id'], item['platform']))
            result = cursor.fetchone()
            if result:
                sql = "update repo_commit_comment_extend set body = %s " \
                      "where repo_id = %s and comment_id = %s and platform = %s"
                try:
                    cursor.execute(sql, (item['body'],item['repo_id'], item['comment_id'], item['platform']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
            else:
                sql = "insert into repo_commit_comment_extend(repo_id, comment_id, platform, body) " \
                      "values(%s, %s, %s, %s)"
                try:
                    cursor.execute(sql, (item['repo_id'], item['comment_id'], item['platform'], item['body']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
        elif isinstance(item, RepoForkItem):
            cursor.execute("select * from repo_fork where repo_id = %s and platform = %s and fork_id = %s",
                           (item['repo_id'], item['platform'], item['fork_id']))
            result = cursor.fetchone()
            if result:
                sql = "update repo_fork set create_time = %s, user_id = %s, fork_full_name = %s " \
                      "where repo_id = %s and platform = %s and fork_id = %s"
                try:
                    cursor.execute(sql, (item['create_time'], item['user_id'], item['fork_full_name'],
                                         item['repo_id'], item['platform'], item['fork_id']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
            else:
                sql = "insert into repo_fork(repo_id, platform, fork_id, create_time, user_id, fork_full_name) " \
                      "values(%s, %s, %s, %s, %s, %s)"
                try:
                    cursor.execute(sql, (
                        item['repo_id'], item['platform'], item['fork_id'], item['create_time'], item['user_id'],
                        item['fork_full_name']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
        elif isinstance(item, RepoStarItem):
            cursor.execute("select * from repo_star where repo_id = %s and user_id = %s and platform = %s",
                           (item['repo_id'], item['user_id'], item['platform']))
            result = cursor.fetchone()
            if result:
                sql = "update repo_star set star_time = %s " \
                      "where repo_id = %s and user_id = %s and platform = %s"
                try:
                    cursor.execute(sql, (item['star_time'],item['repo_id'], item['user_id'], item['platform']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()
            else:
                sql = "insert into repo_star(repo_id, user_id, platform, star_time) " \
                      "values(%s, %s, %s, %s)"
                try:
                    cursor.execute(sql, (item['repo_id'], item['user_id'], item['platform'], item['star_time']))
                    cursor.connection.commit()
                except BaseException as e:
                    print(item)
                    print(e)
                    dbObject.rollback()

        return item
