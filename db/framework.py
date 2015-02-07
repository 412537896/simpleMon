#!/usr/bin/python
import Queue
import threading
import time
import json
import commands
import sys, os
import MySQLdb as mysql
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from nbNet.nbNet import *

db = mysql.connect(user="reboot", passwd="reboot123", \
        db="sys_song", charset="utf8")
db.autocommit(True)
c = db.cursor()

def cmdRunner(input):
    #{"MemTotal": 15888, "MemUsage": 396, "MemFree": 15491, "Host": "teach.works", "LoadAvg": 0.16, "Time": 1416129351}
    data = json.loads(input)
    hostname = data["Host"]
    load = data["LoadAvg"]
    time = data["Time"]
    memtotal = data["MemTotal"]
    memusage = data["MemUsage"]
    memfree = data["MemFree"]

    print hostname,load,time,memtotal,memusage,memfree

    try:
        sql = "INSERT INTO `statusinfo` (`hostname`,`load`,`time`,`memtotal`,`memusage`,`memfree`) VALUES('%s', %s, %s, %s, %s, %s);" % (hostname, load,time,memtotal,memusage,memfree)
        ret = c.execute(sql)
        return 'OK'
    except mysql.IntegrityError:
        return 'errer'

class execThread(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
    def run(self):
        server = nbNet(self.host, self.port, cmdRunner)
        server.run()


def startTh():
    execTh = execThread("0.0.0.0", 50013)
    execTh.start()
    print  "start"
    execTh.join()

if __name__ == "__main__":
    startTh()
