import sys
sys.path.append("..")
from DB import mysql

mysqldb = mysql.MysqlDB()

#创建代理池
res = mysqldb.drop('proxy_pool')
#print(res)
sql = """
    CREATE TABLE `proxy_pool` (
      `id` bigint(20) NOT NULL COMMENT 'id',
      `created` int(10) DEFAULT NULL,
      `updated` int(10) DEFAULT NULL,
      `ip` char(20) CHARACTER SET latin1 NOT NULL DEFAULT '' COMMENT '代理ip',
      `port` int(11) DEFAULT '80' COMMENT '端口号',
      `type` varchar(50) CHARACTER SET latin1 DEFAULT 'HTTP' COMMENT '类型',
      `success` int(11) DEFAULT '0' COMMENT '成功次数',
      `failed` int(11) DEFAULT '0' COMMENT '失败次数',
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """
res = mysqldb.query(sql)
# print(res)
print("创建代理池成功！")

#创建地铁表
res = mysqldb.drop('subway')
sql = """
    CREATE TABLE `subway` (
      `id` tinyint(4) NOT NULL,
      `created` int(11) DEFAULT NULL,
      `updated` int(11) DEFAULT NULL,
      `name` char(50) CHARACTER SET utf8mb4 DEFAULT NULL,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """
res = mysqldb.query(sql)
# print(res)
print("创建地铁线路成功！")

#创建地铁站表
res = mysqldb.drop('station')
sql = """
    CREATE TABLE `station` (
      `id` int(11) NOT NULL,
      `created` int(11) DEFAULT NULL,
      `updated` int(11) DEFAULT NULL,
      `name` char(50) CHARACTER SET utf8mb4 DEFAULT NULL,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """
res = mysqldb.query(sql)
# print(res)
print("创建地铁站成功！")

#创建地铁线路，地铁站成功
res = mysqldb.drop('subway_station')
sql = """
    CREATE TABLE `subway_station` (
      `id` int(11) NOT NULL,
      `created` int(10) DEFAULT NULL,
      `updated` int(10) DEFAULT NULL,
      `station_id` int(11) DEFAULT NULL,
      `subway_id` int(11) DEFAULT NULL,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """
res = mysqldb.query(sql)
# print(res)
print("创建地铁线路，地铁站关系表成功！")
