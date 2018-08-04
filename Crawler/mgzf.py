# 蘑菇租房
import os
import re
import json
from Crawler import base
from DB import mysql
from Helper import common

def run():
    file_name = 'mgzf_station.txt'
    file = os.getcwd() + '/Output/' + file_name
    if os.path.exists(file):
        base_url = 'http://bj.mgzf.com/list'
        content = common.getFileContents(file_name)
        dict = json.loads(content)
        proxy = common.getOneProxy()
        format_proxy = common.getFormatProxy(proxy)

        for key, value in dict.items():
            for station in value:
                count = 0
                url = base_url + '/' + station['platform_subway_mark'] + '/' + station['mark']
                # 尝试抓去3次
                while (count < 3):
                    data = tryCrawler(url, {'page': 1}, '', 'POST', format_proxy)
                    # 更新代理质量，并且失败情况下获得一个新的代理
                    if data:
                        common.proxyCallback(proxy, 1)
                        break
                    else:
                        common.proxyCallback(proxy, 0)
                        proxy = common.getOneProxy()
                        format_proxy = common.getFormatProxy(proxy)
                        count += 1
                # 解析
                if data:
                    for room in data['roomInfos']:
                        jsonListSave(room, station['sys_station_id'])
                else:
                    info = "Can't crawler url: " + url + " info"
                    print(info)
    else:
        raise RuntimeError('没有基础地铁信息，请先执行基础数据爬取')

# 列表页数据整理和存储
def jsonListSave(dict = {}, station_id = 0):
    if dict['nickName'] == '主卧':
        room_type = 1
    elif dict['nickName'] == '次卧':
        room_type = 2
    else:
        room_type = 0

    if dict['rentType']['key'] == 2:
        rent_type = 1
    else:
        rent_type = 0

    commute_info = ''
    for value in dict['metroInfo']:
        commute_info += value + ';'

    pay_method_map = {
        0: '押一付三',
        1: '押一付一',
        2: '信用租'
    }

    img_name = common.getStrMd5(dict['image'])
    res = common.downloadImage('mgzf', img_name, dict['image'])

    data = {
        'source': 3,
        'room_id': dict['roomId'],
        'name': dict['title'],
        'room_type': room_type,
        'rent_type': rent_type,
        'compound_name': dict['comName'],
        'compound_type': dict['flatTag'],
        'district': dict['districtName'],
        'price': dict['showPrice'],
        'brief_info': dict['customTitle'],
        'commute_info': commute_info,
        'pay_method': pay_method_map[dict['monthlyPay']],
        'publish_info': dict['lastPublishTimeText'],
        'image_info': img_name,
        'station_ref': station_id
    }
    mysqldb = mysql.MysqlDB()
    res = mysqldb.insert('room', data)

# 尝试抓取
def tryCrawler(url = '', params = {}, headers = {}, method = 'POST', proxy = {}):
    crawler = base.webRequest(url, params, headers, method, proxy)
    cookie = crawler.getCookie()
    add_headers = {
        'Cookie': cookie,
        'Host': 'bj.mgzf.com',
    }
    headers = common.customHeader(add_headers)
    crawler = base.webRequest(url, {'page': 1}, headers, 'POST', proxy)
    data = crawler.run()
    # 如果能够正常解析，说明代理有效果
    try:
        content = json.loads(data.text)
    except ValueError as e:
        content = False
    return content

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
    sortStation(dict)
    sys_stations = common.getSystemStations()
    return dict

# 整理成需要的形式
def sortStation(dict):
    mgzf_station = {}
    file_name = 'mgzf_station.txt'
    file = os.getcwd() + '/Output/' + file_name
    if os.path.exists(file):
        content = common.getFileContents(file_name)
        mgzf_station = json.loads(content)
    else:
        sys_stations = common.getSystemStations()
        # 将输入字段整理成以名字为key的字段
        for key, value in dict.items():
            subway_id = value['id']
            subway_name = value['name']
            subway_mark = value['mark']
            for station in value['stations']:
                station_name = getRealStation(station['name'])
                if station_name is None:
                    continue
                sys_station_id = sys_stations[station_name]
                station_info = {
                    'sys_station_id': sys_station_id,
                    'platform_id': station['id'],
                    'name': station_name,
                    'mark': station['mark'],
                    'platform_subway_id': subway_id,
                    'platform_subway_name': subway_name,
                    'platform_subway_mark': subway_mark,
                }
                if station_name not in mgzf_station.keys():
                    mgzf_station[station_name] = []
                mgzf_station[station_name].append(station_info)
        common.outputToFile(file_name, json.dumps(mgzf_station))
    return mgzf_station

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
