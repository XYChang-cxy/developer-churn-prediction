import pymysql


MYSQL_HOST = 'localhost'
MYSQL_DBNAME = 'churn_database'
MYSQL_USER = 'root'
MYSQL_PASSWD = '123456'

fmt_day = '%Y-%m-%d'
fmt_second = '%Y-%m-%d %H:%M:%S'

def dbHandle():
    conn = pymysql.connect(
        host=MYSQL_HOST,
        db=MYSQL_DBNAME,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWD,
        charset='utf8',
        use_unicode=True
    )
    return conn
