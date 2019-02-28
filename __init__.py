from flask import Flask, render_template, redirect, request, url_for, session
from database import connection
import random
import string


app = Flask(__name__)


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
                            c.close()
                            conn.close()
                            return render_template("settings.html", msg=msg)
                        else:
                            msg = "Password Not matched"
                            conn.commit()
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
        print e
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
                            c.execute("SELECT * FROM {} WHERE datecol>='{}'".format(roomnumber, fromdate))
                            datarr = []
                            for rows in c.fetchall():
                                row = []
                                for ele in rows:
                                    row.append(str(ele))
                                datarr.append(tuple(row))
                            c.close()
                            conn.close()
                            heading = "Student Log report of "+str(roomnumber)+" during "+str(fromdate)
                            return render_template("printdata.html", data=datarr, heading=heading)
                        else:
                            c.execute("SELECT * FROM {} WHERE datecol>='{}' and datecol<='{}'".format(roomnumber, fromdate, todate))
                            datarr = []
                            for rows in c.fetchall():
                                row = []
                                for ele in rows:
                                    row.append(str(ele))
                                datarr.append(tuple(row))
                            c.close()
                            conn.close()
                            heading = "Student Log report of "+str(roomnumber)+" during "+str(fromdate)+" to "+str(todate)
                            return render_template("printdata.html", data=datarr, heading=heading)
                    else:
                        sid = request.form['sid']
                        c.execute("SELECT * FROM {} WHERE userId={}".format(roomnumber, sid))
                        datarr = []
                        for rows in c.fetchall():
                            row = []
                            for ele in rows:
                                row.append(str(ele))
                            datarr.append(tuple(row))
                        c.close()
                        conn.close()
                        heading = str(roomnumber)+" log report on student "+str(sid)
                        return render_template("printdata.html", data=datarr,heading=heading)
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
        print e
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
        print e
        return redirect(url_for("servererror"))


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
                        conn.commit()
                        c.close()
                        conn.close()
                        return render_template('mainpage.html')
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
        print e
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
                randomkey = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])
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
        print e
        return redirect(url_for("servererror"))


if __name__ == "__main__":
    app.config['SECRET_KEY'] = "Your_secret_string"
    app.run("192.168.43.104",port="80")
