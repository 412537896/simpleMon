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

def controller(input):
    # flask_web 发input过来
    #input 应该是{"hostlist":['reboot1', 'reboot2'], "cmd":"ps aux"}
    # 新开一个进程
    #    调用client.py里面的execRemote
    #    把execRemote 的返回值写入数据库
    # 主进程返回OK
    return "OK"

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
