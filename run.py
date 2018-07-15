from DB import mysql
from Crawler import base

if __name__ == '__main__':
    mysqldb = mysql.MysqlDB()
    condition = {}
    #condition = {"success": 1, "failed": 2}
    data = mysqldb.fetchALL('proxy_pool', condition)

    crawler = base.webRequest()
