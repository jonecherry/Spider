#encoding=utf-8
import sys
from lxml import etree
import requests
import re
import os
import MySQLdb
import thread
import time# 为线程定义一个函数
reload(sys)
a = []
a.append(0)
a.append(3)
print a