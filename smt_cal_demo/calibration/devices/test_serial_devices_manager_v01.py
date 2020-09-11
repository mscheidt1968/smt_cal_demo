# -*- coding: utf-8 -*-
"""
Created on Wed Feb 06 11:47:34 2013

@author: Scheidt
"""

import numpy as np

import zmq
import simplejson
import datetime as dt
import smt_cal_demo.calibration.tokens.devices as c_dev

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://127.0.0.1:5001")
t1 = dt.datetime.now()

for k1 in range(1000): 
    data=dict(target = c_dev.fluke_8846A_01, cmd = "ping", data = "testload" )
    socket.send_json(data)
    answer = socket.recv_json()
    if answer["cmd"] != "ping":
        print(answer)

t2 = dt.datetime.now()
print((t2-t1))

data=dict(target = c_dev.fluke_8846A_01, cmd = "readln", data = "IDN?" )
socket.send_json(data)
answer = socket.recv_json()

print(answer)

data=dict(target = c_dev.fluke_8846A_01, cmd = "readln", data = "" )
socket.send_json(data)
answer = socket.recv_json()
print(answer)

data=dict(target = c_dev.fluke_8846A_01, cmd = "stop", data = "" )
socket.send_json(data)
# no answer will be sent