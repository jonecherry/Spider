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
    if not os.path.exists(os.path.join('zhuaqu','巴黎')):
        os.mkdir(os.path.join('zhuaqu','巴黎'))
    jilu = open(os.path.join('zhuaqu','巴黎','bali.txt'),'a')
    POI = open('lundunPOI.txt','a')

    for i in range(8,9):
        url = 'http://www.mafengwo.cn/group/s.php?q=伦敦&p='+str(i)+'&t=poi'
        html = getsource(url)
        selector = etree.HTML(html)
        # print 'html类型'
        # print type(html)

        jilu.write(html)

        # poilist = selector.xpath('//div[@class="ct-text "]/h3/a/text()')
        poilist = selector.xpath('//div[@class="ct-text "]/h3')
        for poi in poilist:
            poi = poi.xpath('string(.)')
            # poi = poi.replace('\n','')

            print '类型 - 中文名称 英文名称'
            # print poi.replace(' ','')
            print poi
            elements = poi.split('-')
            leixin = elements[0]
            print '类型:'
            leixin = leixin.replace(' ','')
            print leixin
            temp = elements[1].split()
            if len(temp)==1:
                zhongwen=temp[0]
                yingwen=temp[0]
            else:
                zhongwen = temp[0]
                yingwen = ''
                for i in range(1,len(temp)):
                    yingwen = yingwen +' '+ temp[i]

            print '中文:'
            print zhongwen
            print '英文:'
            print yingwen

            line = '伦敦'+','+leixin+','+zhongwen+','+yingwen+'\n'
            print '收录poi:'
            print line
            POI.write(line)
            print '--------------------'
    jilu.close()
    POI.close()
    print 'finished'