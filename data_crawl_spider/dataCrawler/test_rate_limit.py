# This python file is used to test current rate limits of the tokens in file "request_header.py"
from data_crawl_spider.dataCrawler.request_header import *
import time

def testRateLimit():
    url = 'https://api.github.com/'
    for i in range(GitHub_token_number):
        head_json = get_html_json(url=url,header= getGitHubHeader(i),verify=False)[1]
        print('index = '+str(i)+'\t'+'X-RateLimit-Remaining = '+head_json['X-RateLimit-Remaining'])


def getRateLimitPeriodly(frequency):
    while True:
        url = 'https://api.github.com/'
        for i in range(GitHub_token_number):
            head_json = get_html_json(url=url, header=getGitHubHeader(i), verify=False)[1]
            print('time = '+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))+'index = ' + str(i) + '\t' + 'X-RateLimit-Remaining = ' + head_json['X-RateLimit-Remaining'])
        time.sleep(frequency)


if __name__ == '__main__':
    testRateLimit()
    # getRateLimitPeriodly(5)