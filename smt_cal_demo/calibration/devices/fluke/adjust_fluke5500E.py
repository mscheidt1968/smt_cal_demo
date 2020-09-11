# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 08:55:00 2016

@author: Scheidt
"""

import smt_cal_demo.utilities.easygui as eg
import logging
import smt_cal_demo.calibration.devices.support as n_support
import smt_cal_demo.calibration.tokens.devices as c_dev
import smt_cal_demo.calibration.devices.agilent.hp3458a_v02 as n_mul

c_number_of_lines_consts_report = 482
c_number_of_lines_stored_report = 155

    
conn = n_support.SerialDeviceConnection()
conn.target = c_dev.fluke_5500E_01


hp = n_mul.device()
hp.connect()

R1k = 1.0003899e3
R100 = 99.99723
R10 = 9.99977
R10AC = 9.99981
R1 = 999.901e-3
R01 = 99.9836e-3
R10Meg = 10.000266e6

def abort():
    conn.writeln("cal_abort")
    
def process_errors():
    first_line = True
    any_error = False
    fertig = False
    while not fertig:
        zw = conn.readln("Err?")
        if zw == '0,"No Error"':
            fertig = True
        else:
            if first_line:
                print("Former Errors:")
                first_line = False
                any_error = True
            print(zw)
    
    if any_error:
        print("End former Errors")

def get_active_report():
    zw = ""
    conn.writeln("RPT? Active,SPREAD,I90D")
    for k1 in range(c_number_of_lines_stored_report):
        zw += (conn.readln())

    return zw    

while conn.readln() != "":
    pass

process_errors()

conn.writeln("*IDN?")  
idn = conn.readln()
print(idn)
if idn != "FLUKE,5500E,1924010,1.0+1.3+2.0+*":
    raise Exception("Can't contact device")
    
# get latest report
conn.writeln("RPT? Active,SPREAD,I90D")
for k1 in range(c_number_of_lines_stored_report+10):
    zw = (conn.readln())
    print(k1, zw)
    
print(conn.readln())

if eg.ynbox("DC Calibration?"):
    process_errors()
    print(conn.readln("CAL_STEP?"))
    conn.writeln("CAL_START MAIN")
    ans = conn.readln("CAL_STEP?")
    if ans != "MAINI":
        raise Exception("Cal Step wrong. Expected MAINI receive " + ans)
    ans = conn.readln("Cal_info?")
    print(ans)
    if ans != "":
        raise Exception("Cal info wrong. Received " + ans)


conn.writeln("RPT? Consts,Spread,I90D")
for k1 in range(c_number_of_lines_consts_report):
    zw = (conn.readln())
    print(k1, zw)