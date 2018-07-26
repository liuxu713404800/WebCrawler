# 蘑菇租房
import os
import re
from Crawler import base
from DB import mysql
from Helper import common

def mgHeader():
    return common.customHeader({
    'Cookie':'UM_distinctid=164bd14e2d95d-06808d4fc6b97f-5e452019-144000-164bd14e2daac7; gr_user_id=7a913461-51d3-4678-9858-6329ccb141af; grwng_uid=41ad3824-f703-4131-9a6d-966e4e67a8db; mgzf-guid-sign=66d19dd82a8dec696ae9eb6cc30fb91e; mgzf-guid-name=2c35bf9eff6fcbcbed4462260147b330; mogo_bottomAdvInfo={%22isShowBottomAdv%22:false%2C%22expires%22:1}; acw_tc=AQAAAMftRB8/nQkAycN5e/U8uJD0MErn; JSESSIONID=980587dd-e0af-44bf-b95c-be5e6e4f5d14; SESSION=980587dd-e0af-44bf-b95c-be5e6e4f5d14; CNZZDATA1253147438=820277291-1532175301-http%253A%252F%252Fwww.mgzf.com%252F%7C1532524931; acw_sc__=5b58ac91ea3cd301c2553991b05d5fafbdcd1990','Host': 'bj.mgzf.com'})

# 抓取网上列表，以字典形式返回
def getMap():
    file_name = 'mgzf.txt'
    file = os.getcwd() + '/Output/' + file_name
    if os.path.exists(file):
        dict = common.getFileContents(file_name)
    else:
        header = mgHeader()
        url = 'http://bj.mgzf.com/map'#蘑菇租房题图map
        crawler = base.webRequest(url, '', header, '', 0)
        data = crawler.run()
        tinydata = re.sub(r' |\t|\r|\n|\f|\v', '', data.text)
        pattern = '<divclass="row-blockrow-block-subway">(.+?)<divclass="clear"></div>'
        all_contents = re.search(pattern, tinydata)
        pattern = '<spanclass="item">(.*?)</div></span>'
        subway_contents = re.findall(pattern, all_contents.group(1))

        dict = {}
        for value in subway_contents:
            pattern = 'color="#[\d\w]{6}">(.+?)</a>'
            subway_station = re.findall(pattern, value)
            if subway_station:
                subway = subway_station.pop(0)
                dict[subway] = subway_station
            else:
                print(subway_station)
        common.outputToFile('mgzf.txt', dict)
    return dict

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
