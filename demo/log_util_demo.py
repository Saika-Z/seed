#-*- encoding: utf-8 -*-
'''
log_util_demo.py
#Created on 2020/4/6 14:34
#@author:VincentZhao
'''
# 引入log_util 模块的 LogUtil类
from commons.util.log_util import LogUtil

# 获取logger对象
logger = LogUtil().get_logger("log_name", "log_file")
logger.info("这是测试log_util的使用")
logger.error("这是测试log_util的使用")
try:
    num = 0
    1/num
except Exception as msg:
    logger.exception(msg)

