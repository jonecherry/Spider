#encoding=utf-8
from lxml import etree
import requests
import os
import sys
import MySQLdb
import re
import random
reload(sys)
sys.setdefaultencoding("utf-8")

def xiaoxie(city_en_name):
    city_en_name = city_en_name.split()
    en_name = ''
    for name in city_en_name:
        en_name = en_name + name.lower()
    return en_name
#getsource用来获取网页源代码
def getsource(url):
    headlist = [{'User-Agent':'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.'},
      {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},
      {'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;'},
      {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'},
      {'User-Agent':'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)'},
      {'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)'},
      {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},
      {'User-Agent':'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11'},
      {'User-Agent':'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'},
      {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'},
      {'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)'}]
    html = requests.get(url,headers = headlist[random.randint(0,10)])
    html.encoding = 'utf-8'
    return html.text
#获取信息块
def getblock(source):
    blocks = re.findall('(<div class="ct-text ".*?</div>)',source,re.S)
    return blocks

def pankong(re):
    if len(re)==0:
        re = ''
    else:
        re = re [0]
        re = re.strip()
    return re
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
def qushuzi(str):
    num = ''
    if not str:
        return num
    else:
        for sr in str:
            if sr.isdigit():
                num = num+sr
        return num
def subjiexi(url):
    subhtml = getsource(url)
    subselector = etree.HTML(subhtml)

    # 地址
    poi_address1 = subselector.xpath('//span[@itemprop="locality region"]/text()')
    poi_address1 = pankong(poi_address1)
    poi_address2 = subselector.xpath('//span[@itemprop="street-address"]/@title')
    poi_address2 = pankong(poi_address2)
    poi_address = poi_address1+poi_address2
    print '地址：',poi_address
    # 电话
    poi_telephone = subselector.xpath('//span[@itemprop="tel"]/text()')
    poi_telephone = pankong(poi_telephone)
    print '电话：',poi_telephone
    # 评论数
    psp = subselector.xpath('//div[@class="brief-info"]/span/text()')
    comments_count = pankong(psp)
    comments_count = qushuzi(comments_count)
    print '评论数：',comments_count
    # 评分
    poi_score = psp[2]
    for chi,ch in enumerate(poi_score):
        if ch.isdigit():
            ni = chi
            break
    poi_score = poi_score[ni:]
    print '评分',poi_score

# 列表页解析
def jiexi(url,tag_id):
    tempurl = url +'1'
    print '列表页', tempurl
    dangqianselector = url_to_selector(tempurl)
    # 购物&美食
    if tag_id in [1,4]:
        print '购物or美食'
        try:
            zongyeshu = dangqianselector.xpath('//div[@class="Pages"]/a/@data-ga-page')[-2]
        except:
            pass
        else:
            for ye in range(1,int(zongyeshu)+1):
                lieurl = url+ "%s"%(ye)
                print '列表ye',lieurl
                html = getsource(lieurl)
                blocks = re.findall('(<ul class="detail">.*?</ul>)', html, re.S)
                print '这页poi数量',len(blocks)
                for block in blocks:
                    selector = etree.HTML(block)
                    #中文名称、英文名称、本地名称
                    name = selector.xpath('///a[@class="BL"]/@title')[0]
                    shouzimu = name[0].encode('utf-8')
                    if shouzimu.isalpha():
                        poi_ch_name = ''
                        poi_en_name = name
                    else:
                        poi_ch_name = name
                        poi_en_name = ''
                    poi_loc_name = poi_en_name
                    print '名称：',poi_ch_name,poi_en_name
                    # 判断数据库是否已经存在该POI记录，决定是插入数据还是更新数据。
                    sqli_ch = "select * from " + db + "." + tb + " where poi_ch_name = " + "'%s'" % (poi_ch_name)
                    sqli_en = "select * from " + db + "." + tb + " where poi_en_name = " + "'%s'" % (poi_en_name)
                    try:
                        r1 = cur.execute(sqli_ch)
                        r2 = cur.execute(sqli_en)
                    except:
                        pass
                    else:
                        if poi_ch_name == '':
                            r1 = 0
                        if poi_en_name == '':
                            r2 = 0
                        print '查询结果：'
                        print '中文', r1, '英文', r2
                        if r1 or r2:
                            print '已经存在记录，更新数据... ...'
                            pass
                        else:
                            # 详情链接
                            suburl = selector.xpath('//a[@class="BL"]/@href')[0]
                            suburl = 'http://www.dianping.com'+suburl
                            print '详情链接', suburl

                            subhtml = getsource(suburl)
                            subselector = etree.HTML(subhtml)
                            # 地址
                            poi_address1 = subselector.xpath('//span[@itemprop="locality region"]/text()')
                            poi_address1 = pankong(poi_address1)
                            poi_address2 = subselector.xpath('//span[@itemprop="street-address"]/@title')
                            poi_address2 = pankong(poi_address2)
                            poi_address = poi_address1 + poi_address2
                            print '地址：', poi_address
                            # 电话
                            poi_telephone = subselector.xpath('//span[@itemprop="tel"]/text()')
                            poi_telephone = pankong(poi_telephone)
                            print '电话：', poi_telephone
                            # 评论数
                            psp = subselector.xpath('//div[@class="brief-info"]/span/text()')
                            comments_count = pankong(psp)
                            comments_count = qushuzi(comments_count)
                            print '评论数：', comments_count
                            # 评分
                            try:
                                poi_score = psp[2]
                            except:
                                poi_score = ''
                            else:
                                for chi, ch in enumerate(poi_score):
                                    if ch.isdigit():
                                        ni = chi
                                        break
                                poi_score = poi_score[ni:]
                            print '评分', poi_score

                            if r1 or r2:
                                print '已经存在记录，更新数据... ...'
                                pass
                            else:
                                print '新增POI... ...'
                                print '中文：' + poi_ch_name, '英文：' + poi_en_name, '本地语言名称' + poi_en_name, '城市id' + str(poi_region_id), '类型：' + str(tag_id), '评论数' + str(comments_count), '评分' + str(poi_score), '地址' + poi_address, '电话' + poi_telephone
                                sqli = "INSERT INTO " + db + "." + tb + "(poi_ch_name,poi_en_name,poi_loc_name,poi_region_id,poi_tag_id,poi_score,poi_address,poi_telephone,comments_count,source_website)" + " VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                                cur.execute(sqli, (poi_ch_name, poi_en_name, poi_loc_name, poi_region_id, tag_id,poi_score, poi_address, poi_telephone,comments_count, source))
                                conn.commit()
                            print '----------------------------------------'
    # 景点
    elif tag_id == 3:
        print '景点'
        try:
            zongyeshu = dangqianselector.xpath('//div[@class="Pages"]/a/@data-ga-page')[-2]
        except:
            pass
        else:
            for ye in range(1, int(zongyeshu) + 1):
                jingurl = url + "%s"%(ye)
                html = getsource(jingurl)

                blocks = re.findall('(<li data-poi.*?</li>)',html,re.S)
                for block in blocks:
                    selector = etree.HTML(block)
                    # 中文名称、英文名称、本地名称
                    name = selector.xpath('//div[@class="poi-title"]/h4/a/text()')[0]
                    shouzimu = name[0].encode('utf-8')
                    if shouzimu.isalpha():
                        poi_ch_name = ''
                        poi_en_name = name
                    else:
                        poi_ch_name = name
                        poi_en_name = ''
                    poi_loc_name = poi_en_name
                    print '中文名称：',poi_ch_name,'英文名称：',poi_en_name
                    # 判断数据库是否已经存在该POI记录，决定是插入数据还是更新数据。
                    sqli_ch = "select * from " + db + "." + tb + " where poi_ch_name = " + "'%s'" % (poi_ch_name)
                    sqli_en = "select * from " + db + "." + tb + " where poi_en_name = " + "'%s'" % (poi_en_name)
                    try:
                        r1 = cur.execute(sqli_ch)
                        r2 = cur.execute(sqli_en)
                    except:
                        pass
                    else:
                        if poi_ch_name == '':
                            r1 = 0
                        if poi_en_name == '':
                            r2 = 0
                        print '查询结果：'
                        print '中文', r1, '英文', r2
                        if r1 or r2:
                            print '已经存在记录，更新数据... ...'
                            pass
                        else:
                            # 详情链接
                            suburl = selector.xpath('//div[@class="poi-title"]/h4/a/@href')[0]
                            suburl = 'http://www.dianping.com'+suburl
                            print '详情链接', suburl

                            subhtml = getsource(suburl)
                            subselector = etree.HTML(subhtml)

                            # 地址
                            poi_address1 = subselector.xpath('//span[@itemprop="locality region"]/text()')
                            poi_address1 = pankong(poi_address1)
                            poi_address2 = subselector.xpath('//span[@itemprop="street-address"]/@title')
                            poi_address2 = pankong(poi_address2)
                            poi_address = poi_address1 + poi_address2
                            print '地址：', poi_address
                            # 电话
                            poi_telephone = subselector.xpath('//span[@itemprop="tel"]/text()')
                            poi_telephone = pankong(poi_telephone)
                            print '电话：', poi_telephone
                            # 评论数
                            psp = subselector.xpath('//div[@class="brief-info"]/span/text()')
                            comments_count = pankong(psp)
                            comments_count = qushuzi(comments_count)
                            print '评论数：', comments_count
                            # 评分
                            if not len(psp)==5:
                                poi_score = ''
                            else:
                                poi_score = psp[2]
                                for chi, ch in enumerate(poi_score):
                                    if ch.isdigit():
                                        ni = chi
                                        break
                                poi_score = poi_score[ni:]
                            print '评分', poi_score

                            if r1 :
                                print '已经存在记录，更新数据... ...'
                                pass
                            else:
                                print '新增POI... ...'
                                print '中文：' + poi_ch_name, '英文：' + poi_en_name, '本地语言名称' + poi_en_name, '城市id' + str(poi_region_id), '类型：' + str(tag_id), '评论数' + str(comments_count), '评分' + str(poi_score), '地址' + poi_address, '电话' + poi_telephone
                                sqli = "INSERT INTO " + db + "." + tb + "(poi_ch_name,poi_en_name,poi_loc_name,poi_region_id,poi_tag_id,poi_score,poi_address,poi_telephone,comments_count,source_website)" + " VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                                cur.execute(sqli, (poi_ch_name, poi_en_name, poi_loc_name, poi_region_id, tag_id, poi_score, poi_address,poi_telephone, comments_count, source))
                                conn.commit()
                            print '----------------------------------------'
    # 酒店
    elif tag_id == 2:
        print '酒店'
        try:
            zongyeshu = dangqianselector.xpath('//div[@class="page"]/a/@data-ga-page')[-2]
        except:
            pass
        else:
            for ye in range(1, int(zongyeshu) + 1):
                jingurl = url + "%s" % (ye)
                html = getsource(jingurl)

                blocks = re.findall('(<li class=" hotel-block J_hotel-block".*?</li>)', html, re.S)
                for block in blocks:

                    selector = etree.HTML(block)
                    # 详情链接
                    suburl = selector.xpath('//h2[@class="hotel-name"]/a/@href')[0]
                    suburl = 'http://www.dianping.com' + suburl
                    print '详情链接', suburl
                    subhtml = getsource(suburl)
                    subselector = etree.HTML(subhtml)
                    # 中文名称、英文名称、本地名称
                    name0 = subselector.xpath('//h1[@class="shop-name"]/text()')
                    name0 = pankong(name0)
                    name1 = subselector.xpath('//span[@class="shop-enname"]/text()')
                    name1 = pankong(name1)

                    shouzimu = name0[0] .encode('utf-8')
                    if shouzimu.isalpha():
                        poi_ch_name = ''
                        poi_en_name = name0
                    else:
                        poi_ch_name = name0
                        poi_en_name = name1
                    poi_loc_name = poi_en_name
                    print '中文名称：', poi_ch_name, '英文名称：', poi_en_name


                    # 判断数据库是否已经存在该POI记录，决定是插入数据还是更新数据。
                    sqli_ch = "select * from " + db + "." + tb + " where poi_ch_name = " + "'%s'" % (poi_ch_name)
                    sqli_en = "select * from " + db + "." + tb + " where poi_en_name = " + "'%s'" % (poi_en_name)
                    try:
                        r1 = cur.execute(sqli_ch)
                        r2 = cur.execute(sqli_en)
                    except:
                        pass
                    else:
                        if poi_ch_name == '':
                            r1 = 0
                        if poi_en_name == '':
                            r2 = 0
                        print '查询结果：'
                        print '中文',r1,'英文',r2
                        if r1 or r2:
                            print '已经存在记录，更新数据... ...'
                            pass
                        else:
                            # 地址
                            poi_address = subselector.xpath('//p[@class="shop-address"]/text()')
                            poi_address =pankong(poi_address)
                            poi_address = poi_address[3:]
                            # 评分
                            poi_score = subselector.xpath('//p[@class="info shop-star"]/span[1]/@class')
                            if not poi_score:
                                poi_score = ''
                            else:
                                poi_score = qushuzi(poi_score[0])
                                poi_score = round(int(poi_score)/5,2)

                            # 评论数
                            comments_count = subselector.xpath('//p[@class="info shop-star"]/span[@class="item"]/text()')
                            if not comments_count:
                                comments_count = ''
                            else:
                                comments = ''
                                for dd in comments_count[0]:
                                    if dd.isdigit():
                                        comments = comments +dd
                                comments_count = comments
                            print '评论数：',comments_count
                            # 电话
                            poi_telephone = ''

                            print '新增POI... ...'
                            print '中文：' + poi_ch_name, '英文：' + poi_en_name, '本地语言名称' + poi_en_name, '城市id' + str(poi_region_id), '类型：' + str(tag_id), '评论数' + str(comments_count), '评分' + str(poi_score), '地址' + poi_address, '电话' + poi_telephone
                            sqli = "INSERT INTO " + db + "." + tb + "(poi_ch_name,poi_en_name,poi_loc_name,poi_region_id,poi_tag_id,poi_score,poi_address,poi_telephone,comments_count,source_website)" + " VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                            cur.execute(sqli, (poi_ch_name, poi_en_name, poi_loc_name, poi_region_id, tag_id, poi_score, poi_address,poi_telephone, comments_count, source))
                            conn.commit()
                            print '----------------------------------------'
    else:
        pass


def url_to_selector(url):
    html = getsource(url)
    return etree.HTML(html)

if __name__ == '__main__':
    # 设置白名单，过滤国家
    chengshibaimingdan = range(1,2)
    # 来源
    source = '大众点评'
    db = 'map'
    # 数据表
    tb = 'map_poi1'
    area = 'usa'
    # 标签id 美食：1，酒店：2，景点：3，购物：4，娱乐：5，交通：6
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
    # 抽取待抓取的城市列表
    sqli0 = "select region_en_name,region_id from map.map_region"
    num_city = cur.execute(sqli0)
    cities = cur.fetchmany(num_city)
    for city in cities:
        poi_region_id = city[1]
        city = city[0]
        city = city.strip()
        city = xiaoxie(city)
        if poi_region_id in chengshibaimingdan:
            print '已经完成',city,'的抓取'
            pass
        else:
            starturl = 'http://www.dianping.com/'+city+'/food/p1'
            starthtml = getsource(starturl)
            # print starthtml
            try:
                startselector = etree.HTML(starthtml)
            except:
                pass
            else:
                poiyeshu = startselector.xpath('//div[@class="Pages"]')
                if len(poiyeshu)== 0:
                    print '城市',city,'在点评上没有数据'
                    pass
                else:
                    print '开始抓取', city
                    url_food = 'http://www.dianping.com/'+city+'/food/p'
                    url_shopping = 'http://www.dianping.com/'+city+'/shopping/p'
                    url_jingdian = 'http://www.dianping.com/'+city+'/attraction?district=&category=&pageNum='
                    url_jiudian = 'http://www.dianping.com/'+city+'/hotel/p'
                    urllist = [url_food,url_shopping,url_jingdian,url_jingdian]
                    for ui,url in enumerate(urllist):
                        if ui == 0:
                            tag_id = 1
                        elif ui == 1:
                            tag_id = 4
                        elif ui == 2:
                            tag_id = 3
                        elif ui == 3:
                            tag_id = 2
                        else:
                            tag_id = ''
                        jiexi(url,tag_id)

    cur.close()
    conn.close()
    jilu.close()
    print 'finished'