# This python file is used to test current rate limits of the tokens in file "request_header.py"
from data_crawl_spider.dataCrawler.request_header import *

if __name__ == '__main__':
    url = 'https://api.github.com/'
    for i in range(GitHub_token_number):
        head_json = get_html_json(url=url,header= getGitHubHeader(i),verify=False)[1]
        print('index = '+str(i)+'\t'+'X-RateLimit-Remaining = '+head_json['X-RateLimit-Remaining'])
