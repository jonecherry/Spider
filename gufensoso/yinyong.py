#encoding=utf-8
import sys
from lxml import etree
import requests

#getsource用来获取网页源代码
def getsource(url):
    html = requests.get(url)
    return html.text

if __name__ == '__main__':
    url = 'http://gg3.cytbj.com/scholar?q=社会网络'
    html = getsource(url)
    selector = etree.HTML(html)
    referenceNum = selector.xpath('//div[@class="gs_fl"]/a/text()')[0]
    print referenceNum[0:6]
    print referenceNum[6:]




