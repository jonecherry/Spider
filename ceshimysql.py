#coding=utf-8
import MySQLdb
db = 'southamerica'
sqli = 'INSERT INTO ceshi VALUES(1,"haode")'
try:
    conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='123456', port=3306, charset='utf8',db='southamerica',)
    cur = conn.cursor()
    # cur.execute("INSERT INTO southamerica.巴西(chinesename,englishname) VALUES( '艺术桥','艺术桥' )")
    cur.execute(sqli)
    cur.execute("insert into ceshi values(100,'Tom')")

    # cur.execute('set interactive_timeout=96*3600')
except MySQLdb.Error, e:
    print "Mysql Error %d: %s" % (e.args[0], e.args[1])


cur.close()
conn.commit()
conn.close()
print 'ok'