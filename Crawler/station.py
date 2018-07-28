import re
import os
from Crawler import base
from DB import mysql
from Helper import common

# 抓取网上列表，以字典形式返回
def getStation():
    file_name = 'subway_xml.txt'
    file = os.getcwd() + '/Output/' + file_name
    if os.path.exists(file):
        content = common.getFileContents(file_name)
    else:
        url = 'http://map.bjsubway.com:8080/subwaymap2/public/subwaymap/beijing.xml'#北京地铁官网
        crawler = base.webRequest(url, '','', '', 0)
        data = crawler.run()
        content = data.text
        common.outputToFile('subway_xml.txt', content)
    tinydata = re.sub(r' |\t|\r|\n|\f|\v', '', content)
    pattern = '<llid="(.*?)</l>'
    ret = re.findall(pattern, tinydata)
    map = {}
    sub_id = 1
    for value in ret:
        pattern = 'lb="(.+?)"i="(\d+)"'
        subway = re.search(pattern, value)
        pattern = '<pn="(\d+?)"acc="(\d+?)"lb="(.+?)"'
        stations = re.findall(pattern, value)
        list = []
        for station in stations:
            list.append(station[2])
        map[sub_id] = {'name':subway.group(1), 'stations': list}
        sub_id += 1
    saveStation(map)
    return map

def saveStation(map):
    station_count = 0
    subway_count = 0
    relation_count = 0
    mysqldb = mysql.MysqlDB()
    for key, value in map.items():
        # 完成地铁线路的保存
        dict = {
            'id': key,
            'name': value['name']
        }
        res = mysqldb.save('subway', dict)
        subway_count += 1
        for station in value['stations']:
            # 保存地铁站点
            data = station_condition = {'name': station}
            db_station = mysqldb.fetchOne('station', station_condition)
            if db_station:
                station_id = db_station['id']
            else:
                res = mysqldb.save('station', data)
                db_station = mysqldb.fetchOne('station', station_condition)
                station_id = db_station['id']
                station_count += 1

            # 保存关系
            data = relation_condition = {'station_id': station_id, 'subway_id': key}
            db_relation = mysqldb.fetchOne('subway_station', relation_condition)
            if db_relation:
                pass
            else:
                res = mysqldb.save('subway_station', data)
            relation_count += 1
    print('subway:' + str(subway_count))
    print('station:' + str(station_count))
    print('relation:' + str(relation_count))
