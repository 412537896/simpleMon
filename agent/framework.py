#!/usr/bin/python
import Queue
import threading
import time
import json
import urllib2
import socket
import commands
from moniItems import mon

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from nbNet.nbNet import *

class porterThread (threading.Thread):
    def __init__(self, name, q, ql, interval=None,host=None,port=None):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q
        self.queueLock = ql
        self.interval = interval
        self.host = host
        self.port = port

    def run(self):
        #print "Starting %s"  % self.name
        if self.name == 'collect':
            self.put_data()
        elif self.name == 'sendjson':
            self.get_data()
        elif self.name == 'receiveCmd':
            self.receiveCmd()
        elif self.name == 'sendCmdResults':
            self.sendCmdResults()

    def put_data(self):
        m = mon()
        atime=int(time.time())
        while 1:
            data = m.runAllGet()
            #print data 
            self.queueLock.acquire()
            self.q.put(data)
            self.queueLock.release()
            btime=int(time.time())
            #print '%s  %s' % (str(data), self.interval-((btime-atime)%30))
            time.sleep(self.interval-((btime-atime)%self.interval))
            
    def get_data(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock_l = [s]
            s.connect((self.host, self.port))
        except:
            pass
        while 1:
            print "get"
            self.queueLock.acquire()
            if not self.q.empty():
                data = self.q.get()
                print data
                sendData(sock_l, self.host, self.port, json.dumps(data))
            self.queueLock.release()
            time.sleep(self.interval)
            
    def receiveCmd(self):
        server = nbNet(self.host, self.port, self.cmdQueue)
        server.run()
        
    def cmdQueue(self,input):
        self.queueLock.acquire()
        self.q.put(input)
        self.queueLock.release()
        return 'ok'

    def sendCmdResults(self):
        while 1:
            print "get cmd"
            self.queueLock.acquire()
            if not self.q.empty():
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock_l = [s]
                    s.connect((self.host, self.port))
                except:
                    s.close()
                data = json.loads(self.q.get()) 
                print data
                cmd_ret = commands.getstatusoutput(data['cmd'])
                sendData(sock_l, self.host, self.port, json.dumps({'Operation':'receiveData','cmd':data['cmd'],'taskid':data['taskid'],'ret':os.WEXITSTATUS(cmd_ret[0]), 'out':cmd_ret[1],'hostname':data['host'],'rtime':int(time.time())}, separators=(',', ':')) )
            self.queueLock.release()
            time.sleep(self.interval)


def startTh():
    q1 = Queue.Queue(10)
    ql1 = threading.Lock()
    collect = porterThread('collect', q1, ql1, interval=30)
    collect.start()
    time.sleep(0.5)
    sendjson = porterThread('sendjson', q1, ql1, interval=3, host="0.0.0.0", port=50001)
    sendjson.start()
    q2 = Queue.Queue(10)
    ql2 = threading.Lock()
    execTh = porterThread('receiveCmd',q2,ql2,host="0.0.0.0", port=50000)
    execTh.start()
    execSendTh = porterThread('sendCmdResults',q2,ql2,host="0.0.0.0", port=50005, interval=2)
    execSendTh.start()

    print  "start"
    collect.join()
    sendjson.join()
    execTh.join()
    execSendTh.join()
if __name__ == "__main__":
    startTh()


