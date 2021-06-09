#-*- encoding: utf-8 -*-
'''
demo.py
#Created on 2020/4/6 14:34
#@author:VincentZhao
'''


day = '20190620'
hour = '12'
minute = 10

for i in range(60,-5,-5):
    if minute < i:
        continue
    minute = i
    break

minute = '0%s' % minute if minute < 10 else minute
print ('%s%s%s' % (day,hour,minute))