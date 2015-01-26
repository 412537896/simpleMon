#!/usr/bin/env python
# coding=utf-8
import socket, os, sys, select
import json
import profile
import copy

def cmdRunner(input):
    import commands
    cmd_ret = commands.getstatusoutput(input)
    return json.dumps({'ret':cmd_ret[0], 'out':cmd_ret[1]}, separators=(',', ':'))

__all__ = ['nbNet', 'sendData']

class _State:
    def __init__(self):
        self.state = "read"
        self.have_read = 0
        self.need_read = 10
        self.have_write = 0
        self.need_write = 0
        self.data = ""

class nbNet:

    def __init__(self, host, port, logic):
        self.host = host
        self.port = port
        self.logic = logic
        self.sm = {
            "read":self.aread,
            "write":self.awrite,
            "process":self.aprocess,
            "closing":self.aclose,
        }


    def run(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.host, self.port))
        self.s.setblocking(0)
        self.s.listen(10)
        self.R_LIST = [self.s]
        self.W_LIST = []
        # listen: accept -> read -> process -> write -> closing
        # accpet: read -> process -> write -> closing
        self.STATE = {}
        self.COUNTER = 0
        while True:
            r_socks, w_socks, err_socks = select.select(self.R_LIST, self.W_LIST, [])
            for sock in r_socks:
                self.state_machine(sock)
            for sock in w_socks:
                self.state_machine(sock)

    def aread(self, sock):
        #TODO 异常处理
        try:
            one_read = sock.recv(self.STATE[sock].need_read)
            if len(one_read) == 0:
                self.STATE[sock].state = "closing"
                self.state_machine(sock)
                return
            self.STATE[sock].data += one_read
            self.STATE[sock].have_read += len(one_read)
            self.STATE[sock].need_read -= len(one_read)
            if self.STATE[sock].have_read == 10:
                self.STATE[sock].need_read += int(self.STATE[sock].data)
                self.STATE[sock].data = ''
            elif self.STATE[sock].need_read == 0:
                self.R_LIST.remove(sock)
                self.STATE[sock].state = 'process'
                #print self.STATE[sock]
                self.state_machine(sock)
        except:
            self.STATE[sock].state = "closing"
            self.state_machine(sock)
            return

    def aclose(self, sock):
        self.STATE.pop(sock)
        try:
            self.R_LIST.remove(sock)
        except:
            pass
        try:
            self.W_LIST.remove(sock)
        except:
            pass
        sock.close()

    def aprocess(self, sock):
        #print self.STATE[sock].data
        response = self.logic(self.STATE[sock].data)
        self.STATE[sock].data = "%010d%s"%(len(response), response)
        self.STATE[sock].need_write = len(self.STATE[sock].data)
        self.STATE[sock].state = 'write'
        self.W_LIST.append(sock)
        self.COUNTER += 1
        if self.COUNTER % 1000 == 0:
            print self.COUNTER

    def awrite(self, sock):
        try:
            last_have_send = self.STATE[sock].have_write
            have_send = sock.send(self.STATE[sock].data[last_have_send:])
            self.STATE[sock].have_write += have_send
            self.STATE[sock].need_write -= have_send
            if self.STATE[sock].need_write == 0 and self.STATE[sock].have_write != 0:
                #self.STATE[sock].state = 'closing'
                self.STATE[sock] = _State()
                self.R_LIST.append(sock)
                self.W_LIST.remove(sock)
        except:
            self.STATE[sock].state = "closing"
            self.state_machine(sock)
            return

    def state_machine(self, sock):
        if sock == self.s: 
            # 监听socket
            conn, addr = self.s.accept()
            conn.setblocking(0)
            self.STATE[conn] = _State()
            self.R_LIST.append(conn)
        else:
            # 已经accept的socket
            #print self.STATE
            stat = self.STATE[sock].state
            self.sm[stat](sock)

def sendData(sock_l, host, port, data):
    retry = 0
    while retry < 3:
        try:
            if sock_l[0] == None:
                sock_l[0] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock_l[0].connect((host, port))
                print "connecting"
            d = data
            sock_l[0].sendall("%010d%s"%(len(d), d))
            print "%010d%s"%(len(d), d)
            count = sock_l[0].recv(10)
            if not count:
                raise Exception("recv error", "recv error")
            count = int(count)
            buf = sock_l[0].recv(count)
            print buf
            if buf[:2] == "OK":
                retry = 0
                break
        except:
            sock_l[0].close()
            sock_l[0] = None
            retry += 1


if __name__ == "__main__":
    HOST = '0.0.0.0'
    PORT = 50005
    nb = nbNet(HOST, PORT, cmdRunner)
    nb.run()

#profile.run("run()", "prof.txt")
#import pstats
#p = pstats.Stats("prof.txt")
#p.sort_stats("time").print_stats()
