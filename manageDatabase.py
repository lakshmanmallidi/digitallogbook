import mysql.connector
import sys
import serial
from getpass import getpass
try:
    com = input("Enter Rfid detector com port(baudrate:9600):")
    ipaddress = input("Enter your database server host address:")
    user_db = input("Enter username:")
    password_db = getpass("Enter password:")
    choice = input("Enter Y to create new database or N to use existing database:")
    db_name = None
    if(choice == "Y" or choice=="y"):
        db_name = input("Enter database name:")
        c = mysql.connector.connect(host=ipaddress,
                                   user=user_db,
                                   passwd=password_db)
        cur = c.cursor()
        cur.execute('CREATE DATABASE '+db_name)
        c.commit()
        c.close()
    elif(choice=="N" or choice=="n"):
        db_name = input("Enter database name:")
    conn = mysql.connector.connect(host=ipaddress,
                                   user=user_db,
                                   passwd=password_db,
                                   db=db_name)
    c = conn.cursor()
    while True:
        choice = int(input("\n-------------------------\nklef log book\n-------------------------\n1.Create New Room\n2.Delete Room\n3.Show all Room\n4.Add new Id map\n5.Delete Id map\n6.Show Id number mapping\n7.Initialize database\n8.Exit\nplease choose an option:"))
        if choice > 0 and choice < 9:
            if choice == 1:
                room = input("Enter the Room number:")
                password = getpass("Enter the password:")
                confrimPwd = getpass("Enter the password again:")
                if(password==confrimPwd):
                    c.execute("SELECT count(*) FROM rooms where room='{}'".format(room))
                    if int(c.fetchall()[0][0]) < 1:
                        c.execute("INSERT INTO rooms(room,password) VALUES('{}','{}')".format(room,password))
                        print("Room successfully created")
                    else:
                        print("The Room number is already existed")
                else:
                    print("passwords not matched")
            elif choice == 2:
                room = input("Enter the Room number you want to delete(All data related to room is perminently lost):")
                c.execute("SELECT count(*) FROM rooms where room='{}'".format(room))
                if int(c.fetchall()[0][0]) > 0:
                    c.execute("DELETE FROM rooms where room='{}'".format(room))
                    print('Delete successfull')
                else:
                    print("Room number not existed")
            elif choice == 3:
                c.execute("SELECT room FROM rooms")
                print("----------------------\nRooms\n----------------------\n")
                for row in c.fetchall():
                    print(row[0])
            elif choice == 4:
                Idnumber = input("Enter Id number:")
                s = serial.Serial(com)
                rfid = s.readline()[1:11].decode()
                #rfid = "1234567891"
                c.execute("SELECT count(*) FROM rfid_map where id='{}' or rfid='{}'".format(Idnumber,rfid))
                if int(c.fetchall()[0][0]) < 1:
                    c.execute("INSERT INTO rfid_map(id,rfid) values('{}','{}')".format(Idnumber,rfid))
                    print(Idnumber," is successfully mapped with ",rfid)
                else:
                    print("Id number or Rfid already exists in database")
                s.close()
            elif choice == 5:
                Idnumber = input("Enter Id number to delete:")
                c.execute("SELECT count(*) FROM rfid_map where id='{}'".format(Idnumber))
                if(int(c.fetchall()[0][0])>0):
                    c.execute("DELETE FROM rfid_map where id='{}'".format(Idnumber))
                    print("Delete successfull")
                else:
                    print("Id number not exists")
            elif choice == 6:
                c.execute("SELECT * FROM rfid_map")
                print("----------------------\nId number mapping\n----------------------\n")
                for row in c.fetchall():
                    print(row[0],row[1])
            elif choice == 7:
                c.execute("CREATE TABLE rooms(id INT NOT NULL AUTO_INCREMENT,room VARCHAR(10) NOT NULL,\
                          password VARCHAR(20) NOT NULL,PRIMARY KEY (id),UNIQUE KEY (room))")
                c.execute("CREATE TABLE session_code(code VARCHAR(32) NOT NULL)")
                c.execute("CREATE TABLE rfid_map(id INT NOT NULL,rfid VARCHAR(30) NOT NULL, PRIMARY KEY (id),UNIQUE KEY (rfid))")
                c.execute("CREATE TABLE manual_logs(si INT NOT NULL AUTO_INCREMENT,user_id INT NOT NULL,room_id INT NOT NULL ,purpose VARCHAR(30),\
                          equipment_id VARCHAR(20),datecol DATE NOT NULL,in_time TIME NOT NULL,out_time TIME,PRIMARY KEY (si),\
                          FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE)")
                c.execute("CREATE TABLE rfid_logs(si INT NOT NULL AUTO_INCREMENT,user_id INT NOT NULL,room_id INT NOT NULL ,\
                          datecol DATE NOT NULL,in_time TIME NOT NULL,out_time TIME,PRIMARY KEY (si),\
                          FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE)")
                print("All required tables are successfully initialized")
            else:
                break
        else:
            print("please choose a valid option")
    conn.commit()
    c.close()
    conn.close()
except Exception as e:
    print(e)
