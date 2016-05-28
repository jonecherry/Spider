#encoding=utf-8
from lxml import etree
import requests
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

#getsource用来获取网页源代码
def getsource(url):
    html = requests.get(url)
    html.encoding = 'utf-8'
    return html.text

if __name__ == '__main__':

    if not os.path.exists('zhuaqu'):
        os.mkdir('zhuaqu')
    if not os.path.exists(os.path.join('zhuaqu','伦敦')):
        os.mkdir(os.path.join('zhuaqu','伦敦'))
    jilu = open(os.path.join('zhuaqu','伦敦','lundun.txt'),'a')

    for i in range(2,3):
        url = 'http://www.mafengwo.cn/group/s.php?q=伦敦&p='+str(i)+'&t=poi'
        html = getsource(url)

        # html = unicode(html, "utf-8")

        selector = etree.HTML(html)
        # print html
        print 'html类型'
        print type(html)

        jilu.write(html)
        jilu.close()
        poilist = selector.xpath('//div[@class="ct-text "]/h3/a/text()')
        for poi in poilist:
            print '类型-中文名称 英文名称'
            print poi
            print
            elements = poi.split('-')
            leixin = elements[0]
            print '类型:'
            print leixin
            temp = elements[1].split()
            zhongwen = temp[0]
            print '中文:'
            print zhongwen
            yingwen = ''
            for i in range(1,len(temp)):
                yingwen = yingwen +' '+ temp[i]
            print '英文:'
            print yingwen
            mingcheng = elements[1]
            print 'poi:'
            print mingcheng
            print '--------------------'
            break
            # poi = unicode(poi,"utf-8")
            # print poi.encode('gbk')
            # print poi
            # print poi.decode('

    print 'finished'