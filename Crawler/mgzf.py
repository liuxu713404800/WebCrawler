# 蘑菇租房
import os
import re
import json
from Crawler import base
from DB import mysql
from Helper import common

# 抓取网上列表，以字典形式返回
def getMap():
    file_name = 'mgzf_data.txt'
    file = os.getcwd() + '/Output/' + file_name
    if os.path.exists(file):
        content = common.getFileContents(file_name)
        dict = json.loads(content)
    else:
        file_name = 'mgzf_html.txt'
        file = os.getcwd() + '/Output/' + file_name
        if os.path.exists(file):
            content = common.getFileContents(file_name)
        else:
            url = 'http://bj.mgzf.com/map'#蘑菇租房题图map
            crawler = base.webRequest(url, '', '', '', 0)
            data = crawler.run()
            content = data.text
            common.outputToFile('mgzf_html.txt', content)
        tinydata = re.sub(r' |\t|\r|\n|\f|\v', '', content)
        pattern = '<divclass="row-blockrow-block-subway">(.+?)<divclass="clear"></div>'
        all_contents = re.search(pattern, tinydata)
        pattern = '<spanclass="item">(.*?)</div></span>'
        subway_contents = re.findall(pattern, all_contents.group(1))
        dict = {}
        for value in subway_contents:
            pattern = '<ahref="(.+?)"code="(.+?)"type="(.+?)"data-id="(\d+)".+?>(.*?)</a>'
            subway_station = re.findall(pattern, value)
            subway = ''
            list = []
            for node in subway_station:
                if (node[2] == 'subway'):
                    subway = node[4]
                    dict[subway] = {
                        'id': node[3],
                        'name': node[4],
                        'mark': node[1],
                    }
                elif (node[2] == 'station'):
                    tmp_dict = {
                        'id': node[3],
                        'name': node[4],
                        'mark': node[1],
                    }
                    list.append(tmp_dict)
            dict[subway]['stations'] = list
        common.outputToFile('mgzf_data.txt', json.dumps(dict))
    # 整理一下数据
    # sortStation(dict)
    # sys_stations = common.getDiffStations(dict)
    sys_stations = common.getSystemStations()
    print(sys_stations)
    return dict

# 整理成需要的形式
def sortStation(dict):
    file_name = 'mgzf_station.txt'
    file = os.getcwd() + '/Output/' + file_name
    if os.path.exists(file):
        content = common.getFileContents(file_name)
        return
    else:
        print(dict)
    return

# 得到真实的信息
def getRealStation(station):
    map = {
        '海定黄庄': '海淀黄庄',
        '柯木塱': None,
        '垈头': '垡头',
        'T2航站楼': '2号航站楼',
        'T3航站楼': '3号航站楼',
        '稻香湖': '稻香湖路'
    }

    if station in map.keys():
        return map[station]
    else:
        return station
