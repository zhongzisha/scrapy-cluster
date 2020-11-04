import pymysql


def test1():  # OK
    conn = pymysql.connect(host='localhost', user='root', password='zzs123456')
    cursor = conn.cursor()
    cursor.execute('SELECT VERSION()')
    result = cursor.fetchone()
    print(result)
    conn.close()

