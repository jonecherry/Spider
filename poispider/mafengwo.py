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


# 页面解析
def jiexi(html):
    blocks = getblock(html)
    for block in blocks:
        selector = etree.HTML(block)
        poi = selector.xpath('//h3')[0]
        poi = poi.xpath('string(.)')
        # poi = poi.replace('\n','')

        elements = poi.split('-')
        leixin = elements[0]
        leixin = leixin.replace(' ', '')
        leixin = leixin.replace('\n', '')

        temp = elements[1].split()

        if len(temp) == 0:
            continue
        shouzimu = str(temp[0])

        if len(temp)==1 and not shouzimu.isalpha():
            zhongwen = temp[0]
            yingwen = ''
        elif shouzimu.isalpha():
            yingwen = ''
            for i in range(0, len(temp)):
                yingwen = yingwen + ' ' + temp[i]
            zhongwen = ''
        else:
            zhongwen = temp[0]
            yingwen = ''
            for i in range(1, len(temp)):
                yingwen = yingwen + ' ' + temp[i]

        # 判断数据库是否已经存在该POI记录，决定是插入数据还是更新数据。
        sqli1 = "select * from " + db + "." + tb + " where poi_ch_name = " + "'%s'" % (zhongwen)
        sqli2 = "select * from " + db + "." + tb + " where poi_en_name = " + "'%s'" % (yingwen)
        try:
            r1 = cur.execute(sqli1)
            r2 = cur.execute(sqli2)
        except:
            pass
        else:
            # 国家、城市
            poiinfos = selector.xpath('//li/a/text()')
            country_city = poiinfos[0]
            country_city = country_city.split('-')
            country = country_city[0]
            city = country_city[1]

            # 查询城市id
            sqli1 = 'select region_id from map.map_region where region_ch_name = '+"'%s'"%(city)
            cur.execute(sqli1)
            id = cur.fetchmany(1)

            if len(id)==0:
                region_id = ''
            else:
                region_id = id[0][0]


            # 评论数
            pinglunshu = getnum(poiinfos[1])
            # 相关游记数
            relatedyoujishu = getnum(poiinfos[2])

            # tag_id
            if leixin == '美食':
                tag_id = 1
            elif leixin == '酒店':
                tag_id = 2
            elif leixin == '景点':
                tag_id = 3
            elif leixin == '购物':
                tag_id =4
            elif leixin == '娱乐':
                tag_id = 5
            elif leixin == '交通':
                tag_id = 6
            else:
                tag_id = ''


            # 详情链接
            link = selector.xpath('//h3/a/@href')[0]
            print '详情链接',link
            try:
                subhtml = getsource(link)
                subselector = etree.HTML(subhtml)
            except:
                pass
            else:
                if leixin == '景点':
                    quguoshoucang = subselector.xpath('//span[@class="pa-num"]/text()')
                    # 去过数
                    quguonum = quguoshoucang[1]
                    # 收藏数
                    shoucangshu = quguoshoucang[0]
                    # 评分
                    poi_score = ''
                    # 排名
                    poi_rank = ''
                    # 地址
                    poi_address = ''
                    poi_telephone_tag = subselector.xpath('//dl[@class="intro"]/dd/span/text()')
                    if '电话' in poi_telephone_tag:
                        for ti,tele_tag in enumerate(poi_telephone_tag):
                            if tele_tag == '电话':
                                telei = str(ti+1)
                        xpath_tele = '//dl[@class="intro"]/dd['+telei+']/p/text()'
                        poi_telephone = subselector.xpath(xpath_tele)[0]
                    else:
                        poi_telephone =''

                else:
                    quguonum = ''
                    shoucangshu = ''
                    # 评分
                    poi_score = subselector.xpath('//span[@class="score-info"]/em/text()')
                    if not poi_score:
                        poi_score = ''
                    else:
                        poi_score = poi_score[0]
                    # 等级
                    poi_rank = subselector.xpath('//div[@class="ranking"]/em/text()')
                    if not poi_rank:
                        poi_rank = ''
                    else:
                        poi_rank = poi_rank[0][3:]
                    # 地址，电话
                    box_info = subselector.xpath('//div[@class="m-box m-info"]/ul[@class="clearfix"]/li/text()')
                    # print '++++++++',len(box_info)
                    if len(box_info)>=4:
                        poi_address = subselector.xpath('//div[@class="m-box m-info"]/ul[@class="clearfix"]/li[1]/text()')[1].strip()
                        for chari,addchar in enumerate(poi_address):
                            if addchar == "：":
                                tempi = chari
                                poi_address = poi_address[tempi+1:]
                        poi_telephone = subselector.xpath('//div[@class="m-box m-info"]/ul[@class="clearfix"]/li[2]/text()')[1].strip()
                    else:
                        poi_telephone =''
                        poi_address = ''

                # print '国家:' + country, '城市：' + city, '中文：' + zhongwen, '英文：' + yingwen, '城市id' + str(region_id), '类型id：' + str(tag_id), '类型:' + leixin, \
                #     '评论数' + str(pinglunshu), '相关游记数' + str(relatedyoujishu), '去过数' + str(quguonum), '收藏数' + str(shoucangshu), '评分' + str(poi_score), \
                #     '排名' + str(poi_rank), '电话' + str(poi_telephone), '地址' + poi_address

                if r1 or r2:
                    print '已经存在记录，更新数据... ...'
                    pass
                else:
                    print '新增POI... ...'
                    sqli = "INSERT INTO " + db + "." + tb + "(poi_ch_name,poi_en_name,poi_loc_name,poi_region_id,poi_tag_id,poi_score,poi_rank,poi_address,poi_telephone,visited_count,comments_count,collection_count,source_website)" + " VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    # print sqli

                    cur.execute(sqli,(zhongwen,yingwen,yingwen,region_id,tag_id,poi_score,poi_rank,poi_address,poi_telephone,quguonum,pinglunshu,shoucangshu,source))
                    conn.commit()
                print '----------------------------------------'
if __name__ == '__main__':
    # tag
    taglist = {'美食':1,'酒店':2,'景点':3,'购物':4,'娱乐':5,'交通':6}

    # 设置白名单，过滤国家
    chengshibaimingdan = ['美国']
    # 来源
    source = '蚂蜂窝'

    db = 'map'
    # 数据表
    tb = 'map_poi_0'
    area = 'usa'

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
    sqli0 = "select region_ch_name from map.map_region"
    num_city = cur.execute(sqli0)
    cities = cur.fetchmany(num_city)

    for city in cities:
        city = city[0]
        city = city.strip()
        if city in chengshibaimingdan:
            pass
        else:
            url0 = 'http://www.mafengwo.cn/group/s.php?q=%s&p=1&t=poi&kt=1'%(city)
            print url0
            html0 = getsource(url0)
            if not html0:
                pass
            else:
                #获取爬取的页数
                selector0 = etree.HTML(html0)
                # temp0 = selector0.xpath('//div[@class="m-pagination"]/span[@class="count"]/text()')
                poinum = selector0.xpath('//p[@class="ser-result-primary"]/text()')[0]
                poinum = poinum.strip()
                for k,zifu in enumerate(poinum):
                    if poinum[k-1]=='结'and poinum[k]=='果':
                        si = k
                    if poinum[k] =='条':
                        ei = k
                try:
                    poinum = int(poinum[si+1:ei])
                except:
                    pass
                else:
                    print 'poi数量:',poinum

                    if poinum < 750:
                        yema = poinum / 15
                    else:
                        yema = 50

                    if yema == 0:
                        print '----------%s 1页---------'%(city)
                        url = 'http://www.mafengwo.cn/group/s.php?q=%s&p=%d&t=poi' % (city, 1)
                        html = getsource(url)
                        # jilu.write(html)
                        jiexi(html)
                    else:
                        for i in range(yema+1):
                            url = 'http://www.mafengwo.cn/group/s.php?q=%s&p=%d&t=poi'%(city,i)
                            html = getsource(url)
                            # jilu.write(html)
                            jiexi(html)

    cur.close()
    conn.close()
    jilu.close()
    print 'finished'