import mysql.connector

def connection():
    conn = mysql.connector.connect(host='127.0.0.1',
                                   user='root',
                                   passwd='mydatabase123!',
                                   db='logbook')
    c = conn.cursor()
    return c, conn
