#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
a = "口味：345.34534"
for i,chr in enumerate(a):
    if chr.isdigit():
        ci = i
        break
num = a[ci:]
print num



