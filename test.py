#encoding=utf-8
import sys
from lxml import etree
import requests
import re


str = '点评(10)'
print len(str)
i = 0
for cha in str:
    if cha == '(':
        print str[i]
    i = i + 1