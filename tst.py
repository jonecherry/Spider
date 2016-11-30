#coding=utf-8
import random
import re
import sys
import urllib2

# import MySQLdb
import requests
# from lxml import etree
import socket
# import proxyIP

reload(sys)
sys.setdefaultencoding("utf-8")

#getsource用来获取网页源代码
def getsource(url):
    headers = {
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
        # 详情页 cookie
        # 'Cookie':'JSESSIONID=EE4F457A78D5ADB9B416BA9BD1260691; BIGipServerESI-WEB-APP-8080=748214282.36895.0000; PSSID="A1-wS2nsbT8yAaiz92yMmlx2BpnjzUUjx2BdSTY-18x2dyfQZ1yAMOOmix2BC4bxxs5fRAx3Dx3DS0YEN7J3xxOrhIYxxYDlHQyQx3Dx3D-9vvmzcndpRgQCGPd1c2qPQx3Dx3D-wx2BJQh9GKVmtdJw3700KssQx3Dx3D"; CUSTOMER="WUHAN UNIV"; E_GROUP_NAME="IC2 Platform"; esi.isLocalStorageCleared=true; Type=documents; Show=null; esi.docsActiveTab=0; esi.Type=; esi.FilterValue=; esi.GroupBy=; esi.FilterBy=; esi.Show=; esi.authorsList=; esi.frontList=; esi.fieldsList=; esi.instList=; esi.journalList=; esi.terriList=; esi.titleList=',
        # 列表页 cookie
        'Cookie' : 'Type=documents; Show=null; esi.docsActiveTab=0; esi.Type=; esi.FilterValue=; esi.GroupBy=; esi.FilterBy=; esi.Show=; esi.authorsList=; esi.frontList=; esi.fieldsList=; esi.instList=; esi.journalList=; esi.terriList=; esi.titleList=; clientId=CID1242b7d4b50d1e0ed3ac323a908e08bd; esi.isLocalStorageCleared=true; qq%5Flogin%5Fstate=54D44A36B7E6D2165B2090C42F8CB27E; JSESSIONID=811CB477BFE1C370AB4A99C711A0C0E1; _pk_ref.2.a2d0=%5B%22%22%2C%22%22%2C1480485842%2C%22http%3A%2F%2Fwww.lib.whu.edu.cn%2Fdc%2Furlto_proxy.asp%3Fid%3D638%26url%3Dhttp%3A%2F%2Firas.lib.whu.edu.cn%3A8080%2Fgo%3Fid%3DESI%26source_id%3DWHU03752%26u%3D%26title%3DESI%C2%A3%C2%A8Essential%20Science%20Indicators%C2%A3%C2%A9%22%5D; _pk_id.2.a2d0=b5d6c9744eade5ad.1480474056.2.1480485842.1480485842.; _pk_ses.2.a2d0=*'
    }
    socket.setdefaulttimeout(60)

    html = requests.get(url,headers = headers)
    html.encoding = 'utf-8'
    return html.text

if __name__ == '__main__':
    # 详情页 url
    # url = 'http://gateway.webofknowledge.com/gateway/Gateway.cgi?GWVersion=2&SrcAuth=TSMetrics&SrcApp=TSM_TEST&DestApp=WOS_CPL&DestLinkType=FullRecord&KeyUT=ISI:000262948300002'
    # 列表页 url
    url = 'http://iras.lib.whu.edu.cn:8080/rwt/ESI/https/MW3XTLUJN3SXT7DFPMYHI4DQNW3X85UTMW4YI3LTPMYGG55N/IndicatorsDataAction.action?_dc=1480468834254&type=documents&author=&researchField=CLINICAL%20MEDICINE&institution=&journal=&territory=&article_UT=&researchFront=&articleTitle=&docType=Top&year=&page=1&start=10&limit=10&sort=%5B%7B%22property%22%3A%22citations%22%2C%22direction%22%3A%22DESC%22%7D%5D'
    result = getsource(url)
    print result

