import requests
import re
from Helper import common
from Helper import proxy
from DB import mysql

class webRequest:
    # 创建默认对象值
    def __init__(self, url = '', params = {}, header = {}, http_fun = 'GET', proxy = 0, coding = 'utf-8'):
        #将个变量赋值给对象
        self.url = url
        if params == '':
            self.params = {}
        else:
            self.params = params

        if header == '':
            self.header = {}
        else:
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
        if re.search(r'(http|ftp)s{0,1}://.+', self.url, re.I) is None:
            raise RuntimeError('url不合法')

        # 存在header，则使用header，否则使用默认header
        if self.header:
            pass
        else:
            self.header = common.commonHeader()

        # 是否使用代理
        if self.proxy == 0 or self.proxy == '':
            self.proxy = {}

        if self.http_fun == 'GET':
            try:
                request = requests.get(self.url, params = self.params, headers = self.header,  proxies = self.proxy)
            except:
                return False
        elif self.http_fun == 'POST':
            try:
                request = requests.post(self.url, params = self.params, headers = self.header,  proxies = self.proxy)
            except:
                return False
        else:
            raise RuntimeError('暂不支持该HTTP方法')

        request.encoding = self.coding
        return request

    def getCookie(self):
        # 获取数据库的代理信息
        proxy = common.getDbProxy(self.proxy)
        # 更新代理质量，失败返回下FALSE
        try:
            if self.http_fun == 'GET':
                headers = requests.get(self.url, params = self.params, headers = self.header,  proxies = self.proxy).headers
            elif self.http_fun == 'POST':
                headers = requests.post(self.url, params = self.params, headers = self.header,  proxies = self.proxy).headers
            common.proxyCallback(proxy, 1)
        except Exception as err:
            common.proxyCallback(proxy, 0)
            return False

        setCookie = headers['Set-Cookie']
        content = re.sub(r' |\t|\r|\n|\f|\v', '', setCookie)
        content = content.split(';')
        reject_values = ['Path=/', 'HttpOnly']
        reject_keys = ['Domain', 'Expires', 'Path']
        cookie = ''
        for value in content:
            if value in reject_values:
                continue
            sub_value = value.split(',')
            for sub in sub_value:
                if '=' in sub:
                    one = sub.split('=')
                    if one[0] not in reject_keys:
                        cookie = cookie + sub + ';'
        return cookie[:-1]
