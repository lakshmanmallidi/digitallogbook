import MySQLdb


def connection():
    conn = MySQLdb.connect(host="localhost",
                           user="your_sql_user",
                           passwd="your_sql_user_password",
                           db="your_database_name")
    c = conn.cursor()
    return c, conn
