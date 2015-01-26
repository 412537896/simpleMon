#!/usr/bin/env python
# coding=utf-8
import json
import commands
from nbNet import *

def cmdRunner(input):
    cmd_ret = commands.getstatusoutput(input)
    return json.dumps({'ret':cmd_ret[0], 'out':cmd_ret[1]}, separators=(',', ':'))

HOST = '0.0.0.0'
PORT = 8899

server = nbNet(HOST, PORT, cmdRunner)
server.run()
