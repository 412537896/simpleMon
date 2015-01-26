#!/usr/bin/env python

import socket, sys, os

HOST = '0.0.0.0'
PORT = 8889

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

cmd = sys.argv[1]
while True:
    s.sendall("%010d%s"%(len(cmd), cmd))
    count = s.recv(10)
    if not count:
        sys.exit()
    count = int(count)
    buf = s.recv(count)
    print buf
