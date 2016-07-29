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

url = "http://www.mafengwo.cn/poi/6673956.html"
html = getsource(url)







