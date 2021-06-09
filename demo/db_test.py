#-*- encoding: utf-8 -*-
'''
db_test.py
#Created on 2020/4/6 14:34
#@author:VincentZhao
'''
from commons.util.db_util import DBUtil
from configs.config import _HAINIU_DB
db_util = DBUtil(_HAINIU_DB)

# 设置字符集是utf8mb4
db_util.execute_no_commit("set NAMES utf8mb4;")

# 测试 execute(self,sql,params = None):
# sql = """
# insert into hainiu_queue (type,action,params) values (1, 'www.hainiubl.com', 'aa');
# """
# db_util.execute(sql)


# -------------------------------------
# 测试 execute(self,sql,params != None):
# sql = """
# insert into hainiu_queue (type,action,params) values (%s, %s, %s);
# """
# params = [1, 'www.hainiubl.com', "a'a"]
# db_util.execute(sql, params)

# -------------------------------------
# 测试 executemany(self,sql, params):
# sql = """
# insert into hainiu_queue (type,action,params) values (%s, %s, %s);
# """
# params = [(1, 'www.hainiubl.com', "bb"), (1, 'www.hainiubl.com', "cc")]
# db_util.executemany(sql, params)

# -------------------------------------
# 测试查询read_one(self,sql, params = None):
# sql = """
# select count(*) as  num from hainiu_queue where type=%s;
# """
#
# # sql = """
# # select id from hainiu_queue where type=%s;
# # """
#
# params = [1]
# rs = db_util.read_one(sql, params)
# print rs[0] if rs != None else '无记录'

# -------------------------------------
# 测试 read_dict(self, sql, params = None):
# sql = """
# select id, type, action, params from hainiu_queue where type=%s;
# """
# params = [1]
# rs = db_util.read_dict(sql, params)
# # 元组里面套字典({},{},{})
# for row in rs:
#     # print row
#     id = row["id"]
#     type = row["type"]
#     action = row["action"]
#     p = row["params"]
#     print "%s %s %s %s" % (id, type, action, p)

# -------------------------------------
# read_tuple(self, sql, params = None):
#元组里面套字典((),(),())
# sql = """
# select id, type, action, params from hainiu_queue where type=%s;
# """
# params = [1]
# rs = db_util.read_tuple(sql, params)
# # 元组里面套元组((),(),())
# for row in rs:
#     # print row
#     id = row[0]
#     type = row[1]
#     action = row[2]
#     p = row[3]
#     print "%s %s %s %s" % (id, type, action, p)

# -------------------------------------
# # 插入两次，两次在同一个事务里
import time,traceback
sql = """
insert into hainiu_queue (type,action,params) values (%s, %s, %s);
"""
try:
    params = [1, 'www.hainiubl.com', "ff"]
    db_util.execute_no_commit(sql, params)

    # time.sleep(5)
    1/0

    params = [1, 'www.hainiubl.com', "gg"]
    db_util.execute_no_commit(sql, params)

    # time.sleep(5)

    db_util.commit()
except Exception as msg:
    db_util.rollback()
    traceback.print_exc(msg)
finally:
    db_util.close()




# -------------------------------------
# 悲观锁 + 事务





