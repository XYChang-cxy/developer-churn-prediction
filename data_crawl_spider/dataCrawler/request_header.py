import urllib3
import random
import requests
import traceback
import json
requests.packages.urllib3.disable_warnings() #request忽略http验证(verify=False)时消除警告
requests.adapters.DEFAULT_RETRIES = 5 #默认重试次数

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
GitHub_accept = 'application/vnd.github.v3+json'
Gitee_accept = 'application/json'
Connection = 'close'
GitHub_token_list =[
    "token xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "token xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "token xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
]
GitHub_token_number = 3
Gitee_auth="token xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
headers = [
            urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'cit-bot1:sjtucit1'),
            urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'cit-bot2:sjtucit2'),
            urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'cit-bot3:sjtucit3'),
            urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'cit-bot4:sjtucit4'),
            urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'cit-bot5:sjtucit5'),
            urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'cit-bot6:sjtucit6'),
            urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'cit-bot7:sjtucit7')]
# for header in headers:
#     header['Connection'] = Connection
#     # header['Authorization'] = GitHub_auth
#     # header['Authorization'] = Gitee_auth


def getGitHubHeader(token_index):
    header = headers[random.randint(0, len(headers)-1)]
    header['Connection'] = Connection
    header['Authorization'] = GitHub_token_list[token_index]
    header['Accept'] = GitHub_accept
    return header


def getGitHubStarHeader(token_index):#用于github中moose_star数据的爬取
    header = headers[random.randint(0, len(headers)-1)]
    header['Connection'] = Connection
    header['Accept'] = 'application/vnd.github.v3.star+json'#使用vnd.github.v3.star可以获取到starred_at信息
    header['Authorization'] = GitHub_token_list[token_index]
    return header


def getGiteeHeader():
    header = headers[random.randint(0, len(headers) - 1)]
    header['Connection'] = Connection
    header['Authorization'] = Gitee_auth
    header['Accept'] = Gitee_accept
    return header


def get_html_json(url, header,verify=True):
    try:
        if verify == False:
            response = requests.get(url, headers=header, verify=False)
        else:
            response = requests.get(url, headers=header)
        text_info = response.text
        text_json = json.loads(text_info)
        head_info = response.headers
        return text_json, head_info, response.status_code
    except:
        traceback.print_exc()