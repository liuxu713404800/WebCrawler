import re
import time
import random
from DB import mysql
from Crawler import base

# 抓取代理网站的链接
def run():
    proxy_crawlers = getProxyUrls()
    for key, value in proxy_crawlers.items():
        if key == 'xicidaili':
            print ('开始抓取西刺代理')
            for url in value:
                runXiciProxy(url)
                time.sleep(random.randint(20,30))
        elif key == 'kuaidaili':
            print ('开始抓取快代理')
            for url in value:
                runKuaiProxy(url)
                time.sleep(random.randint(20,30))

# 
def getProxyUrls():
    return {
            'xicidaili':
                ['http://www.xicidaili.com/nn/1',
                'http://www.xicidaili.com/nn/2',
                'http://www.xicidaili.com/nn/3',
                'http://www.xicidaili.com/nn/4',
                'http://www.xicidaili.com/nn/5',
                'http://www.xicidaili.com/nn/6',
                'http://www.xicidaili.com/nn/7',
                'http://www.xicidaili.com/nn/8',
                ],
            'kuaidaili':
                ['https://www.kuaidaili.com/free/inha/1/',
                'https://www.kuaidaili.com/free/inha/2/',
                'https://www.kuaidaili.com/free/inha/3/',
                'https://www.kuaidaili.com/free/inha/4/',
                'https://www.kuaidaili.com/free/inha/5/',
                'https://www.kuaidaili.com/free/inha/6/',
                'https://www.kuaidaili.com/free/inha/7/',
                'https://www.kuaidaili.com/free/inha/8/',
                'https://www.kuaidaili.com/free/inha/9/',
                'https://www.kuaidaili.com/free/inha/10/',
                ]
            }

# 抓取西刺代理的代理ip
def runXiciProxy(url):
    mysqldb = mysql.MysqlDB()
    crawler = base.webRequest(url, '','', '', 0)
    data = crawler.run()
    tinydata = re.sub(r' |\t|\r|\n|\f|\v', '', data.text)
    ret = re.findall(r'<trclass="(odd)?">(.*?)</tr>', tinydata)
    count = 0
    for value in ret:
        content = value[1]
        # 截取相关内容
        pattern = '<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td><td>(\d{1,5})</td>'
        res = re.search(pattern, content)
        ip = res.group(1)
        port = res.group(2)
        pattern = '<td>(HTTPS?)</td><tdclass="country">'
        res = re.search(pattern, content)
        type = res.group(1)

        # 检查该ip否存在，不存在新增，存在更新
        condition = {'ip': ip}
        record = mysqldb.fetchAll('proxy_pool', condition)
        if record:
            data = {'updated': int(time.time())}
            record = mysqldb.update('proxy_pool', data, condition)
        else:
            data = {
                'created': int(time.time()),
                'updated': int(time.time()),
                'ip': ip,
                'port': port,
                'type': type
            }
            record = mysqldb.insert('proxy_pool', data)
        count += 1
    print('完成了来自于 ' + url + ' 的' + str(count) + '条代理的抓取')


# 抓取西刺代理的代理ip
def runKuaiProxy(url):
    mysqldb = mysql.MysqlDB()
    crawler = base.webRequest(url, '','', '', 0)
    data = crawler.run()
    tinydata = re.sub(r' |\t|\r|\n|\f|\v', '', data.text)
    ret = re.findall(r'<tr><tddata-title="IP">(.*?)</tr>', tinydata)

    count = 0
    for value in ret:
        content = value
        # 截取相关内容
        pattern = '(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td><tddata-title="PORT">(\d{1,5})</td>'
        res = re.search(pattern, content)
        ip = res.group(1)
        port = res.group(2)
        pattern = '(HTTPS?)</td><tddata-title='
        res = re.search(pattern, content)
        type = res.group(1)
        # 检查该ip否存在，不存在新增，存在更新
        condition = {'ip': ip}
        record = mysqldb.fetchAll('proxy_pool', condition)
        if record:
            data = {'updated': int(time.time())}
            record = mysqldb.update('proxy_pool', data, condition)
        else:
            data = {
                'created': int(time.time()),
                'updated': int(time.time()),
                'ip': ip,
                'port': port,
                'type': type
            }
            record = mysqldb.insert('proxy_pool', data)
        count += 1
    print('完成了来自于 ' + url + ' 的' + str(count) + '条代理的抓取')
