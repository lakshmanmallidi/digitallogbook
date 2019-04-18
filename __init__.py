from flask import Flask, render_template, redirect, request, url_for, session
from database import connection
import random
import string
import socket

app = Flask(__name__)
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(3)
serverIp = ("127.0.0.1",8999)

def getRfid(c):
    try:
        client.sendto(b"RfidNumber",serverIp)
        rfidNumber = client.recvfrom(10)[0].decode()
        c.execute("SELECT Id from rfidmapping where Rfid='{}'".format(rfidNumber))
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
            c.execute("SELECT '{}' FROM sessioncode".format(key))
            length = len(c.fetchall())
            if length > 0:
                if request.method == "POST":
                    oldpsw = request.form['oldpsw']
                    c.execute("SELECT password FROM rooms where room='{}'".format(session.get('room')))
                    origpsw = str(c.fetchall()[0][0])
                    if oldpsw == origpsw:
                        if request.form['newpsw'] == request.form['newpswconf']:
                            c.execute("UPDATE rooms SET password='{}' WHERE room='{}'".format(request.form['newpsw'], session.get('userid')))
                            msg = "Password successfully changed"
                            conn.commit()
                        else:
                            msg = "Password Not matched"
                        c.close()
                        conn.close()
                        return render_template("settings.html", msg=msg)
                    else:
                        msg = "Old Password incorrect"
                        conn.commit()
                        c.close()
                        conn.close()
                        return render_template("settings.html", msg=msg)
                else:
                    c.close()
                    conn.close()
                    return render_template("settings.html", msg="")
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
            c.execute("SELECT '{}' FROM sessioncode".format(key))
            length = len(c.fetchall())
            roomnumber = session.get('room')
            if length > 0:
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
                                heading = "Student Manual Log report of "+str(roomnumber)+" during "+str(fromdate)
                                c.execute("SELECT * FROM {} WHERE datecol>='{}'".format(roomnumber, fromdate))
                            elif request.form['recordstype'] == "rfid":
                                heading = "Student Rfid Log report of "+str(roomnumber)+" during "+str(fromdate)
                                c.execute("SELECT * FROM {} WHERE datecol>='{}'".format(roomnumber+"rfdata", fromdate))                                
                        else:
                            if request.form['recordstype'] == "manual":
                                heading = "Student Manual Log report of "+str(roomnumber)+" during "+str(fromdate)+" to "+str(todate)
                                c.execute("SELECT * FROM {} WHERE datecol>='{}' and datecol<='{}'".format(roomnumber, fromdate, todate))
                            elif request.form['recordstype'] == "rfid":
                                heading = "Student Rfid Log report of "+str(roomnumber)+" during "+str(fromdate)+" to "+str(todate)
                                c.execute("SELECT * FROM {} WHERE datecol>='{}' and datecol<='{}'".format(roomnumber+"rfdata", fromdate, todate))
                                
                    else:
                        sid = request.form['sid']
                        if request.form['recordstype'] == "manual":
                            heading = str(roomnumber)+" manual log report on student "+str(sid)
                            c.execute("SELECT * FROM {} WHERE userId={}".format(roomnumber, sid))
                        elif request.form['recordstype'] == "rfid":
                            heading = str(roomnumber)+" rfid log report on student "+str(sid)
                            c.execute("SELECT * FROM {} WHERE userId={}".format(roomnumber+"rfdata", sid))
                            
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
            c.execute("DELETE FROM sessioncode WHERE code='{}'".format(str(key)))
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
            c.execute("SELECT '{}' FROM sessioncode".format(key))
            length = len(c.fetchall())
            roomnumber = session.get('room')
            if length > 0:
                if request.method == "POST":
                    result = getRfid(c)
                    if(result!="NoConnection" and result!="Invalid"):
                        if request.form['type']=="GetId":
                            return render_template('rfidMain.html',IdNumber=result)
                        elif request.form['type']=="login":
                            c.execute("INSERT INTO {}(userId,datecol,intime) VALUES({},CURDATE(),CURTIME())".format(roomnumber+"rfdata",result))
                        elif request.form['type']=="logout":
                            c.execute("UPDATE {} SET outtime=CURTIME() WHERE userId={} order by si desc limit 1".format(roomnumber+"rfdata",result))
                        conn.commit()
                        c.close()
                        conn.close()
                        return render_template('rfidMain.html')
                    elif(result=="Invalid"):
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
            c.execute("SELECT '{}' FROM sessioncode".format(key))
            length = len(c.fetchall())
            roomnumber = session.get('room')
            if length > 0:
                if request.method == "POST":
                    if 'prps' in request.form:
                        sid = request.form['sid']
                        prps = request.form['prps']
                        eqid = request.form['eqid']
                        c.execute("INSERT INTO {}(userId,purpose,equipmentid,datecol,intime) VALUES({},'{}','{}',CURDATE(),CURTIME())".format(roomnumber,sid,prps,eqid))
                    else:
                        sid = request.form['sid']
                        c.execute("UPDATE {} SET outtime=CURTIME() WHERE userId={} order by si desc limit 1".format(roomnumber, sid))
                    conn.commit()
                    c.close()
                    conn.close()
                    return render_template('mainpage.html')
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
            sql = "SELECT password FROM rooms WHERE room='{}'".format(attempted_room)
            c.execute(sql)
            origpsw = c.fetchall()[0][0]
            if(str(origpsw) == attempted_password):
                randomkey = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
                session.permanent = True
                session['log_in'] = True
                session['room'] = attempted_room
                session['key'] = randomkey
                sql = "INSERT INTO sessioncode values('{}')".format(randomkey)
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
        elif(session.get("log_in")):
            key = session.get('key')
            c.execute("SELECT '{}' FROM sessioncode".format(key))
            length = len(c.fetchall())
            if length > 0:
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
