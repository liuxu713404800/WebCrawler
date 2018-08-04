import sys
sys.path.append("..")
from DB import mysql

mysqldb = mysql.MysqlDB()

#创建代理池
res = mysqldb.drop('proxy_pool')
#print(res)
sql = """
    CREATE TABLE `proxy_pool` (
      `id` bigint(20) NOT NULL AUTO_INCREMENT,
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
      `id` tinyint(4) NOT NULL AUTO_INCREMENT,
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
      `id` int(11) NOT NULL AUTO_INCREMENT,
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
      `id` int(11) NOT NULL AUTO_INCREMENT,
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

#创建地铁线路，地铁站成功
res = mysqldb.drop('subway_station')
sql = """
    CREATE TABLE `room` (
        `id`  int(11) NOT NULL AUTO_INCREMENT ,
        `source`  tinyint NOT NULL COMMENT '信息来源：1,链家；2,贝壳；3,蘑菇；4,自如；5,蛋壳' ,
        `room_id`  int(11) NOT NULL COMMENT '平台房间id' ,
        `name`  varchar(255) NULL COMMENT '房间名称' ,
        `room_type`  tinyint NULL DEFAULT 1 COMMENT '卧室类型：0,整租;1,主卧;2,次卧' ,
        `rent_type`  tinyint NULL DEFAULT 1 COMMENT '出租方式：0,整租;1合租' ,
        `compound_name`  varchar(255) NULL COMMENT '小区名称' ,
        `compound_type`  tinyint NULL DEFAULT 2 COMMENT '小区类型：1,民宅;2,酒店式公寓' ,
        `district`  varchar(50) NULL COMMENT '所属区域' ,
        `room_area`  decimal NULL COMMENT '房屋面积' ,
        `build_area`  decimal NULL COMMENT '建筑面积' ,
        `house_type`  varchar(30) NULL COMMENT '户型' ,
        `floor_number`  varchar(50) NULL COMMENT '当前层数' ,
        `price`  decimal(10,2) NULL COMMENT '价格' ,
        `brief_info`  varchar(500) NULL COMMENT '简单介绍' ,
        `detail_info`  text NULL COMMENT '详细介绍' ,
        `commute_info`  varchar(255) NULL COMMENT '通勤介绍' ,
        `pay_method`  varchar(100) NULL COMMENT '支付方式' ,
        `decoration`  varchar(255) NULL COMMENT '装修' ,
        `publish_info`  varchar(100) NULL COMMENT '发布信息',
        `image_info` text COMMENT '房屋图片信息',
        `station_ref` int(5) DEFAULT NULL COMMENT '所属地铁',
        PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
res = mysqldb.query(sql)
# print(res)
print("创建房间表成功！")
