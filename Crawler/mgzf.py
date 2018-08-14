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

def run():
    file_name = 'mgzf_station.txt'
    file = os.getcwd() + '/Output/' + file_name
    if os.path.exists(file):
        base_url = 'http://bj.mgzf.com/list'
        content = common.getFileContents(file_name)
        dict = json.loads(content)
        point = False
        for key, value in dict.items():
            for station in value:
                if station['name'] == '东直门' and point == False:
                    point = True
                if point == False:
                    continue

                total_page = 1
                current_page = 1
                while current_page <= total_page:
                    url = base_url + '/' + station['platform_subway_mark'] + '/' + station['mark']
                    data = crawlerPolicy(url, {'page': current_page}, '', 'POST')
                    # 解析
                    if data:
                        total_page = data['totalPage']
                        for room in data['roomInfos']:
                            jsonListSave(room, station['sys_station_id'])
                        info = "Crawler " + station['platform_subway_name'] + ' ' +station['name'] + ' ' + str(current_page) + " page info finished"
                        print (info)
                    else:
                        info = "Can't crawler " + station['platform_subway_name'] + ' ' +station['name'] + ' ' + str(current_page) + " page info"
                        print (info)
                        continue
                    current_page += 1
                    time.sleep(random.randint(3,8))
    else:
        raise RuntimeError('没有基础地铁信息，请先执行基础数据爬取')

def getRoomDetail(room_id):
    mysqldb = mysql.MysqlDB()
    condition = {'id': room_id}
    room = mysqldb.fetchOne('room', condition)
    url = 'http://bj.mgzf.com/room/' + str(room['room_id']) + '.shtml?page=list&sourceType=' + str(room['compound_type'])
    data = crawlerPolicy(url, {}, {}, 'GET', 'detail')
    return data, room_id

# 创建抓取策略
def crawlerPolicy(url = '', params = {}, headers = {}, method = 'POST', type = 'list'):
    count = 0
    flag = False
    # 首先尽可能多多使用代理，检验代理质量
    while (count < 10):
        proxy = common.getOneProxy()
        format_proxy = common.getFormatProxy(proxy)
        data = tryCrawler(url, params, '', method, format_proxy, type)
        # 更新代理质量，并且失败情况下获得一个新的代理
        if data:
            flag = True
            break
        else:
            count += 1

    # 如果十次都失败了，那么只能说是这几个代理人品不好，尝试用高质量的代理进行抓取
    if flag == False:
        count = 0
        while (count < 10):
            proxy = common.getHighQualityProxy()
            format_proxy = common.getFormatProxy(proxy)
            data = tryCrawler(url, params, '', method, format_proxy, type)
            if data:
                break
            else:
                count += 1
    # 如果还是失败了，放弃这个房间的抓取吧，直接返回False
    return data

# 尝试抓取
def tryCrawler(url = '', params = {}, headers = {}, method = 'POST', proxy = {}, type = 'list'):
    # crawler = base.webRequest(url, params, headers, method, proxy)
    # cookie = crawler.getCookie()
    # if cookie == False:
    #     return False
    add_headers = {
        # 'Cookie': cookie,
        'Host': 'bj.mgzf.com',
    }

    headers = common.customHeader(add_headers)
    crawler = base.webRequest(url, params, headers, method, proxy)
    data = crawler.run()
    proxy = common.getDbProxy(proxy)
    if data == False:
        common.proxyCallback(proxy, 0)
        return False
    elif data.status_code == requests.codes.ok:
        common.proxyCallback(proxy, 1)
    else:
        common.proxyCallback(proxy, 0)
        return False
    if type == 'list':
        # 如果能够正常解析，说明代理有效果
        try:
            content = json.loads(data.text)
        except ValueError as e:
            content = False
    elif type == 'detail':
        tinydata = re.sub(r' |\t|\r|\n|\f|\v', '', data.text)
        ret = re.search(r'<title>Servererror</title>', tinydata)
        if ret:
            return True
        else:
            ret = re.search(r'functionreload', tinydata)
            if ret:
                return False
            else:
                ret = re.search(r'window.__NUXT__=(.*?);</script>', tinydata)
                content = json.loads(ret.group(1))
    return content

# 列表页数据整理和存储
def jsonListSave(dict = {}, station_id = 0):
    if dict['rentType']['key'] == 2:
        rent_type = 1
    else:
        rent_type = 0

    commute_info = ''
    for value in dict['metroInfo']:
        commute_info += value + ';'

    # 支付方式如果能找到押一付一，则写押一付一，否则写押一付三，暂时先这么处理
    if dict['monthlyPay'] == 1:
        pay_method = '押一付一'
    else:
        pay_method = '押一付三'

    img_name = common.getStrMd5(dict['image'])
    res = common.downloadImage('mgzf', img_name, dict['image'])

    data = {
        'source': 3,
        'room_id': dict['roomId'],
        'name': dict['title'],
        'room_type': dict['nickName'],
        'rent_type': rent_type,
        'compound_name': dict['comName'],
        'compound_type': dict['flatTag'],
        'district': dict['districtName'],
        'price': dict['showPrice'],
        'brief_info': dict['customTitle'],
        'commute_info': commute_info,
        'pay_method': pay_method,
        'publish_info': dict['lastPublishTimeText'],
        'image_info': img_name,
        'station_ref': station_id
    }
    mysqldb = mysql.MysqlDB()
    condition = {'room_id': dict['roomId']}
    res = mysqldb.fetchAll('room', condition)
    if res:
        ret = mysqldb.update('room', data, condition)
    else:
        ret = mysqldb.insert('room', data)
    return ret

def jsonDetailSave(dict = {}, sys_room_id = 0):
    condition = {'id': sys_room_id}
    data = {}
    if dict == True or dict == False:
        data = {
            'rented': 1,
        }
        mysqldb = mysql.MysqlDB()
        res = mysqldb.update('room', data, condition)
        return res

    if dict['data'][0]['basicInfo']:
        room_info = dict['data'][0]['basicInfo']['roomIntroAttrDTO']
        # data['price'] = room_info['minAmount']
        data['detail_info'] = room_info['roomDesc']
        data['pay_method'] = room_info['payTypes'][0]['payDisplayValue']
        data['foregift'] = room_info['payTypes'][0]['foregiftAmount']
        if room_info['rentStatusVal'] == 1 or room_info['rentStatusName'] == '未出租':
            data['rented'] = 0
        else:
            data['rented'] = 1

        room_conf = dict['data'][0]['basicInfo']['roomDetailConfig']
        for value in room_conf:
            if value['groupName'] == 'unitType':
                data['house_type'] = value['value']
            elif value['groupName'] == 'area':
                data['room_area'] = float(re.sub("[^\d.]", "", value['value']))
            elif value['groupName'] == 'floor':
                data['floor_number'] = value['value']

        decoration = ''
        if 'roomConfig' in dict['data'][0]['roomConfig'].keys():
            for value in dict['data'][0]['roomConfig']['roomConfig']:
                decoration += value['value'] + ','
                data['decoration'] = decoration[:-1]
        mysqldb = mysql.MysqlDB()
        res = mysqldb.update('room', data, condition)
        return res
    else:
        return False

# 得到所有未出租的房子
def getAllUnrentedRooms():
    mysqldb = mysql.MysqlDB()
    condition = {'rented': 0}
    res = mysqldb.fetchAllIds('room', condition)
    return res

def updateRoomInfo():
    ids = getAllUnrentedRooms()
    for value in ids:
        data, sys_room_id = getRoomDetail(value['id'])
        res = jsonDetailSave(data, sys_room_id)
        time.sleep(random.randint(3,5))


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
