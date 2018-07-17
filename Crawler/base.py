import requests
import urllib
import common
import re
import proxy

class webRequest:

    # 创建默认对象值
    def __init__(self, url = '', params = {}, header = {}, http_fun = 'GET', proxy = 1, coding = 'utf-8'):
        #将个变量赋值给对象
        self.url = url
        self.params = params
        self.header = header
        if http_fun == '':
            self.http_fun = 'GET'
        else:
            self.http_fun = http_fun
        self.proxy = proxy
        if coding == '':
            self.coding = 'utf-8'
        else:
            self.coding = coding

    def run(self):
        # 简单校验url
        if re.search(r'(https|ftp)s{0,1}://.+', self.url, re.I) is None:
            raise RuntimeError('url不合法')

        # 存在header，则使用header，否则使用默认header
        if self.header:
            pass
        else:
            self.header = common.commonHeader()

        # 是否使用代理
        if self.proxy == 1:
            pass
            # todo 从自己的代理池中抓一个
        else
            self.proxy = {}

        if self.http_fun == 'GET':
            request = requests.get(self.url, params = self.params, headers = self.header,  proxies = self.proxy)
        elif self.http_fun == 'POST':
            request = requests.post(self.url, params = self.params, headers = self.header,  proxies = self.proxy)
        else:
            raise RuntimeError('暂不支持该HTTP方法')

        request.encoding = self.coding
        return request
