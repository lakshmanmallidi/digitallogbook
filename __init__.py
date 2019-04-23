from flask import Flask, render_template, redirect, request, url_for, session
from database import connection
import random
import string
import socket

app = Flask(__name__)
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(4)
serverIp = ("127.0.0.1",8999)

def getRfid(c):
    try:
        client.sendto(b"RfidNumber",serverIp)
        rfidNumber = client.recvfrom(10)[0].decode()
        c.execute("SELECT id from rfid_map where rfid='{}'".format(rfidNumber))
        rfidData=c.fetchall()
        if(len(rfidData)==1):
            return rfidData[0][0]
        else:
            return "Invalid"
    except Exception as e:
        print(e)
        return "NoConnection"

@app.errorhandler(500)
def servererror(e):
    return render_template("error500.html")


@app.errorhandler(404)
def pagenotfound(e):
    return render_template("error404.html")


@app.route("/settings.html", methods=["POST", "GET"])
def settingshandler():
    try:
        if session.get("log_in"):
            key = session.get('key')
            c, conn = connection()
            c.execute("SELECT count(*) FROM session_code where code='{}'".format(key))
            if int(c.fetchall()[0][0]) > 0:
                if request.method == "POST":
                    oldpsw = request.form['oldpsw']
                    c.execute("SELECT password FROM rooms WHERE id={}".format(session.get('room_id')))
                    origpsw = str(c.fetchall()[0][0])
                    if oldpsw == origpsw:
                        if request.form['newpsw'] == request.form['newpswconf']:
                            c.execute("UPDATE rooms SET password='{}' WHERE id={}".format(request.form['newpsw'], session.get('room_id')))
                            c.execute("DELETE FROM session_code WHERE code='{}'".format(key))
                            conn.commit()
                        else:
                            return render_template("settings.html", error="Password Not matched")
                        c.close()
                        conn.close()
                        return render_template("settings.html", msg="Password successfully changed")
                    else:
                        conn.commit()
                        c.close()
                        conn.close()
                        return render_template("settings.html", error="Old Password incorrect")
                else:
                    c.close()
                    conn.close()
                    return render_template("settings.html")
            else:
                c.close()
                conn.close()
                return redirect(url_for("loginhandler"))
        else:
            return redirect(url_for("loginhandler"))
    except Exception as e:
        print(e)
        return redirect(url_for("servererror"))


@app.route("/print.html",methods=["GET","POST"])
def printerhandler():
    try:
        if session.get("log_in"):
            key = session.get('key')
            c, conn = connection()
            c.execute("SELECT count(*) FROM session_code where code='{}'".format(key))
            if int(c.fetchall()[0][0]) > 0:
                roomId = session.get('room_id')
                c.execute("SELECT room FROM rooms WHERE id={}".format(roomId))
                roomNumber = c.fetchall()[0][0]
                if request.method =="POST":
                    if request.form['searchtype'] == "date":
                        fromdate = request.form['fromdate']
                        todate = request.form['todate']
                        dateformat = request.form['dateformat']
                        if dateformat=="2014-25-02":
                            toarr,fromarr = todate.split("-"), fromdate.split("-")
                            todate = "-".join(toarr[0],toarr[2],toarr[1])
                            fromdate = "-".join(fromarr[0],fromarr[2],fromarr[1])
                        elif dateformat=="2014/25/02":
                            toarr,fromarr = todate.split("/"), fromdate.split("/")
                            todate = "-".join(toarr[0],toarr[2],toarr[1])
                            fromdate = "-".join(fromarr[0],fromarr[2],fromarr[1])
                        elif dateformat=="2014/02/25":
                            toarr,fromarr = todate.split("/"), fromdate.split("/")
                            todate = "-".join(toarr[0],toarr[1],toarr[2])
                            fromdate = "-".join(fromarr[0],fromarr[1],fromarr[2])
                        if fromdate == todate:
                            if request.form['recordstype'] == "manual":
                                heading = "Student Manual Log report of "+str(roomNumber)+" during "+str(fromdate)
                                c.execute("SELECT * FROM manual_logs WHERE datecol>='{}' AND room_id={}".format(fromdate,roomId))
                            elif request.form['recordstype'] == "rfid":
                                heading = "Student Rfid Log report of "+str(roomNumber)+" during "+str(fromdate)
                                c.execute("SELECT * FROM rfid_logs WHERE datecol>='{}' AND room_id={}".format(fromdate,roomId))                                
                        else:
                            if request.form['recordstype'] == "manual":
                                heading = "Student Manual Log report of "+str(roomNumber)+" during "+str(fromdate)+" to "+str(todate)
                                c.execute("SELECT * FROM manual_logs WHERE datecol>='{}' AND datecol<='{}' AND room_id={}".format(fromdate, todate,roomId))
                            elif request.form['recordstype'] == "rfid":
                                heading = "Student Rfid Log report of "+str(roomNumber)+" during "+str(fromdate)+" to "+str(todate)
                                c.execute("SELECT * FROM rfid_logs WHERE datecol>='{}' AND datecol<='{}' AND room_id={}".format(fromdate,todate,roomId))
                                
                    else:
                        sId = request.form['sid']
                        if request.form['recordstype'] == "manual":
                            heading = str(roomNumber)+" manual log report on student "+str(sId)
                            c.execute("SELECT * FROM manual_logs WHERE user_id={} AND room_id={}".format(sId,roomId))
                        elif request.form['recordstype'] == "rfid":
                            heading = str(roomNumber)+" rfid log report on student "+str(sId)
                            c.execute("SELECT * FROM rfid_logs WHERE user_id={} AND room_id={}".format(sId,roomId))
                            
                    datarr = []
                    for rows in c.fetchall():
                        row = []
                        for ele in rows:
                            row.append(str(ele))
                        datarr.append(tuple(row))
                    c.close()
                    conn.close()
                    if request.form['recordstype'] == "manual":
                        return render_template("printdata.html", data=datarr, heading=heading)
                    elif request.form['recordstype'] == "rfid":
                        return render_template("rfprintdata.html", data=datarr, heading=heading)
                else:
                    c.close()
                    conn.close()
                    return render_template("print.html")
            else:
                c.close()
                conn.close()
                return redirect(url_for("loginhandler"))
        else:
            return redirect(url_for("loginhandler"))
    except Exception as e:
        print(e)
        return redirect(url_for("servererror"))


@app.route("/logout")
def logouthandler():
    try:
        if session.get('log_in'):
            key = session.get('key')
            c, conn = connection()
            c.execute("DELETE FROM session_code WHERE code='{}'".format(key))
            session.clear()
            conn.commit()
            c.close()
            conn.close()
            return redirect(url_for("loginhandler"))
        else:
            return redirect(url_for("loginhandler"))
    except Exception as e:
        print(e)
        return redirect(url_for("servererror"))

@app.route("/rfidMain.html", methods=['GET', 'POST'])
def RfidMainhandler():
    try:
        if session.get("log_in"):
            key = session.get('key')
            c, conn = connection()
            c.execute("SELECT count(*) FROM session_code where code='{}'".format(key))
            if int(c.fetchall()[0][0]) > 0:
                roomId = session.get('room_id')
                if request.method == "POST":
                    sId = getRfid(c)
                    if(sId!="NoConnection" and sId!="Invalid"):
                        if request.form['type']=="GetId":
                            return render_template('rfidMain.html',msg=sId)
                        elif request.form['type']=="login":
                            c.execute("INSERT INTO rfid_logs(user_id,room_id,datecol,in_time) VALUES({},{},CURDATE(),CURTIME())".format(sId,roomId))
                        elif request.form['type']=="logout":
                            c.execute("UPDATE rfid_logs SET out_time=CURTIME() WHERE user_id={} AND room_id={} ORDER BY si DESC LIMIT 1".format(sId,roomId))
                        conn.commit()
                        c.close()
                        conn.close()
                        if(request.form['type']=="login"):
                            return render_template('rfidMain.html',msg="Successfully logged in")
                        elif(request.form['type']=="logout"):
                            return render_template('rfidMain.html',msg="Successfully logged out")
                    elif(sId=="Invalid"):
                        c.close()
                        conn.close()
                        return render_template('rfidMain.html',error="Invalid Rf Card")
                    else:
                        c.close()
                        conn.close()
                        return render_template('rfidMain.html',error="RFID server not connected")
                else:
                    c.close()
                    conn.close()
                    return render_template('rfidMain.html')
            else:
                c.close()
                conn.close()
                return redirect(url_for("loginhandler"))
        else:
            return redirect(url_for("loginhandler"))
    except Exception as e:
        print(e)
        return redirect("servererror")

@app.route("/adminpage", methods=['GET', 'POST'])
def adminhandler():
    try:
        if session.get("log_in"):
            key = session.get('key')
            c, conn = connection()
            c.execute("SELECT count(*) FROM session_code where code='{}'".format(key))
            if int(c.fetchall()[0][0]) > 0:
                roomId = session.get('room_id')
                if request.method == "POST":
                    if 'prps' in request.form:
                        sId = request.form['sid']
                        prps = request.form['prps']
                        eqId = request.form['eqid']
                        sql = "INSERT INTO manual_logs(user_id,room_id,purpose,equipment_id,datecol,in_time) VALUES(%s,%s,%s,%s,CURDATE(),CURTIME())"
                        c.execute(sql,(sId,roomId,prps,eqId))
                    else:
                        sId = request.form['sid']
                        sql= "UPDATE manual_logs SET out_time=CURTIME() WHERE user_id=%s AND room_id=%s ORDER BY si DESC LIMIT 1"
                        c.execute(sql,(sId,roomId))
                    conn.commit()
                    c.close()
                    conn.close()
                    if 'prps' in request.form:
                        return render_template('mainpage.html',msg="Successfully logged in")
                    else:
                        return render_template('mainpage.html',msg="Successfully logged out")
                else:
                    c.close()
                    conn.close()
                    return render_template('mainpage.html')
            else:
                c.close()
                conn.close()
                return redirect(url_for("loginhandler"))
        else:
            return redirect(url_for("loginhandler"))
    except Exception as e:
        print(e)
        return redirect("servererror")


@app.route("/", methods=['GET', 'POST'])
def loginhandler():
    try:
        c, conn = connection()
        if request.method == 'POST':
            attempted_room = request.form['room']
            attempted_password = request.form['psw']
            c.execute("SELECT id,password FROM rooms WHERE room='{}'".format(attempted_room))
            roomData = c.fetchall()
            if(len(roomData)==1):
                origpsw = roomData[0][1]
                if(str(origpsw) == attempted_password):
                    randomkey = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
                    session.permanent = True
                    session['log_in'] = True
                    session['room_id'] = roomData[0][0] 
                    session['key'] = randomkey
                    sql = "INSERT INTO session_code(code) values('{}')".format(randomkey)
                    c.execute(sql)
                    conn.commit()
                    c.close()
                    conn.close()
                    return redirect(url_for("adminhandler"))
                else:
                    c.execute("SELECT room FROM rooms")
                    data = []
                    for row in c.fetchall():
                        data.append(row[0])
                    c.close()
                    conn.close()
                    return render_template("login.html", error="Username or password is incorrect", data=data)
            else:
                c.execute("SELECT room FROM rooms")
                data = []
                for row in c.fetchall():
                    data.append(row[0])
                c.close()
                conn.close()
                return render_template("login.html", error="No room selected", data=data)
        elif(session.get("log_in")):
            key = session.get('key')
            c.execute("SELECT count(*) FROM session_code where code='{}'".format(key))
            if int(c.fetchall()[0][0]) > 0:
                c.close()
                conn.close()
                return redirect(url_for("adminhandler"))
            else:
                c.execute("SELECT room FROM rooms")
                data = []
                for row in c.fetchall():
                    data.append(row[0])
                c.close()
                conn.close()
                return render_template("login.html", error="Please login again",data=data)
        else:
            c.execute("SELECT room FROM rooms")
            data = []
            for row in c.fetchall():
                data.append(row[0])
            c.close()
            conn.close()
            return render_template("login.html", error="", data=data)
    except Exception as e:
        print(e)
        return redirect(url_for("servererror"))


if __name__ == "__main__":
    app.config['SECRET_KEY'] = "Your_secret_string"
    app.run()
