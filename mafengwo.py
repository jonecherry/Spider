#encoding=utf-8
from lxml import etree
import requests

#getsource用来获取网页源代码
def getsource(url):
    html = requests.get(url)
    return html.text

if __name__ == '__main__':
    for i in range(2,3):
        url = 'http://www.mafengwo.cn/group/s.php?q=伦敦&p='+str(i)+'&t=poi'
        html = getsource(url)
        # html = unicode(html, "utf-8")
        selector = etree.HTML(html)
        # print html
        poilist = selector.xpath('//div[@class="ct-text "]/h3/a/text()')
        for poi in poilist:
            # print type(poi)
            elements = poi.split('-')
            type = elements[0]
            print type
            # temp = elements[1].split()
            # zhongwen = temp[0]
            # print zhongwen
            # yingwen = ''
            # for i in range(1,len(temp)):
            #     yingwen = yingwen +' '+ temp[i]
            # print yingwen
            mingcheng = elements[1]
            print mingcheng
            # poi = unicode(poi,"utf-8")
            # print poi.encode('gbk')
            # print poi
            # print poi.decode('
