import re
from Crawler import base
from DB import mysql

def getStation():
    url = 'http://map.bjsubway.com:8080/subwaymap2/public/subwaymap/beijing.xml'#北京地铁官网
    mysqldb = mysql.MysqlDB()
    crawler = base.webRequest(url, '','', '', 0)
    data = crawler.run()
    tinydata = re.sub(r' |\t|\r|\n|\f|\v', '', data.text)
    pattern = '<llid="(.*?)</l>'
    ret = re.findall(pattern, tinydata)
    map = {}
    for value in ret:
        pattern = 'lb="(.+?)"i="(\d+)"'
        subway = re.search(pattern, value)
        print(subway.group(1))
        print(subway.group(2))
        pattern = '<pn="(\d+?)"acc="(\d+?)"lb="(.+?)"'
        stations = re.findall(pattern, value)
        list = []
        for station in stations:
            list.append(station[2])
        map[subway.group(2)] = {'name':subway.group(1), 'stations': list}
    print(map)
