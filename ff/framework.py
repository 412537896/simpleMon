#!/usr/bin/python
import Queue
import threading
import time
import json
import commands
import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from nbNet.nbNet import *

ff_conf = []

def cmdRunner(input):
    print input
    global ff_conf
    if input == "reload":
        with file("ff.conf") as f:
            ff_conf = json.loads(f.read())
    else:
        if not ff_conf:
            with file("ff.conf") as f:
                d = f.read()
                print d
                ff_conf = json.loads(d)
        #{"MemTotal": 15888, "MemUsage": 396, "MemFree": 15491, "Host": "teach.works", "LoadAvg": 0.16, "Time": 1416129351}
        mon_data = json.loads(input)
        for m in ff_conf:
            val = mon_data.get(m[0], None)
            if val != None:
                alert_flag = eval(str(val) + m[1] + str(m[2]))
                if alert_flag:
                    print str(val) + m[1] + str(m[2])

    return "OK"

class execThread(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
    def run(self):
        server = nbNet(self.host, self.port, cmdRunner)
        server.run()


def startTh():
    execTh = execThread("0.0.0.0", 50002)
    execTh.start()
    print  "start"
    execTh.join()

if __name__ == "__main__":
    startTh()
