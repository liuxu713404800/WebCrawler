# 蘑菇租房
import os
import re
import json
import time
import random
import requests
from Crawler import base
from DB import mysql
from Helper import common

# 获得平台的地铁信息
def getPlatformSubway():
    file_name = 'bkzf_platform_subway.txt'
    file = os.getcwd() + '/Output/' + file_name
    if os.path.exists(file):
        content = common.getFileContents(file_name)
        platform_subway = json.loads(content)
        return platform_subway
    else:
        url = 'https://bj.zu.ke.com/zufang/'
        requset = base.webRequest(url)
        data = requset.run()
        tinydata = re.sub(r' |\t|\r|\n|\f|\v', '', data.text)
        subways = re.findall(r'<lidata-id="(\d+?)"data-type="line"class="filter__item--level2"><ahref="/ditiezufang/(.+?)/">(.+?)</a></li>', tinydata)
        common.outputToFile('bezf_platform_subway.txt', json.dumps(subways))
        return subways

# 获得平台的地铁站信息
def getPlatformStation():
    file_name = 'bkzf_platform_station.txt'
    file = os.getcwd() + '/Output/' + file_name
    if os.path.exists(file):
        content = common.getFileContents(file_name)
        platform_station = json.loads(content)
        return platform_station
    else:
        subways = getPlatformSubway()
        platform_station = {}
        for subway in subways:
            url = 'https://bj.zu.ke.com/ditiezufang/' + subway[1]
            requset = base.webRequest(url)
            data = requset.run()
            tinydata = re.sub(r' |\t|\r|\n|\f|\v', '', data.text)
            subway_stations = re.findall(r'<lidata-id="(\d+?)"data-type="station"class="filter__item--level3"><ahref="/ditiezufang/([\d\w]+?)/">(.+?)</a></li>', tinydata)
            platform_station[subway[1]] = subway_stations
        common.outputToFile('bkzf_platform_station.txt', json.dumps(platform_station))
        return platform_station

# 平台地铁与系统地铁之间的映射关系
def subwayMap(platform_subway_id):
    map = {
        'li647': 1,
        'li648': 2,
        'li656': 3,
        'li649': 4,
        'li46107350': 5,
        'li46537785': 6,
        'li659': 7,
        'li43145267': 8,
        'li651': 9,
        'li652': 10,
        'li46461179': 12,
        'li1110790465974155': 11,
        'li43143633': 13,
        'li1116796246117001': 14,
        'li653': 15,
        'li43144847': 18,
        'li43144993': 17,
        'li43145111': 16,
        'li654': 22,
        'li1120027908698063': 19,
        'li1120028159353771': 20,
        'li1120028158304639': 21,
    }
    return map[platform_subway_id]

# 平台地铁与系统站点之间的映射关系
def stationMap(platform_station):
    map = {
        'li659s46538215': None,
        'li659s47245768': None,
        'li659s46538136': None,
        'li659s46538039': None,
        'li659s46538038': None,
        'li659s46538037': None,
        'li659s46538036': None,
        'li659s46538035': None,
        'li659s46538034': None,
        'li659s46538033': None,
        'li46461179s46537872': None,
        'li43144847s53186125': None,
        'li654s43144824': (316, '3号航站楼'),
        'li654s43144825': (317, '2号航站楼'),
    }
    if platform_station[1] in map:
        return map[platform_station[1]]
    else:
        mysqldb = mysql.MysqlDB()
        condition = {'name': platform_station[2]}
        res = mysqldb.fetchOne('station', condition)
        return (res['id'], res['name'])

# 获得标准地铁站信息
def getStandardStation():
    file_name = 'bkzf_standard_station.txt'
    file = os.getcwd() + '/Output/' + file_name
    if os.path.exists(file):
        content = common.getFileContents(file_name)
        standard_station = json.loads(content)
        return standard_station
    else:
        standard_stations = {}
        platform_stations = getPlatformStation()
        for subway, subway_station in platform_stations.items():
            system_subway_id = subwayMap(subway)
            standard_stations[system_subway_id] = []
            for station in subway_station:
                system_station = stationMap(station)
                if system_station:
                    res = {'system_station_id': system_station[0], 'platform_station_id': station[1], 'name': system_station[1], 'platform_subway': subway}
                    standard_stations[system_subway_id].append(res)
                else:
                    continue
        common.outputToFile('bkzf_standard_station.txt', json.dumps(standard_stations))
        return standard_stations
