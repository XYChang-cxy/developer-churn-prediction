# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RepoMetadataItem(scrapy.Item):
    repo_id = scrapy.Field()
    repo_full_name = scrapy.Field()
    repo_name = scrapy.Field()
    community_name = scrapy.Field()
    platform = scrapy.Field()
    owner_id = scrapy.Field()
    owner_type = scrapy.Field()
    repo_description = scrapy.Field()
    main_language = scrapy.Field()
    languages = scrapy.Field()
    languages_count = scrapy.Field()
    stars_count = scrapy.Field()
    forks_count = scrapy.Field()
    subscribers_count = scrapy.Field()
    size = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    repo_homepage = scrapy.Field()
    repo_license = scrapy.Field()


class UserDataItem(scrapy.Item):
    user_id = scrapy.Field()
    platform = scrapy.Field()
    user_login = scrapy.Field()
    user_name = scrapy.Field()
    followers_count = scrapy.Field()
    following_count = scrapy.Field()
    public_repos_count = scrapy.Field()
    user_type = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    user_company = scrapy.Field()
    user_location = scrapy.Field()
    user_email = scrapy.Field()
    user_blog = scrapy.Field()


class RepoDataScopeItem(scrapy.Item):
    repo_id = scrapy.Field()
    platform = scrapy.Field()
    repo_issue_scope = scrapy.Field()
    repo_issue_closed_scope = scrapy.Field()
    repo_issue_comment_scope = scrapy.Field()
    repo_pull_scope = scrapy.Field()
    repo_pull_merged_scope = scrapy.Field()
    repo_review_scope = scrapy.Field()
    repo_review_comment_scope = scrapy.Field()
    repo_commit_scope = scrapy.Field()
    repo_commit_comment_scope = scrapy.Field()
    repo_fork_scope = scrapy.Field()
    repo_star_scope = scrapy.Field()


class RepoIssueItem(scrapy.Item):
    repo_id = scrapy.Field()
    platform = scrapy.Field()
    issue_id = scrapy.Field()
    issue_number = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    close_time = scrapy.Field()
    is_core_issue = scrapy.Field()
    is_locked_issue = scrapy.Field()
    issue_state = scrapy.Field()
    issue_comment_count = scrapy.Field()
    user_id = scrapy.Field()
    author_association = scrapy.Field()


class RepoIssueExtendItem(scrapy.Item):
    repo_id = scrapy.Field()
    issue_id = scrapy.Field()
    platform = scrapy.Field()
    issue_labels = scrapy.Field()
    issue_title = scrapy.Field()
    issue_body = scrapy.Field()


class RepoIssueClosedItem(scrapy.Item):
    repo_id = scrapy.Field()
    issue_id = scrapy.Field()
    platform = scrapy.Field()
    create_time = scrapy.Field()
    close_time = scrapy.Field()
    user_id = scrapy.Field()


class RepoIssueCommentItem(scrapy.Item):
    repo_id = scrapy.Field()
    platform = scrapy.Field()
    issue_number = scrapy.Field()
    issue_comment_id = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    user_id = scrapy.Field()
    author_association = scrapy.Field()
    polarity = scrapy.Field()
    is_core_issue_comment = scrapy.Field()


class RepoIssueCommentExtendItem(scrapy.Item):
    repo_id = scrapy.Field()
    issue_comment_id = scrapy.Field()
    platform = scrapy.Field()
    issue_comment_body = scrapy.Field()


class RepoPullItem(scrapy.Item):
    repo_id = scrapy.Field()
    platform = scrapy.Field()
    pull_id = scrapy.Field()
    pull_number = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    close_time = scrapy.Field()
    merge_time = scrapy.Field()
    is_core_pull = scrapy.Field()
    is_locked_pull = scrapy.Field()
    is_merged = scrapy.Field()
    is_reviewed = scrapy.Field()
    pull_state = scrapy.Field()
    pull_comment_count = scrapy.Field()
    pull_review_comment_count = scrapy.Field()
    core_review_count = scrapy.Field()
    core_review_comment_count = scrapy.Field()
    user_id = scrapy.Field()
    author_association = scrapy.Field()


class RepoPullExtendItem(scrapy.Item):
    repo_id = scrapy.Field()
    pull_id = scrapy.Field()
    platform = scrapy.Field()
    pull_title = scrapy.Field()
    pull_body = scrapy.Field()


class RepoPullMergedItem(scrapy.Item):
    repo_id = scrapy.Field()
    pull_id = scrapy.Field()
    platform = scrapy.Field()
    create_time = scrapy.Field()
    merge_time = scrapy.Field()
    user_id = scrapy.Field()


class RepoReviewItem(scrapy.Item):
    repo_id = scrapy.Field()
    pull_id = scrapy.Field()
    review_id = scrapy.Field()
    platform = scrapy.Field()
    submit_time = scrapy.Field()
    user_id = scrapy.Field()
    author_association = scrapy.Field()


class RepoReviewCommentItem(scrapy.Item):
    repo_id = scrapy.Field()
    pull_id = scrapy.Field()
    review_id = scrapy.Field()
    review_comment_id = scrapy.Field()
    platform = scrapy.Field()
    create_time = scrapy.Field()
    user_id = scrapy.Field()
    author_association = scrapy.Field()


class RepoCommitItem(scrapy.Item):
    repo_id = scrapy.Field()
    commit_id = scrapy.Field()
    platform = scrapy.Field()
    commit_time = scrapy.Field()
    user_id = scrapy.Field()
    commit_message = scrapy.Field()


class RepoCommitCommentItem(scrapy.Item):
    repo_id = scrapy.Field()
    user_id = scrapy.Field()
    commit_id = scrapy.Field()
    comment_id = scrapy.Field()
    platform = scrapy.Field()
    comment_time = scrapy.Field()
    is_core_comment = scrapy.Field()
    author_association = scrapy.Field()


class RepoCommitCommentExtendItem(scrapy.Item):
    repo_id = scrapy.Field()
    comment_id = scrapy.Field()
    platform = scrapy.Field()
    body = scrapy.Field()


class RepoForkItem(scrapy.Item):
    repo_id = scrapy.Field()
    platform = scrapy.Field()
    fork_id = scrapy.Field()
    create_time = scrapy.Field()
    user_id = scrapy.Field()
    fork_full_name = scrapy.Field()


class RepoStarItem(scrapy.Item):
    repo_id = scrapy.Field()
    user_id = scrapy.Field()
    platform = scrapy.Field()
    star_time = scrapy.Field()

