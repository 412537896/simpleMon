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
num = 0
def cmdRunner(input):
    
    return str(num += 1)

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
