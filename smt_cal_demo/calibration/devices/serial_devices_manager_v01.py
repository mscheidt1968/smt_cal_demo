# -*- coding: utf-8 -*-
"""
Created on Wed Feb 06 09:29:31 2013

@author: Scheidt
"""

import numpy as np

import os
import datetime as dt
import time
import threading
import winreg
import zmq
import serial

import smt_cal_demo.calibration.tokens.devices as c_dev

com_ports = dict()
com_ports[c_dev.fluke_5500E_01] = "COM7"

known_ports = dict()
portmap = dict()


def scan_ports():
        
    print("Scanning ports for expected devices")
    port = None

    # search fluke 5500
    try:
        port = com_ports[c_dev.fluke_5500E_01]
    except:
        port = None

    if not port is None:            
        print(("Searching for Fluke5500 on port {:s}".format(port)))
        try: 
            ser = serial.Serial(port,9600,
                                parity=serial.PARITY_ODD,
                                bytesize =serial.SEVENBITS,
                                timeout = 0.5)
            ser.write("\n*IDN?\n".encode("latin_1"))
            answer = ser.readline()
            answer = answer.rstrip().decode("latin_1")
            print(answer)
            if answer.find("FLUKE,5500") != -1:
                # system could be identified
                print("Fluke5500 found")
                portmap[c_dev.fluke_5500E_01] = dict(ser_if=ser,idn=answer.rstrip().split(","))
                known_ports[port] = c_dev.fluke_5500E_01
            else:
                ser.close()
                print("Fluke5500 not found")
        except Exception as exc:
            print(("Port {:s} not available, Fluke5500 not found, Error:".format(port)),exc)
            pass


scan_ports()
if c_dev.fluke_5500E_01 not in portmap:
    raise Exception("Fluke 5500 not on {:s}".format(com_ports[c_dev.fluke_5500E_01]))

stop = False
tstart = dt.datetime.now()

def readln(ser, writelnFirst="", simresult=""):
    if writelnFirst != "":
        writeln(ser, writelnFirst)
    if hasattr(ser,"eol"):
        answer = bytes()
        end = False
        while not end:
            zw = ser.read()
            if zw == b"\r" or zw ==b"":
                end = True
            answer += zw
        answer = answer.decode("latin-1")
    else:
         answer =  (ser.readline().rstrip()).decode("latin-1")
    return answer

def readbinary(ser, byte_count=1, simresult=""):
    answer = (ser.read(byte_count)).decode("latin-1")
    return answer
    
def write(ser,data):
    ser.write(data.encode("latin-1"))

def writeln(ser, data):
    if hasattr(ser,"eol"):
        ser.write(data.encode("latin-1") + ser.eol)
    else:
        ser.write((data+"\n").encode("latin-1"))


# the server understands json datapackage with following structure
# target = device names as in tokens.devices
# cmd = write, read, readln, readbinary
# optional:
# data = datas which should be send by cmd in advance
# byte_count = number of bytes which should be read

context = zmq.Context()
stop = False

def worker_routine(worker_url, id_number):
    """Worker routine"""
    global context
    global stop 
    # Socket to talk to dispatcher
    socket = context.socket(zmq.REP)

    socket.connect(worker_url)

    while not stop:
        try:
            msg = socket.recv_json()
        except:
            stop = True
        
        if not stop:
            print(("Worker {:f} working".format(id_number)))
            try:
                if "target" in msg:
                    ser_if = portmap[msg["target"]]["ser_if"]
                    print(("Worker {:f} working on {:s} with command: {:s}".format(id_number,msg["target"],msg["cmd"])))
                else:
                    ser_if = None
                
                if msg["cmd"] == "write":
                    write(ser_if,msg["data"])
                    socket.send_json(dict(cmd = "ok"))
                elif msg["cmd"] == "writeln":
                    writeln(ser_if,msg["data"])
                    socket.send_json(dict(cmd = "ok"))
                elif msg["cmd"] == "readln":
                    answer = readln(ser_if,msg["data"])
                    socket.send_json(dict(cmd = "ok",data = answer))
                elif msg["cmd"] == "readbinary":
                    answer = readbinary(ser_if,msg["byte_count"])
                    socket.send_json(dict(cmd = "ok",data = answer))
                elif msg["cmd"] == "ping":
                    answer = dt.datetime.now().isoformat()
                    socket.send_json(dict(cmd = "ping",data = answer))
                elif msg["cmd"] == "scan":
                    scan_ports()
                    socket.send_json(dict(cmd = "ok",data = portmap))
                elif msg["cmd"] == "stop":
                    stop = True
            except Exception as exc:
                print(exc)
                socket.send_json(dict(cmd = "error", data = exc.args[0]))

    socket.close()            


url_worker = "inproc://workers"
url_client = "tcp://127.0.0.1:5001"

# Socket to talk to clients
clients = context.socket(zmq.ROUTER)
clients.bind(url_client)

# Socket to talk to workers
workers = context.socket(zmq.DEALER)
workers.bind(url_worker)

# Launch pool of worker threads
for i in range(5):
    thread = threading.Thread(target=worker_routine, args=(url_worker,i,))
    thread.start()

def zmq_service():      
    """Server routine"""
    print("zmq_service started")
    try:
        zmq.device(zmq.QUEUE, clients, workers)
    except:
        pass

    clients.close()
    workers.close()
    print("zmq_service ended")

def stop_zmq_service():
    context.term()

def main():
    zmq_thread = threading.Thread(target=zmq_service)
    zmq_thread.start()
    print("Caution, runs in background until the process is terminated!")

if __name__ == "__main__":
    main()
