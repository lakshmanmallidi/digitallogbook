import mysql.connector
import sys
try:
    ipaddress = raw_input("Enter your database server host address:")
    user_db = raw_input("Enter username:")
    password_db = raw_input("Enter password:")
    db_name = raw_input("Enter database name:")
    conn = mysql.connector.connect(host=ipaddress,
                                   user=user_db,
                                   passwd=password_db,
                                   db=db_name)
    c = conn.cursor()
    while True:
        choice = int(raw_input("-------------------------\nklef log book\n-------------------------\n1.Create New Room\n2.Delete Room\n3.Show all Room\n4.Initialize database\n5.Exit\nplease choose an option:"))
        if choice > 0 and choice < 6:
            if choice == 1:
                room = raw_input("Enter the Room number:")
                password = raw_input("Enter the password:")
                c.execute("SELECT * FROM rooms where room='{}'".format(room))
                if len(c.fetchall()) < 1:
                    c.execute("INSERT INTO rooms(room,password) VALUES('{}','{}')".format(room,password))
                    c.execute("CREATE TABLE {}(si INT NOT NULL PRIMARY KEY AUTO_INCREMENT,userId INT NOT NULL,purpose VARCHAR(30),equipmentid VARCHAR(20),datecol date NOT NULL,intime time NOT NULL,outtime time)".format(room))
                else:
                    print "The Room number is already existed"
            elif choice == 2:
                room = raw_input("Enter the Room number you want to delete:")
                c.execute("SELECT room FROM rooms where room='{}'".format(room))
                if len(c.fetchall()) > 0:
                    c.execute("DELETE FROM rooms where room='{}'".format(room))
                    c.execute("DROP TABLE {}".format(room))
                else:
                    print "Room number not existed"
            elif choice == 3:
                c.execute("SELECT room FROM rooms")
                print "----------------------\nRooms\n----------------------\n"
                for row in c.fetchall():
                    print row[0]
            elif choice == 4:
                c.execute("CREATE TABLE rooms(room varchar(10) NOT NULL, password varchar(20) NOT NULL)")
                c.execute("CREATE TABLE sessioncode(code varchar(32) NOT NULL)")
            else:
                break
        else:
            print "please choose a valid option"
    conn.commit()
    c.close()
    conn.close()
except Exception as e:
    print e
