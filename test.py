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
sys.setdefaultencoding("utf-8")

#getsource用来获取网页源代码
def getsource(url):
    html = requests.get(url)
    html.encoding = 'utf-8'
    return html.text

#获取信息块
def getblock(source):
    blocks = re.findall('(<div class="ct-text ".*?</div>)',source,re.S)
    return blocks
#获取信息块
def getpoiblock(source):
    blocks = re.findall('(<li class="clearfix".*?</li>)',source,re.S)
    return blocks


db = 'map'
# 数据表
tb = 'temp'
area = 'usa'


# 连接数据库
try:
    conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='123456', port=3306, charset='utf8')
    cur = conn.cursor()
    cur.execute('set interactive_timeout=96*3600')
    conn.select_db(db)
except MySQLdb.Error, e:
    print "Mysql Error %d: %s" % (e.args[0], e.args[1])
# 抽取待抓取的城市列表
sqli0 = "select region_ch_name,region_id from map.map_region"
num_city = cur.execute(sqli0)
cities = cur.fetchmany(num_city)

for city in cities:
    print city[0],city[1]






