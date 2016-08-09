#encoding=utf-8
from lxml import etree
import requests
import os
import sys
import MySQLdb
import re
reload(sys)
sys.setdefaultencoding("utf-8")

#用来获取网页源代码
def getsource(url):
    html = requests.get(url)
    html.encoding = 'utf-8'
    return html.text
#获取信息块
def getcountryblock(source):
    blocks = re.findall('(<h3 class="title fontYaHei".*?</h3>)',source,re.S)
    return blocks

def getpoiblock(source):
    blocks = re.findall('(<li class="clearfix".*?</li>)',source,re.S)
    return blocks
# 对匹配为空进行处理
def pankong(poi_xx):
    if len(poi_xx)==0:
        poi_xx = ''
    else:
        poi_xx = poi_xx[0]
    return poi_xx

if __name__ == '__main__':
    country = 'singapore'
    city = '新加坡'
    starturl = 'http://place.qyer.com/singapore/'

    db = 'map'
    # 数据表
    tb = 'map_poi'
    # 希望跳过抓取的城市
    hulvcities = range(1,826)

    # 连接数据库
    try:
        # conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='123456', port=3306, charset='utf8')
        conn = MySQLdb.connect(host='172.22.185.78', user='root', passwd='123456', port=3306, charset='utf8')
        cur = conn.cursor()
        cur.execute('set interactive_timeout=96*3600')
        conn.select_db(db)
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])


    # 对应的城市id
    sqli1 = "select region_id from " + db + ".map_region" + " where region_ch_name = " + "'%s'" % (city)
    num_result = cur.execute(sqli1)
    if not num_result:
        region_id = ''
    else:
        region_id = cur.fetchmany(1)
        region_id = region_id[0][0]

    # 过滤已经抓取完成的城市
    if region_id in hulvcities:
        print city, '已经完成抓取，跳过'
        pass
    else:
        # 城市主页
        sighturl = starturl+'sight/'
        foodurl = starturl+'food/'
        shoppingurl = starturl+'shopping/'
        city_urls = [sighturl,foodurl,shoppingurl]
        for ci,cityurl in enumerate(city_urls):
            print cityurl
            sub_html = getsource(cityurl)
            sub_selector = etree.HTML(sub_html)
            # 爬取的页数
            poiyeshu = sub_selector.xpath('//div[@class="ui_page"]/a/@data-page')
            try:
                poiyeshu = poiyeshu[-2]
            except:
                pass
            else:
                for ye in range(1,int(poiyeshu)+1):
                    dangqianurl = cityurl+"?page=%s"%(ye)
                    print '列表页url',dangqianurl
                    dangqianhtml = getsource(dangqianurl)
                    poiblocks = getpoiblock(dangqianhtml)
                    print '当前页的poi数',len(poiblocks)
                    for poiblock in poiblocks:
                        dangqianselector = etree.HTML(poiblock)

                        # 中文、英文、本地名称
                        name0 = dangqianselector.xpath('//h3[@class="title fontYaHei"]/a/text()')[0].strip()
                        name1 = dangqianselector.xpath('//h3[@class="title fontYaHei"]/a/span/text()')
                        if len(name1)==0:
                            name1 = ''
                        else:
                            name1 = name1[0].strip()

                        shouzimu = name0[0].encode('utf-8')
                        if shouzimu.isalpha():
                            poi_en_name = name0
                            poi_ch_name = ''
                        else:
                            poi_en_name = name1
                            poi_ch_name = name0
                        poi_loc_name = poi_en_name

                        # 类别id
                        if ci == 0:
                            tag_id = 3
                        elif ci == 1:
                            tag_id =1
                        elif ci == 2:
                            tag_id = 4
                        # 评分
                        poi_score = dangqianselector.xpath('//span[@class="grade"]/text()')
                        if len(poi_score)==0:
                            poi_score=''
                        else:
                            poi_score = poi_score[0]

                        # 排名
                        poi_rank = dangqianselector.xpath('//em[@class="rank orange"]/text()')
                        poi_rank = pankong(poi_rank)
                        newstr = ''
                        for sr in poi_rank:
                            if sr.isdigit():
                                newstr = newstr + sr
                        poi_rank = newstr

                        # 详情页url
                        xiangqingurl = dangqianselector.xpath('//h3[@class="title fontYaHei"]/a/@href')[0]
                        print '详情页',xiangqingurl
                        try:
                            xiangqinghtml = getsource(xiangqingurl)
                        except:
                            pass
                        else:
                            xiangqingselector = etree.HTML(xiangqinghtml)
                            poi_tips_biaoti = xiangqingselector.xpath('//div[@class="poiDet-main"]/ul[@class="poiDet-tips"]/li/span/text()')
                            biaotilist = []
                            for tipi,biaoti in enumerate(poi_tips_biaoti):
                                biaoti = biaoti.strip()
                                biaotilist.append(biaoti)

                            for ti,biaoti in enumerate(biaotilist):
                                if biaoti =='':
                                    biaotilist.pop(ti)
                            for bi,biaoti in enumerate(biaotilist):
                                if biaoti == '地址：':
                                    addi = bi + 1
                                if biaoti == '电话：':
                                    telei = bi + 1
                            if '地址：'in biaotilist:
                                # 地址
                                xpath_str_add = "//ul[@class='poiDet-tips']/li["+str(addi)+"]/div/p/text()"
                                poi_address = xiangqingselector.xpath(xpath_str_add)
                                poi_address = pankong(poi_address)
                            else:
                                poi_address = ''

                            if '电话：'in biaotilist:
                                # 电话
                                xpath_str_tele = "//ul[@class='poiDet-tips']/li[" + str(telei) + "]/div/p/text()"
                                poi_telephone = xiangqingselector.xpath(xpath_str_tele)
                                poi_telephone = pankong(poi_telephone)
                                if not poi_telephone:
                                    poi_telephone = ''
                            else:
                                poi_telephone = ''
                            # 评论数
                            pinglunshu = dangqianselector.xpath('//div[@class="info"]/span[@class="dping"]/a/text()')
                            if len(pinglunshu)==0:
                                pinglunshu =''
                            else:
                                pinglunshu = pinglunshu[0]

                            comments_count = pinglunshu.strip()
                            newstr1 = ''
                            for sr1 in comments_count:
                                if sr1.isdigit():
                                    newstr1 = newstr1 + sr1
                            comments_count = newstr1
                            # 来源
                            source = 'qyer'
                            sqli = "INSERT INTO " + db + "." + tb + "(poi_ch_name,poi_en_name,poi_loc_name,poi_region_id,poi_tag_id,poi_score,poi_rank,poi_address,poi_telephone,comments_count,source_website)" + " VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

                            # 判断数据库是否已经存在城市数据，决定是插入数据还是更新数据。
                            sqli1 = "select * from " + db + "." + tb + " where poi_ch_name = " + "'%s'" % (poi_ch_name)
                            sqli2 = "select * from " + db + "." + tb + " where poi_en_name = " + "'%s'" % (poi_en_name)
                            # print '中文查询',sqli1
                            # print '英文查询',sqli2
                            try:
                                r1 = cur.execute(sqli1)
                                r2 = cur.execute(sqli2)
                            except:
                                pass
                            if poi_ch_name =='':
                                r1 = 0
                            if poi_en_name == '':
                                r2 = 0
                            print '查询结果：','中文',r1,'英文',r2
                            if r1 or r2:
                                print '已经存在记录，迭代数据 ... ...'
                                pass
                            else:
                                print '插入新POI... ...'
                                cur.execute(sqli,(poi_ch_name, poi_en_name, poi_loc_name, region_id, tag_id,poi_score,poi_rank,poi_address,poi_telephone,comments_count,source))
                                conn.commit()
                            print '------------------------------------------------'
    cur.close()
    conn.close()
    print '------------finished--------------'
