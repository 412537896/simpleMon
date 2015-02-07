#!/usr/bin/env python

import socket, sys, os, time, json

PORT = 50000

def execRemote(HOST_L, cmd ,taskid):
    failure = []
    for h in HOST_L:
        output = ''
        host = h.split(":")[0]
        try:
            port = h.split(":")[1]
        except:
            port = PORT
        execCmd = json.dumps({'Operation':'execcmd','cmd':cmd,'taskid':taskid,'host':host})

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            s.sendall("%010d%s"%(len(execCmd), execCmd))
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
            if output != 'ok':
                failure.append(host)
        except:
            failure.append(host)
        
    if failure == []:
        return 'Task: %s failure: %s'%(taskid,str(failure))
    else:
        return 'Task: %s'%(taskid)
if __name__ == "__main__":

    HOST_L = sys.argv[1].split(",")
    cmd = sys.argv[2]
    print execRemote(HOST_L, cmd)
