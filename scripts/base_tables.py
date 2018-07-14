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

#创建房价记录表
