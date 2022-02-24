# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import urllib3
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
import random

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

user_agent = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36'
GitHub_accept = 'application/vnd.github.v3.star+json'###这里统一用vnd.github.v3.star，其实对star以外的相当于是vnd.github.v3+json
Gitee_accept = 'application/json'
# Connection = 'close'
GitHub_auth ="token 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"
# GitHub_token_list =[
#     "token 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",
#     "token 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",
#     "token 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"
# ]
Gitee_auth="token bb26a62f4d4f635b8ef23c399e33c0c3"
headers = [
            urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'cit-bot1:sjtucit1'),
            urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'cit-bot2:sjtucit2'),
            urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'cit-bot3:sjtucit3'),
            urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'cit-bot4:sjtucit4'),
            urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'cit-bot5:sjtucit5'),
            urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'cit-bot6:sjtucit6'),
            urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'cit-bot7:sjtucit7'),
            urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'jiangsha1007:js19851007851007')]


class MyUserAgentMiddleware(UserAgentMiddleware):
    '''
    设置User-Agent
    '''

    def __init__(self, user_agent):
        super().__init__(user_agent)
        self.user_agent = user_agent

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            user_agent=crawler.settings.get('MY_USER_AGENT')
        )

    def process_request(self, request, spider):
        agent = random.choice(headers)
        if spider.name == 'GitHub_addition':
            agent['Authorization'] = GitHub_auth
            agent['Accept'] = GitHub_accept
        else:   #Gitee情况，暂未考虑
            agent['Authorization'] = Gitee_auth
            agent['Accept'] = Gitee_accept
        request.headers.update(agent)


class AdditionspiderSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class AdditionspiderDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
