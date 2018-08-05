import os
import sys
import configparser
import pymysql
import time

class MysqlDB:
    config = configparser.ConfigParser()
    config.read(os.path.split(os.path.realpath(__file__))[0] + "/../setting.py")
    #取[1:-1]是为了解决configparser出现解析配置文件，字符串带上引号的问题
    db_host = '127.0.0.1' if config.get('mysql','db_host') is '' else config.get('mysql','db_host')[1:-1]
    db_user = '' if config.get('mysql','db_user') is '' else config.get('mysql','db_user')
    db_password = '' if config.get('mysql','db_password') is '' else config.get('mysql','db_password')[1:-1]
    db_port = 3306 if config.get('mysql','db_port') is '' else config.getint('mysql','db_port')
    db_name = '' if config.get('mysql','db_name') is '' else config.get('mysql','db_name')[1:-1]
    db_charset = 'utf8' if config.get('mysql','db_charset') is '' else config.get('mysql','db_charset')[1:-1]

    def __init__(self, db_host = db_host, db_user = db_user, db_password = db_password, db_port = db_port, db_name = db_name, db_charset = db_charset):
        #将个变量赋值给对象
        self.db_host = db_host
        self.db_user = db_user
        self.db_password = db_password
        self.db_port = db_port
        self.db_name = db_name
        self.db_charset = db_charset

    #数据库连接
    def connect(self):
        #创建一个连接并返回
        db = pymysql.connect(host = self.db_host, user = self.db_user, passwd = self.db_password, db = self.db_name, port = self.db_port, charset = self.db_charset)
        return db

    #查询数据库版本
    def version(self):
        db = self.connect()
        # 使用 cursor() 方法创建一个游标对象 cursor
        cursor = db.cursor()
        # 使用 execute()  方法执行 SQL 查询
        cursor.execute("SELECT VERSION()")
        # 使用 fetchone() 方法获取单条数据.
        data = cursor.fetchone()
        print ("Database version : %s " % data)
        # 关闭数据库连接
        db.close()

    #源生sql查询，使用事务，防止数据问题
    def drop(self, table):
        db = self.connect()
        cursor = db.cursor()
        sql = "SELECT table_name FROM information_schema.TABLES WHERE table_name ='" + table + "';"
        cursor.execute(sql)
        res = cursor.fetchone()
        if res == None:
            return True
        else:
            sql = "DROP TABLE " + table;
            cursor.execute(sql)
        db.close()
        return True

    #源生sql查询，使用事务，防止数据问题
    def query(self, sql):
        flag = True
        db = self.connect()
        cursor = db.cursor(cursor = pymysql.cursors.DictCursor)#转化为字典
        try:
           cursor.execute(sql)
           db.commit()
           flag = True
        except:
           db.rollback()
           flag = False
        db.close()
        return flag

    #封装查询--查询单表数据--全部
    def fetchALL(self, table, condition = {}):
        # 拼装sql
        sql = "select * from " + table + " where 1 = 1"
        list = []
        for key, value in condition.items():
            sql = sql + " and " + key + " = %s"
            list.append(value)
        tup = tuple(list)   #将数字转化为元组，便于后续查询

        db = self.connect()
        cursor = db.cursor(cursor = pymysql.cursors.DictCursor)
        cursor.execute(sql, tup)
        data = cursor.fetchall()
        db.close()
        return data

    #封装查询--查询单表数据--单条
    def fetchOne(self, table, condition = {}):
        # 拼装sql
        sql = "select * from " + table + " where 1 = 1"
        list = []
        for key, value in condition.items():
            sql = sql + " and " + key + " = %s"
            list.append(value)
        tup = tuple(list)   #将数字转化为元组，便于后续查询

        db = self.connect()
        cursor = db.cursor(cursor = pymysql.cursors.DictCursor)
        cursor.execute(sql, tup)
        data = cursor.fetchone()
        db.close()
        return data

    #封装插入
    def insert(self, table, data):
        # 添加默认的新增和更新时间
        if 'created' not in data.keys():
            data['created'] = int(time.time())
        if 'updated' not in data.keys():
            data['updated'] = int(time.time())

        field = '('
        values = '('
        for key, value in data.items():
            field = field + "`" + key + "`" + ','
            if type(value) is int or type(value) is float:
                values = values + str(value) + ','
            else:
                values = values + "'" + str(value) + "',"
        field = field[:-1] + ')'
        values = values[:-1] + ')'
        # 拼装sql
        sql = "insert into `" + table + "`" + field + " values" + values

        db = self.connect()
        cursor = db.cursor()
        res = cursor.execute(sql)
        db.commit()
        db.close()
        return res

    #封装更新
    def update(self, table, data, condition = {}):
        # 添加默认的更新时间
        if 'updated' not in data.keys():
            data['updated'] = int(time.time())

        update_field = ''
        for key, value in data.items():
            update_field = update_field + "`" + key + "`" + '='
            if type(value) is int or type(value) is float:
                update_field = update_field + str(value) + ','
            else:
                update_field = update_field + "'" + str(value) + "',"
        update_field = update_field[:-1]

        condition_field = ''
        for key, value in condition.items():
            condition_field = condition_field + ' and '  + "`" + key + "`" + '='
            if type(value) is int or type(value) is float:
                condition_field = condition_field + str(value)
            else:
                condition_field = condition_field + "'" + str(value) + "'"
        # 拼装sql
        sql = "update `" + table + "` set " + update_field + " where 1 = 1" + condition_field

        db = self.connect()
        cursor = db.cursor()
        res = cursor.execute(sql)
        db.commit()
        db.close()
        return res

    #封装更新插入更新
    def save(self, table, data):
        if 'id' in data.keys():
            condition = {'id': data['id']}
            ret = self.fetchALL(table, condition)
            if ret:
                res = self.update(table, data, condition)
            else:
                res = self.insert(table, data)
        else:
            res = self.insert(table, data)
        return res
