#-*- encoding: gb2312 -*-
'''
encode_demo.py
#Created on 2020/4/6 14:34
#@author:VincentZhao
'''
from importlib import reload

s1 = '中文'
print (type(s1))
print (s1)

s2 = u'中文'
print (s2)

#print s1.encode('utf-8')

# 需要先decode 再 encode
s3 = s1.decode('gb2312').encode('utf-8')
print (s3)
# 字符串类型
print (type(s3))


import sys
reload(sys)   #Python2.5 初始化后删除了 sys.setdefaultencoding 方法，我们需要重新载入
sys.setdefaultencoding('gb2312')

# 省去decode的流程
print (s1.encode('utf-8'))