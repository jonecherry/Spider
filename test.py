#encoding=utf-8
import sys
from lxml import etree
import requests
import re
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

url = "http://place.qyer.com/los-angeles/sight/?page=1"
html = getsource(url)
poiblocks = getpoiblock(html)
for block in poiblocks:
    dangqianselector = etree.HTML(block)
    # 中文、英文、本地名称
    name0 = dangqianselector.xpath('//h3[@class="title fontYaHei"]/a/text()')[0].strip()
    name1 = dangqianselector.xpath('//h3[@class="title fontYaHei"]/a/span/text()')
    if len(name1) == 0:
        name1 = ''
    else:
        name1 = name1[0].strip()
    print name0, name1
    shouzimu = name0[0].encode('utf-8')
    print type(shouzimu)
    print shouzimu.isalpha()







