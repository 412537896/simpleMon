#!/usr/bin/env python

import socket, sys, os

PORT = 50000

def execRemote(HOST_L, cmd):
    output = ''
    for h in HOST_L:
        host = h.split(":")[0]
        try:
            port = h.split(":")[1]
        except:
            port = PORT
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.sendall("%010d%s"%(len(cmd), cmd))
        count = s.recv(10)
        print count
        if not count:
            sys.exit()
        count = int(count)
        while count > 0:
            buf = s.recv(count)
            print count
            count -= len(buf)
            output += buf
        s.close()
    return output
if __name__ == "__main__":

    HOST_L = sys.argv[1].split(",")
    cmd = sys.argv[2]
    import json
    print json.loads(execRemote(HOST_L, cmd))['out']
