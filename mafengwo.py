#encoding=utf-8
from lxml import etree
import requests
import os
import sys
import MySQLdb
reload(sys)
sys.setdefaultencoding("utf-8")

#getsource用来获取网页源代码
def getsource(url):
    html = requests.get(url)
    html.encoding = 'utf-8'
    return html.text

if __name__ == '__main__':

    db = 'southamerica'
    tb = '巴西'

    if not os.path.exists('zhuaqu'):
        os.mkdir('zhuaqu')
    if not os.path.exists(os.path.join('zhuaqu',tb)):
        os.mkdir(os.path.join('zhuaqu',tb))
    jilu = open(os.path.join('zhuaqu',tb,'jilu.txt'),'a')
    # POI = open('baliPOI.txt','a')
    # 连接数据库
    try:
        conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='123456', port=3306, charset='utf8')
        cur = conn.cursor()
        cur.execute('set interactive_timeout=96*3600')
        conn.select_db(db)
    except MySQLdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])



    for i in range(1,20):
        url = 'http://www.mafengwo.cn/group/s.php?q=巴黎&p='+str(i)+'&t=poi'
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
            leixin = leixin.replace('\n','')

            print leixin
            temp = elements[1].split()
            shouzimu = str(temp[0])
            if len(temp)==1:
                zhongwen=temp[0]
                yingwen=temp[0]
            elif shouzimu.isalpha():
                print shouzimu.isalpha()
                yingwen = ''
                for i in range(0,len(temp)):
                    yingwen = yingwen +' '+ temp[i]
                zhongwen = yingwen
            else:
                zhongwen = temp[0]
                yingwen = ''
                for i in range(1, len(temp)):
                    yingwen = yingwen +' '+ temp[i]

            print '中文:'
            print zhongwen
            print '英文:'
            print yingwen

            line = tb+','+leixin+','+zhongwen+','+yingwen+'\n'
            print '收录poi:'
            print line
            sqli = "INSERT INTO " + db + "." + tb + "(chinesename,englishname)" + " VALUES(%s,%s)"
            print sqli
            cur.execute(sqli,(zhongwen,yingwen))
            # cur.execute("INSERT INTO " + db + "." + tb + "(chinesename,englishname)" + " VALUES( " + zhongwen + ','+yingwen + " )")

            # POI.write(line)
            print '--------------------'

    cur.close()
    conn.commit()
    conn.close()
    jilu.close()
    # POI.close()
    print 'finished'