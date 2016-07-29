#coding=utf-8
import requests
import os
import MySQLdb
from lxml import etree
import re
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

#getsource用来获取网页源代码
def getsource(url):
    html = requests.get(url)
    html.encoding = 'utf-8'
    return html.text
#获取信息块
def getblock(source):
    blocks = re.findall('(<h3 class="title fontYaHei".*?</h3>)',source,re.S)
    return blocks

if __name__ == '__main__':
    starturl = 'http://place.qyer.com/usa/citylist-0-0-1/'
    country_id = 1
    parent_region_id = 1
    region_type = 2

    db = 'map'
    # 数据表
    tb = 'map_region'
    # area = 'miami'

    # if not os.path.exists('zhuaqu'):
    #     os.mkdir('zhuaqu')
    # if not os.path.exists(os.path.join('zhuaqu',tb)):
    #     os.mkdir(os.path.join('zhuaqu',tb))
    # chengshijilu = open('chengshijilu.txt','a')

    # 连接数据库
    try:
        conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='123456', port=3306, charset='utf8')
        cur = conn.cursor()
        cur.execute('set interactive_timeout=96*3600')
        conn.select_db(db)
    except MySQLdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    temphtml = getsource(starturl)
    selector = etree.HTML(temphtml)
    pagenums = selector.xpath('//div[@class="ui_page"]/a/@data-page')
    # 需爬取得页数
    pagenum = pagenums[len(pagenums)-2]

    for i in range(9, int(pagenum) + 1):
        url = 'http://place.qyer.com/usa/citylist-0-0-%d'%(i)
        print url
        html = getsource(url)
        selector2 = etree.HTML(html)
        blocks = getblock(html)
        for j,block in enumerate(blocks):
            print j
            selector1 = etree.HTML(block)
            city = selector1.xpath('//a/text()')[0].strip()
            cityenglishname = selector1.xpath('//span/text()')[0].strip()
            sub_url = selector1.xpath('//a/@href')[0]

            sub_html = getsource(sub_url)
            sub_selector = etree.HTML(sub_html)
            pa_num = sub_selector.xpath('//div[@class="plcTopBarStat fontYaHei"]/em/text()')
            if not pa_num:
                pa_num = 0
            else:
                pa_num = pa_num[0]
            # print pa_num


            sqli = "INSERT INTO " + db + "." + tb + "(region_ch_name,region_en_name,region_loc_name,parent_region_id,country_id,region_type,visited_count)" + " VALUES(%s,%s,%s,%s,%s,%s,%s)"

            # 判断数据库是否已经存在城市数据，决定是插入数据还是更新数据。
            sqli1 = "select * from "+db+"."+tb+" where region_ch_name = "+"'%s'"%(city)

            num_result = cur.execute(sqli1)
            if num_result:
                pass
            if not num_result:
                cur.execute(sqli,(city, cityenglishname, cityenglishname, parent_region_id, country_id, region_type, pa_num))
                conn.commit()
            print '------------------------------------------------'
    cur.close()
    conn.close()
    print '------------finished--------------'
