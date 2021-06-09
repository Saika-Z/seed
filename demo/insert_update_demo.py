#-*- encoding: utf-8 -*-
'''
insert_update_demo.py
#Created on 2020/4/6 14:34
#@author:VincentZhao
'''
from configs.config import _HAINIU_DB
from commons.util.db_util import DBUtil

db_util =  DBUtil(_HAINIU_DB)
import datetime,traceback
try:
    #-----------插入-------------------------
    # sql = """
    # insert into hainiu_web_seed (url, md5,domain, host,category,last_crawl_time)values(%s,%s,%s,%s,%s,%s);
    # """
    # print sql
    # dt=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # print dt
    # md5 = 'a1'
    # params = ['www.baidu.com', md5, "com",'baidu.com', '搜索', dt]
    # db_util.execute(sql, params)

    #-----------更新-------------------------
    # sql = """
    # update hainiu_web_seed set last_crawl_time=%s where md5=%s;
    # """
    # print sql
    # dt=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # md5 = 'a1'
    # params = [dt, md5]
    # db_util.execute_no_commit(sql, params)
    # db_util.commit()


    #---on DUPLICATE KEY 的SQL例子---------------
    # 如果主键存在就更新，不存在就插入
    insert_web_seed_sql = """
    insert into hainiu_web_seed (url, md5,domain, host,category,last_crawl_time,fail_ip) values (%s,%s,%s,%s,%s,%s,%s)
    on DUPLICATE KEY UPDATE fail_times=fail_times+1,fail_ip=values(fail_ip), last_crawl_time=values(last_crawl_time);
"""
    dt=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md5 = 'a1'
    ip = "160"
    params = ['www.baidu.com', md5, "com",'baidu.com', '搜索', dt,ip]
    db_util.execute(insert_web_seed_sql, params)

except Exception as message:
    db_util.rollback_close()
    traceback.print_exc()
    # logger.exception(message)