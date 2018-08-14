from DB import mysql
from Crawler import base
import sys
import re

def getProxy():
    from Helper import proxy
    proxy.run()

def getStation():
    from Crawler import station
    station.getStation()

def updatePlatformMap():
    from Crawler import mgzf
    mgzf.getMap()

def getList():
    from Crawler import mgzf
    mgzf.run()


def getDetail():
    from Crawler import mgzf
    mgzf.updateRoomInfo()

if __name__ == '__main__':
    command =  sys.argv[0]
    if len(sys.argv) == 1:
        pass
    elif sys.argv[1] == 'proxy':
        getProxy()
    elif sys.argv[1] == 'station':
        getStation()
    elif sys.argv[1] == 'platform_map':
        updatePlatformMap()
    elif sys.argv[1] == 'list':
        getList()
    elif sys.argv[1] == 'detail':
        getDetail()
