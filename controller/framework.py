#!/usr/bin/python
import Queue
import threading
import time
import json
import commands
import socket
import MySQLdb as mysql
import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from nbNet.nbNet import *
from controller.client import *

db = mysql.connect(user="reboot", passwd="reboot123", \
        db="sys_song", charset="utf8")
db.autocommit(True)
c = db.cursor()

'''
CREATE TABLE `cmdresult` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `taskid` varchar(60) NOT NULL,
  `cmd`  varchar(200) NOT NULL,
  `hostname` varchar(32) NOT NULL,
  `rtime` int(15) NOT NULL,
  `retstat` int(10) NOT NULL,
  `out` LONGTEXT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=161 DEFAULT CHARSET=utf8;

'''

def controller(input):
    data = json.loads(input)
    print data
    if data["Operation"] == "sendCmd":
        #  {"Operation":"sendCmd","hostlist":request.form.getlist("client"), "cmd":request.form.get("cmd")} 

        out = execRemote(data['hostlist'], data['cmd'],data['taskid'])
        return out


    elif data["Operation"] == "receiveData":
        # {'Operation':'receiveData','cmd':input,'ret':os.WEXITSTATUS(cmd_ret[0]), 'out':cmd_ret[1],'hostname':socket.gethostname(),'rtime':int(time.time()),'taskid':'time.time()'}
        cmd = data['cmd']
        retstat = data['ret']
        out = data['out']
        rtime = data['rtime']
        hostname = data['hostname']
        taskid = data['taskid']
        try:
            sql = "INSERT INTO `cmdresult` (`taskid`,`cmd`,`hostname`,`rtime`,`retstat`,`out`) VALUES('%s', '%s', '%s', '%s', '%s', '%s');" % ( taskid,cmd,hostname,rtime,retstat,out)
            ret = c.execute(sql)
        
            return 'OK'
        except mysql.IntegrityError:
            return 'errer'
        except:
            return 'errer'
        
class execThread(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
    def run(self):
        server = nbNet(self.host, self.port, controller)
        server.run()

def startTh():
    execTh = execThread("0.0.0.0", 50005)
    execTh.start()

    print  "start"
    execTh.join()

if __name__ == "__main__":
    startTh()
