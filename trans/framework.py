#!/usr/bin/python
import Queue
import threading
import time
import json
import commands
import socket
import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from nbNet.nbNet import *

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("reboot", 50002))
sock_l = [s]

s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s1.connect(("reboot", 50003))
sock_a = [s1]

def transfer(input):
    global sock_l
    print "trans", input
    sendData(sock_l, "reboot", 50002, input)
    sendData(sock_a, "reboot", 50003, input)
    return "OK"

class execThread(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
    def run(self):
        server = nbNet(self.host, self.port, transfer)
        server.run()


def startTh():
    execTh = execThread("0.0.0.0", 50001)
    execTh.start()
    print  "start"
    execTh.join()

if __name__ == "__main__":
    startTh()
