#-*- encoding: utf-8 -*-
'''
config.py
#Created on 2020/4/6 14:34
#@author:VincentZhao
'''

#日志地址
_LOG_DIR = '/tmp/python/hainiu_crawler/log/%s'

#数据地址
_LOCAL_DATA_DIR = '/tmp/python/hainiu_crawler/data/%s'

#数据库配置_测试
_HAINIU_DB = {'HOST':'localhost', 'USER':'root', 'PASSWD':'root', 'DB':'hainiu_test', 'CHARSET':'utf8', 'PORT':3306}

# NAME, P_SLEEP_TIME, C_MAX_NUM, C_MAX_SLEEP_TIME, C_RETRY_TIMES
_QUEUE_DEMO = {'NAME':'demo', 'P_SLEEP_TIME': 5, 'C_MAX_NUM': 1, 'C_MAX_SLEEP_TIME': 3, 'C_RETRY_TIMES':3}

# 海牛队列
_QUEUE_HAINIU = {'NAME':'hainiu', 'P_SLEEP_TIME': 3, 'C_MAX_NUM': 1,
                 'C_MAX_SLEEP_TIME': 1, 'C_RETRY_TIMES':3, 'MAX_FAIL_TIMES':6,
                 'LIMIT_NUM': 2}
# 苹果队列配置
_QUEUE_APPLE = {'NAME':'apple', 'P_SLEEP_TIME': 5, 'C_MAX_NUM': 1, 'C_MAX_SLEEP_TIME': 3, 'C_RETRY_TIMES':3}
# 发现新闻队列配置
_QUEUE_NEWS_FIND= {'NAME':'news_find', 'P_SLEEP_TIME': 3, 'C_MAX_NUM': 1, 'C_MAX_SLEEP_TIME': 1, 'C_RETRY_TIMES':3,
                   'MAX_FAIL_TIMES':6,'LIMIT_NUM': 10}


#报警电话
_ALERT_PHONE = '110'

