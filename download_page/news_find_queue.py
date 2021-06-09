#-*- encoding: utf-8 -*-
'''
news_find_queue.py
#Created on 2020/4/6 14:34
#@author:VincentZhao
'''

import json,time
from imp import reload

from commons.util.db_util import DBUtil
from commons.util.log_util import LogUtil
from configs.config import _HAINIU_DB, _QUEUE_NEWS_FIND

# 每页查询多少
PAGE_SHOW_NUM = 5

def put_queue():


    logger = LogUtil().get_logger('put_news_find_queue', 'put_news_find_queue')

    # 查询hainiu_queue表是否后符合条件的数据
    select_queue_count_sql = """
    select count(*) from hainiu_queue where is_work=0 and fail_times < %s;
    """

    # 计算种子表符合条件的总记录数
    select_seed_count_sql = """
    select count(*) from hainiu_web_seed where status=0;
    """


    # 分页查询SQL
    select_seed_page_sql = """
    select url,md5,domain,host from hainiu_web_seed where status=0 limit %s,%s;
    """

    # 插入hainiu_queue
    insert_queue_sql = """
    insert into hainiu_queue (type,action,params) values (%s, %s, %s);
    """

    db_util = DBUtil(_HAINIU_DB)
    try:
        sql_param = [_QUEUE_NEWS_FIND['MAX_FAIL_TIMES']]
        res1 = db_util.read_one(select_queue_count_sql, sql_param)
        count_num = res1[0]


        if count_num != 0:
            logger.info('hainiu_queue 有记录，不需要导入')
            return None


        # 如果没有数据就可以导入
        start_time = time.time()

        res2 = db_util.read_one(select_seed_count_sql)
        total_num = res2[0]

        # 计算分页数
        page_num = total_num/PAGE_SHOW_NUM if total_num/PAGE_SHOW_NUM == 0 else total_num/PAGE_SHOW_NUM + 1

        # 分页查询，批量导入
        for i in range(0, page_num):
            logger.info('%d,%d' % (i * PAGE_SHOW_NUM, PAGE_SHOW_NUM))
            sql_param = [i * PAGE_SHOW_NUM, PAGE_SHOW_NUM]
            # ({},{})
            res3 = db_util.read_dict(select_seed_page_sql, sql_param)
            sql_params = []
            for row in res3:
                url = row['url']
                url_md5 = row['md5']
                domain = row['domain']
                host = row['host']

                dict_param = {'md5':url_md5, 'domain':domain, 'host':host}
                json_str = json.dumps(dict_param)
                typestr = 1
                sql_param = [typestr, url, json_str]
                sql_params.append(sql_param)

            # 批量插入
            db_util.executemany(insert_queue_sql, sql_params)

        end_time = time.time()
        run_time = end_time - start_time
        logger.info("本次导入数据数量：%d, 运行时长：%.2f s" % (total_num, run_time))
    except Exception as msg:
        logger.exception(msg)


    finally:
        db_util.close()


if __name__ == '__main__':
    # 防止中文乱码
    import sys
    reload(sys)   #Python2.5 初始化后删除了 sys.setdefaultencoding 方法，我们需要重新载入
    sys.setdefaultencoding('utf-8')

    put_queue()