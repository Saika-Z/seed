#-*- encoding: gb2312 -*-
'''
encode_demo.py
#Created on 2020/4/6 14:34
#@author:VincentZhao
'''
from importlib import reload

s1 = '����'
print (type(s1))
print (s1)

s2 = u'����'
print (s2)

#print s1.encode('utf-8')

# ��Ҫ��decode �� encode
s3 = s1.decode('gb2312').encode('utf-8')
print (s3)
# �ַ�������
print (type(s3))


import sys
reload(sys)   #Python2.5 ��ʼ����ɾ���� sys.setdefaultencoding ������������Ҫ��������
sys.setdefaultencoding('gb2312')

# ʡȥdecode������
print (s1.encode('utf-8'))