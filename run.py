
from DB import mysql

if __name__ == '__main__':
    mysqldb = mysql.MysqlDB()
    condition = {"success": 1, "failed": 2}
    data = mysqldb.fetchALL('proxy_pool', condition)
    print(data)
