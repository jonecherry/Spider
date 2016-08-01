#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

a =[ 1,2,3,5]
for i,b in enumerate(a):
    if i <2:
        pass
    else:
        print b
