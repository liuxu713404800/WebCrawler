# 这是一些常用的公用方法
import os
import random
import json
import re
import requests as req
import hashlib
from DB import mysql

# 对于需要改变header的场景，可以自定义，也可以使用我的方法
def customHeader(custom_header = {}):
    common_header = commonHeader()
    for key, value in custom_header.items():
        # value值为-1，表明希望删除键值
        if value == -1:
            del common_header[key]
        # 原来键值存在，替换成新的
        elif key in common_header:
            common_header[key] = value
        # 原来键值不存在，新增
        else:
            common_header[key] = value
    return common_header

# 公用的header
def commonHeader():
    user_agent = randomUA()
    header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": user_agent
    }
    return header

# 获得随机的UA
def randomUA():
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240",
    ]
    return random.choice(ua_list)

# 根据一定规则选择出代理
def getOneProxy():
    sql = 'select * from proxy_pool order by failed asc, success desc limit 10;'
    mysqldb = mysql.MysqlDB()
    res = mysqldb.query(sql)
    return random.choice(res)

# 返回字典结构的代理
def getFormatProxy(proxy = {}):
    if proxy:
        format_proxy = {proxy['type']: proxy['type'] + "://" + proxy['ip'] + ':' + str(proxy['port']) + '/'}
    else:
        format_proxy = {}
    return format_proxy

# 根据格式化代理找到数据库中这条代理的信息
def getDbProxy(proxy = {}):
    for key, value in proxy.items():
        ip_port = value.split('/')[2]
        ip = ip_port.split(':')[0]
        condition = {'ip': ip}
    mysqldb = mysql.MysqlDB()
    proxy = mysqldb.fetchOne('proxy_pool', condition)
    return proxy

# 选出高质量的代理
def getHighQualityProxy():
    sql = 'select * from proxy_pool order by success desc limit 10;'
    mysqldb = mysql.MysqlDB()
    res = mysqldb.query(sql)
    return random.choice(res)

# 根据一定规则选择出代理
def proxyCallback(proxy = {}, result = 1):
    success = proxy['success']
    failed = proxy['failed']
    if result == 1:
        success += 1
    else:
        failed += 1
    mysqldb = mysql.MysqlDB()
    data = {
        'success': success,
        'failed':failed
    }
    condition = {'id': proxy['id']}
    res = mysqldb.update('proxy_pool', data, condition)
    return res

#爬取图片下载
def downloadImage(folder, file, url):
    path = os.getcwd()
    folder = path + '/Images/' + folder
    if os.path.exists(folder):
        pass
    else:
        os.mkdir(folder)
    postfix = getImagePostfix(url)
    file = folder + '/' + file + '.' + postfix
    proxy = getOneProxy()
    format_proxy = getFormatProxy(proxy)
    response = req.get(url, proxies = format_proxy)
    img = response.content
    with open(file, 'wb') as f:
        f.write(img)

# 获得图片的后缀
def getImagePostfix(str):
    res = re.search('.*.(jpg|png|jpeg|gif).*', str, re.I)
    if res:
        return res.group(1)
    else:
        # raise RuntimeError('无法获得图片后缀，请检查！！！')
        return 'jpg'

# 获得字符串的md5值
def getStrMd5(str):
    h = hashlib.md5()
    h.update(str.encode(encoding='utf-8'))
    return h.hexdigest()


#输入输出到文件
def outputToFile(file, content):
    path = os.getcwd()
    file = path + '/Output/' + file
    f = open(file,'w')
    f.write(content)
    f.close()

def getFileContents(file):
    path = os.getcwd()
    file = path + '/Output/' + file
    f = open(file, 'r')
    content = f.read()
    f.close()
    return content

# 得到系统的地铁站信息
def getSystemStations():
    mysqldb = mysql.MysqlDB()
    stations = mysqldb.fetchAll('station')
    dict = {}
    for value in stations:
        dict[value['name']] = value['id']
    return dict

# 得到平台数据与系统的差别
def getDiffStations(dict):
    sys_stations = getSystemStations()
    list = sys_stations.keys()

    # 获取平台的名称
    mg_stations = []
    for key, value in dict.items():
        for station in value['stations']:
            mg_stations.append(station['name'])

    # 输出不同
    for value in mg_stations:
        if value in list:
            pass
        else:
            print(value)
