#!/usr/bin/env python
import zerorpc
import os,sys

def rpc_call(host, cmd):
    c = zerorpc.Client()
    c.connect("tcp://%s"%(host))
    get_str = c.hello(cmd)
    print get_str

rpc_call('reboot:4242', sys.argv[1])
