import re
import time
from DB import mysql
from Crawler import base

# 抓取代理网站的链接
def run():
    proxy_crawlers = getProxyUrls()
    for key, value in proxy_crawlers.items():
        if key == 'xicidaili':
            print ('开始抓去西刺代理')
            for url in value:
                runXiciProxy(url)
                time.sleep(30)

def getProxyUrls():
    return {'xicidaili':
                ['http://www.xicidaili.com/nn/',
                'http://www.xicidaili.com/nt/',
                'http://www.xicidaili.com/wn/',
                'http://www.xicidaili.com/wt/']
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
        record = mysqldb.fetchALL('proxy_pool', condition)
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
