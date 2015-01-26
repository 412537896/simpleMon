#!/usr/bin/env python
import json
import time
import MySQLdb as mysql
from flask import Flask, request
import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from controller.client import *

app = Flask(__name__)
db = mysql.connect(user="reboot", passwd="reboot123", \
        db="sys_song", charset="utf8")
db.autocommit(True)
c = db.cursor()

"""
CREATE TABLE `statusinfo` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `hostname` varchar(32) NOT NULL,
  `load` float(10) NOT NULL DEFAULT 0.00,
  `time` int(15) NOT NULL,
  `memtotal` int(15) NOT NULL,
  `memusage` int(15) NOT NULL,
  `memfree` int(15) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=161 DEFAULT CHARSET=utf8;
"""

#@app.route("/collect", methods=["GET", "POST"])
#def collect():
#    sql = ""
#    if request.method == "POST":
#        data = request.json
#        hostname = data["Host"]
#        load = data["LoadAvg"]
#        time = data["Time"]
#        memtotal = data["MemTotal"]
#        memusage = data["MemUsage"]
#        memfree = data["MemFree"]

#        print hostname,load,time,memtotal,memusage,memfree

#        try:
#            sql = "INSERT INTO `statusinfo` (`hostname`,`load`,`time`,`memtotal`,`memusage`,`memfree`) VALUES('%s', %s, %s, %s, %s, %s);" % (hostname, load,time,memtotal,memusage,memfree)
#            ret = c.execute(sql)
#            return 'ok'
#        except mysql.IntegrityError:
#            return 'errer'

@app.route("/load", methods=["GET", "POST"]) 
def load():
    try:  
        #hostname = request.form.get("hostname")
        atime = int(time.time() - 86400)
        sql = "SELECT `time`,`load` FROM `statusinfo` WHERE hostname = '%s' and time > '%d' ;" % ('teach.works',atime)
        c.execute(sql)
        ones = c.fetchall() 
        new_list = []
        for i in ones:
            new_list.append([ i[0] * 1000 + 28800000 ,i[1] ])
        print json.dumps(new_list)
        return json.dumps(new_list)

    except:
        return 'hostname null'
	
@app.route("/mem", methods=["GET", "POST"])
def mem():
    try:
        #hostname = request.form.get("hostname")
        atime = int(time.time() - 86400)
        sql = "SELECT `time`,`memfree`,`memusage` FROM `statusinfo` WHERE hostname = '%s' and time > '%d' ;" % ('teach.works',atime)
        c.execute(sql)
        ones = c.fetchall()
        mem_free_list = []
        mem_usage_list = []
        for i in ones:
            mem_free_list.append([ i[0] * 1000 + 28800000 ,i[1] ])
            mem_usage_list.append([ i[0] * 1000 + 28800000 ,i[2] ])
        print json.dumps([mem_free_list,mem_usage_list])
        return json.dumps([mem_free_list,mem_usage_list])

    except:
        return 'hostname null'

@app.route("/show", methods=["GET", "POST"])
def show():
    try:
        hostname = request.form.get("hostname")
        sql = "SELECT `load` FROM `statusinfo` WHERE hostname = '%s';" % ('teach.works')
        c.execute(sql)
        ones = c.fetchall()

        print ones
        return render_template("sysstatus.html", data=ones, sql = sql)
    except:
        print 'hostname null'
@app.route("/list", methods=["GET", "POST"])
def list():
    page = request.args.get('page', 1)
    print page
    print type(page)
    if page == '1':
        ones = '1.json'
    elif page == '2':
        ones = '2.json'
    return render_template("list.html", data1=ones)

@app.route("/ctl", methods=["GET", "POST"])
def ctl():
    if request.method == "POST":
        out = execRemote(request.form.getlist("client"), request.form.get("cmd"))        
        return render_template("control.html", output=out)
    else:
        return render_template("control.html", output="")


from flask import render_template
@app.route("/xxx/<name>")
def hello_xx(name):
    return render_template("sysstatus.html", name='teach')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=50004, debug=True)


