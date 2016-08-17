#encoding=utf-8
from lxml import etree
import requests
import os
import sys
import MySQLdb
import re
import random
import time
reload(sys)
sys.setdefaultencoding("utf-8")

def qushuzi(str):
    num = ''
    if not str:
        return num
    else:
        for sr in str:
            if sr.isdigit():
                num = num+sr
        return num
#用来获取网页源代码
def getsource(url):
    headlist = [{'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.'},
                {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},
                {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;'},
                {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'},
                {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)'},
                {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)'},
                {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},
                {'User-Agent': 'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11'},
                {'User-Agent': 'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'},
                {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'},
                {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)'},
                {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}]
    num = len(headlist)-1
    html = requests.get(url, headers=headlist[random.randint(0, num)])
    html.encoding = 'utf-8'
    return html.text
#获取信息块
def getcityblock(source):
    blocks = re.findall('(<a href=".*?</a>)',source,re.S)
    return blocks

def getpoiblock(source,ci):
    if ci == 0:
        blocks = re.findall('(<div class="listing easyClear.*?</div>)',source,re.S)
    elif ci == 1:
        blocks = re.findall('(<div class="property_title">.*?</div>)', source, re.S)
    elif ci == 2:
        blocks = re.findall('(<div class="shortSellDetails">.*?</div>)',source,re.S)
    else:
        blocks = []
    return blocks
# 对匹配为空进行处理
def pankong(poi_xx):
    if len(poi_xx)==0:
        poi_xx = ''
    else:
        poi_xx = poi_xx[0]
    return poi_xx
def tiaoguo(selector):
    guolvcibiao = ['市']
    city = selector.xpath('//li[@class="cityName tabItem dropDown hvrIE6"]/span/span/text()')
    city = pankong(city)
    # 对应的城市id
    sqli = "select region_id from " + db + ".map_region" + " where region_ch_name = " + "'%s'" % (city)
    num_result = cur.execute(sqli)
    if not num_result:
        region_id = ''
    else:
        region_id = cur.fetchmany(1)
        region_id = region_id[0][0]
    # 过滤已经抓取完成的城市
    if region_id in hulvcities:
        return city,region_id,True
    else:
        return city,region_id,False
def yemianjiexi(block,ci):
    xiangqingselector = ''
    poi_ch_name = ''
    poi_en_name = ''
    poi_loc_name = ''
    poi_telephone =''
    poi_address =''
    poi_rank=''
    comments_count=''

    selector = etree.HTML(block)
    # 详情页信息获取异常标记
    tiaoguopoi = 0

    if ci == 0:
        # 详情页url

        xiangqingurl = selector.xpath('//div[@class="listing_title"]/a/@href')[0]
        xiangqingurl = starturl + xiangqingurl
        print '详情页', xiangqingurl
        try:
            xiangqinghtml = getsource(xiangqingurl)
        except:
            tiaoguopoi = 1
            return tiaoguopoi, xiangqingselector, poi_ch_name, poi_en_name, poi_loc_name, poi_telephone, poi_address, poi_rank, comments_count
        else:
            time.sleep(tingliu)
            xiangqingselector = etree.HTML(xiangqinghtml)

            # 名称
            name0 = selector.xpath('//div[@class="listing_title"]/a/text()')
            name0 = pankong(name0)

            name1 = xiangqingselector.xpath('//span[@class="altHead"]/text()')
            name1 = pankong(name1)
            shouzimu0 = name0[0].encode('utf-8')
            if not name1:
                if shouzimu0.isalpha():
                    poi_en_name = name0
                    poi_ch_name = ''
                else:
                    poi_en_name = ''
                    poi_ch_name = name0
            else:
                if shouzimu0.isalpha():
                    poi_en_name = name0
                    poi_ch_name = name1
                else:
                    poi_en_name = name1
                    poi_ch_name = name0

            poi_loc_name = poi_en_name

            comments_count = xiangqingselector.xpath('//a[@class="more taLnk"]/@content')
            comments_count = pankong(comments_count)
            poi_rank = xiangqingselector.xpath('//b[@class="rank"]/text()')
            poi_rank = pankong(poi_rank)
            if poi_rank:
                poi_rank = qushuzi(poi_rank)
            # 酒店类的电话获取还未完成，后期优化
            poi_telephone = ''
            # 地址
            street_address = xiangqingselector.xpath('//span[@class="street-address"]/text()')
            street_address = pankong(street_address)

            extended_address = xiangqingselector.xpath('//span[@class="extended-address"]/text()')
            extended_address = pankong(extended_address)

            addresslocality = xiangqingselector.xpath('//span[@property="addressLocality"]/text()')
            addresslocality = pankong(addresslocality)

            addressregion = xiangqingselector.xpath('//span[@property="addressRegion"]/text()')
            addressregion = pankong(addressregion)

            postcode = xiangqingselector.xpath('//span[@property="postalCode"]/text()')
            postcode = pankong(postcode)

    elif ci == 1:
        # 详情页url
        xiangqingurl = selector.xpath('//div[@class="property_title"]/a/@href')[0]
        xiangqingurl = starturl + xiangqingurl
        print '详情页', xiangqingurl
        try:
            xiangqinghtml = getsource(xiangqingurl)
        except:
            tiaoguopoi = 1
            return tiaoguopoi, xiangqingselector, poi_ch_name, poi_en_name, poi_loc_name, poi_telephone, poi_address, poi_rank, comments_count
        else:
            time.sleep(tingliu)
            xiangqingselector = etree.HTML(xiangqinghtml)
            # 名称
            name0 = selector.xpath('//a[@target="_blank"]/text()')
            name0 = pankong(name0).strip()
            if not name0:
                name0 = xiangqingselector.xpath('//h1[@id="HEADING"]/text()')
                name0 = pankong(name0).strip()
            name1 = xiangqingselector.xpath('//span[@class="altHead"]/text()')
            name1 = pankong(name1)
            shouzimu0 = name0[0].encode('utf-8')
            if not name1:
                if shouzimu0.isalpha():
                    poi_en_name = name0
                    poi_ch_name = ''
                else:
                    poi_en_name = ''
                    poi_ch_name = name0
            else:
                if shouzimu0.isalpha():
                    poi_en_name = name0
                    poi_ch_name = name1
                else:
                    poi_en_name = name1
                    poi_ch_name = name0
            poi_loc_name = poi_en_name

            comments_count = xiangqingselector.xpath('//a[@class="more"]/@content')
            comments_count = pankong(comments_count)
            poi_rank = xiangqingselector.xpath('//b[@class="rank_text wrap"]/span/text()')
            poi_rank = pankong(poi_rank)
            if poi_rank:
                poi_rank = qushuzi(poi_rank)
            poi_telephone = xiangqingselector.xpath('//div[@class="phoneNumber"]/text()')
            poi_telephone = pankong(poi_telephone)
            if poi_telephone:
                for i,ch in enumerate(poi_telephone):
                    if ch.isdigit():
                        tempi = i
                        break
                poi_telephone = poi_telephone[tempi:]

            # 地址
            street_address = xiangqingselector.xpath('//span[@class="street-address"]/text()')
            street_address = pankong(street_address)

            extended_address = xiangqingselector.xpath('//span[@class="extended-address"]/text()')
            extended_address = pankong(extended_address)

            addresslocality = xiangqingselector.xpath('//span[@property="addressLocality"]/text()')
            addresslocality = pankong(addresslocality)

            addressregion = xiangqingselector.xpath('//span[@property="addressRegion"]/text()')
            addressregion = pankong(addressregion)

            postcode = xiangqingselector.xpath('//span[@property="postalCode"]/text()')
            postcode = pankong(postcode)

    elif ci == 2:
        # 详情页url
        xiangqingurl = selector.xpath('//a[@class="property_title"]/@href')[0]
        xiangqingurl = starturl + xiangqingurl
        print '详情页', xiangqingurl
        try:
            xiangqinghtml = getsource(xiangqingurl)
        except:
            tiaoguopoi = 1
            return tiaoguopoi,xiangqingselector,poi_ch_name,poi_en_name,poi_loc_name,poi_telephone,poi_address,poi_rank,comments_count
        else:
            time.sleep(tingliu)
            xiangqingselector = etree.HTML(xiangqinghtml)

            # 名称
            poi_ch_name = ''
            poi_en_name = selector.xpath('//a[@target="_blank"]/text()')
            poi_en_name = pankong(poi_en_name)
            poi_en_name = poi_en_name.strip()
            poi_loc_name = poi_en_name

            comments_count = xiangqingselector.xpath('//a[@class="more"]/@content')
            comments_count = pankong(comments_count)
            poi_rank = xiangqingselector.xpath('//b[@class="rank_text wrap"]/span/text()')
            poi_rank = pankong(poi_rank)
            if poi_rank:
                poi_rank = qushuzi(poi_rank)
            poi_telephone = xiangqingselector.xpath('//div[@class="fl phoneNumber"]/text()')
            poi_telephone = pankong(poi_telephone)

            # 地址
            street_address = xiangqingselector.xpath('//span[@class="street-address"]/text()')
            street_address = pankong(street_address)

            extended_address = xiangqingselector.xpath('//span[@class="extended-address"]/text()')
            extended_address = pankong(extended_address)

            addresslocality = xiangqingselector.xpath('//span[@property="addressLocality"]/text()')
            addresslocality = pankong(addresslocality)

            addressregion = xiangqingselector.xpath('//span[@property="addressRegion"]/text()')
            addressregion = pankong(addressregion)

            postcode = xiangqingselector.xpath('//span[@property="postalCode"]/text()')
            postcode = pankong(postcode)

    if extended_address:
        poi_address = street_address + ',' + extended_address+','+addresslocality + ',' + addressregion + postcode
    else:
        poi_address = street_address + ',' + addresslocality + ',' + addressregion + postcode

    if not poi_telephone:
        poi_telephone = ''
    else:
        pass
    return tiaoguopoi,xiangqingselector,poi_ch_name,poi_en_name,poi_loc_name,poi_telephone,poi_address,poi_rank,comments_count

if __name__ == '__main__':
    starturl = 'http://www.tripadvisor.cn'
    tingliu = 2
    db = 'map'
    # 数据表
    tb = 'map_poi'
    # 希望跳过抓取的城市
    hulvcities = range(1,2)
    # 来源
    source = 'tripadvisor'
    # 连接数据库
    try:
        # conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='123456', port=3306, charset='utf8')
        conn = MySQLdb.connect(host='172.22.185.130', user='root', passwd='123456', port=3306, charset='utf8')
        cur = conn.cursor()
        cur.execute('set interactive_timeout=96*3600')
        conn.select_db(db)
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    for i in range(0,51):
        # 城市列表页
        # url = 'http://www.tripadvisor.cn/TourismChildrenAjax?geo=191&offset=%d&desktop=true'% (i)
        url = 'http://www.tripadvisor.cn/TourismChildrenAjax?geo=150768&offset=%d&desktop=true' % (i)
        print '城市列表页：',url
        html = getsource(url)
        time.sleep(tingliu)
        blocks = getcityblock(html)
        for j, block in enumerate(blocks):
            selector1 = etree.HTML(block)

            # 城市主页
            sub_url = selector1.xpath('//a/@href')[0]
            zhuye_url = starturl+sub_url
            print '城市主页：',zhuye_url
            zhuye_html = getsource(zhuye_url)
            time.sleep(tingliu)
            zhuye_selector = etree.HTML(zhuye_html)
            poi_region,region_id, tiaoma = tiaoguo(zhuye_selector)
            if tiaoma:
                pass
            else:
                hotel_url = zhuye_selector.xpath('//li[@class="hotels twoLines"]/a/@href')[0]
                jingdian_url = zhuye_selector.xpath('//li[@class="attractions twoLines"]/a/@href')[0]
                canting_url = zhuye_selector.xpath('//li[@class="restaurants twoLines"]/a/@href')[0]
                city_urls = [hotel_url,jingdian_url,canting_url]
                for ci,cityurl in enumerate(city_urls):
                    city_url = starturl+cityurl
                    print '行业url',city_url
                    if ci ==0:
                        tag_id = 2
                    if ci == 1:
                        tag_id = 3
                    if ci == 2:
                        tag_id = 1
                    dizhiyuanshu = city_url.split('-')
                    sub_html = getsource(city_url)
                    time.sleep(tingliu)
                    sub_selector = etree.HTML(sub_html)
                    # 爬取的页数
                    poiyeshu = sub_selector.xpath('//a[@class="pageNum last taLnk"]/@data-page-number')
                    if len(poiyeshu) == 0:
                        poiyeshu = 1
                    else:
                        poiyeshu = poiyeshu[0]

                    for ye in range(1,int(poiyeshu)+1):
                        index = 30*(ye-1)
                        if index != 0:
                            if ci == 0:
                                dangqianurl = dizhiyuanshu[0]+'-'+dizhiyuanshu[1]+'-'+'oa'+str(index)+'-'+dizhiyuanshu[2]+'-'+dizhiyuanshu[3]
                            if ci == 1:
                                dangqianhtml = dizhiyuanshu[0]+'-'+dizhiyuanshu[1]+'-'+dizhiyuanshu[2]+'-'+'oa'+str(index)+'-'+dizhiyuanshu[3]
                            if ci == 2:
                                dangqianhtml = dizhiyuanshu[0]+'-'+dizhiyuanshu[1]+'-'+'oa'+str(index)+'-'+dizhiyuanshu[2]
                        else:
                            dangqianurl = city_url
                        print '列表页url',dangqianurl
                        dangqianhtml = getsource(dangqianurl)
                        time.sleep(tingliu)
                        poiblocks = getpoiblock(dangqianhtml,ci)
                        print '当前页的poi数',len(poiblocks)
                        for poiblock in poiblocks:

                            tiaoguopoi,xiangqingselector,poi_ch_name, poi_en_name, poi_loc_name, poi_telephone, poi_address, poi_rank,comments_count = yemianjiexi(poiblock,ci)
                            # tiaoguopoi为poi详情页获取阶段，异常获取标志。若获取异常，tiaoguopoi为1，跳过该poi
                            if tiaoguopoi:
                                pass
                            else:
                                sqli = "INSERT INTO " + db + "." + tb + "(poi_ch_name,poi_en_name,poi_loc_name,poi_region_id,poi_region,poi_tag_id,poi_rank,poi_address,poi_telephone,comments_count,source_website)" + " VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

                                # 判断数据库是否已经存在城市数据，决定是插入数据还是更新数据。
                                sqli1 = "select * from " + db + "." + tb + " where poi_ch_name = " + "'%s'" % (poi_ch_name)
                                sqli2 = "select * from " + db + "." + tb + " where poi_en_name = " + "'%s'" % (poi_en_name)

                                try:
                                    r1 = cur.execute(sqli1)
                                    r2 = cur.execute(sqli2)
                                except:
                                    pass

                                if not poi_ch_name :
                                    r1 = 0
                                if not poi_en_name :
                                    r2 = 0
                                print '中文：',poi_ch_name,'英文：',poi_en_name
                                print '查询结果：','中文',r1,'英文',r2

                                if r1 or r2:
                                    print '已经存在记录，迭代数据 ... ...'
                                    pass
                                else:
                                    print '插入新POI... ...'
                                    print '中文：' + poi_ch_name,'英文：' + poi_en_name, '本地语言名称:' + poi_en_name, '城市id:' + str(region_id),'城市:'+poi_region, '类型：' + str(tag_id), '评论数:' + str(comments_count),  '排名:' + str(poi_rank), '地址:' + str(poi_address), '电话:' + str(poi_telephone)
                                    cur.execute(sqli,(poi_ch_name, poi_en_name, poi_loc_name, region_id,poi_region, tag_id,poi_rank,poi_address,poi_telephone,comments_count,source))
                                    conn.commit()
                                print '------------------------------------------------'
    cur.close()
    conn.close()
    print '------------finished--------------'
