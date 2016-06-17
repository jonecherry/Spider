#encoding=utf-8
from lxml import etree
import requests
import os
import sys
import MySQLdb
import re
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

def getnum(commentsnum):
    i = 0
    j = 0
    for char in commentsnum:
        if char == '(':
            break
        i = i + 1

    for char in commentsnum:
        if char == ')':
            break
        j = j + 1
    si = int(i) + 1
    ei = int(j)
    return commentsnum[si:ei]

if __name__ == '__main__':

    db = 'southamerica'
    tb = 'baxi'

    if not os.path.exists('zhuaqu'):
        os.mkdir('zhuaqu')
    if not os.path.exists(os.path.join('zhuaqu',tb)):
        os.mkdir(os.path.join('zhuaqu',tb))
    jilu = open(os.path.join('zhuaqu',tb,'jilu.txt'),'a')
    # 连接数据库
    try:
        conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='123456', port=3306, charset='utf8')
        cur = conn.cursor()
        cur.execute('set interactive_timeout=96*3600')
        conn.select_db(db)
    except MySQLdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])



    for i in range(1,46):
        url = 'http://www.mafengwo.cn/group/s.php?q=巴西&p='+str(i)+'&t=poi'
        html = getsource(url)
        jilu.write(html)
        blocks = getblock(html)
        for block in blocks:
            selector = etree.HTML(block)
            poi = selector.xpath('//h3')[0]
            poi = poi.xpath('string(.)')
            # poi = poi.replace('\n','')
            print poi
            elements = poi.split('-')
            leixin = elements[0]
            leixin = leixin.replace(' ', '')
            leixin = leixin.replace('\n', '')

            temp = elements[1].split()

            if len(temp)==0:
                continue
            shouzimu = str(temp[0])
            if len(temp) == 1:
                zhongwen = temp[0]
                yingwen = temp[0]
            elif shouzimu.isalpha():
                yingwen = ''
                for i in range(0, len(temp)):
                    yingwen = yingwen + ' ' + temp[i]
                zhongwen = yingwen
            else:
                zhongwen = temp[0]
                yingwen = ''
                for i in range(1, len(temp)):
                    yingwen = yingwen + ' ' + temp[i]

            # print '中文:',zhongwen
            print '英文:',yingwen

            # 国家、城市
            poiinfos = selector.xpath('//li/a/text()')
            country_city = poiinfos[0]
            country_city = country_city.split('-')
            country = country_city[0]
            city = country_city[1]
            # 评论数
            pinglunshu = getnum(poiinfos[1])
            # 相关游记数
            relatedyoujishu = getnum(poiinfos[2])



            if leixin =='景点':
                # 详情链接
                link = selector.xpath('//h3/a/@href')[0]
                subhtml = getsource(link)
                subselector = etree.HTML(subhtml)
                quguoshoucang = subselector.xpath('//span[@class="pa-num"]/text()')
                # 去过数
                quguonum = quguoshoucang[1]
                # 收藏数
                shoucangshu = quguoshoucang[0]
            else:
                quguonum = 0
                shoucangshu = 0

            sqli = "INSERT INTO " + db + "." + tb + "(country,city,chinesename,englishname,type,commentsnum,youjinum,pa_num,shoucangnum)" + " VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(sqli,(country,city,zhongwen,yingwen,leixin,pinglunshu,relatedyoujishu,quguonum,shoucangshu))
            print '------------------------------------------------'

    cur.close()
    conn.commit()
    conn.close()
    jilu.close()
    print 'finished'