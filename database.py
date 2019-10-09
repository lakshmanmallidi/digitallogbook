import mysql.connector

host = '127.0.0.1'
user = 'root'
passwd = 'your_password'
db = 'logbook'
def connection():
    conn = mysql.connector.connect(host=host,
                                   user=user,
                                   passwd=passwd,
                                   db=db)
    c = conn.cursor()
    return c, conn
