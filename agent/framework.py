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
    def __init__(self, name, q, ql, interval,):
        threading.Thread.__init__(self)
        self.name = name
        self.interval = interval
        self.queueLock = ql
        self.q = q

    def run(self):
        #print "Starting %s"  % self.name
        if self.name == 'collect':
            self.put_data()
        elif self.name == 'sendjson':
            self.get_data()

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
            s.connect(("reboot", 50001))
        except:
            pass
        while 1:
            print "get"
            self.queueLock.acquire()
            if not self.q.empty():
                data = self.q.get()
                print data
                sendData(sock_l, "reboot", 50001, json.dumps(data))
            self.queueLock.release()
            time.sleep(self.interval)

def cmdRunner(input):
    print input
    cmd_ret = commands.getstatusoutput(input)
    return json.dumps({'ret':os.WEXITSTATUS(cmd_ret[0]), 'out':cmd_ret[1]}, separators=(',', ':'))

class execThread(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
    def run(self):
        server = nbNet(self.host, self.port, cmdRunner)
        server.run()


def startTh():
    q = Queue.Queue(10)
    ql = threading.Lock()
    collect = porterThread('collect', q, ql, 30, )
    collect.start()
    time.sleep(0.5)
    sendjson = porterThread('sendjson', q, ql, 3,)
    sendjson.start()
    execTh = execThread("0.0.0.0", 50000)
    execTh.start()

    print  "start"
    collect.join()
    sendjson.join()
    execTh.join()
if __name__ == "__main__":
    startTh()
