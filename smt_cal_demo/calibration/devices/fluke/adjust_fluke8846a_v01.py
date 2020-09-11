# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 13:15:56 2012

@author: Scheidt
"""

import unittest
import numpy as np
import time
import smt_cal_demo.calibration.tokens.devices as c_dev
import smt_cal_demo.calibration.tokens.electrical_properties as c_el
import smt_cal_demo.calibration.tokens.device_functions as c_fct
import smt_cal_demo.calibration.tokens.physical_units as c_phy
import smt_cal_demo.calibration.devices.support as n_support
from smt_cal_demo.calibration.models.support_v01 import Var
import smt_cal_demo.utilities.easygui as eg
import smt_cal_demo.calibration.devices.agilent.hp3458a_v02 as n_mul
import smt_cal_demo.calibration.devices.fluke.fluke5500e_v01 as n_cal





class device(object):
    """Interaction object with 8846 multimeter connected via RS232"""

    def __init__(self):
        self.conn = None
        self.active_settings = None
        self.simulation = False
        self.serial_number = ""

    def cal_lock_unlock(self, password="FLUKE884X", lock=True):
        if lock:
            self.conn.writeln("CAL:SEC:STAT ON, {:s}".format(password))
        else:
            self.conn.writeln("CAL:SEC:STAT OFF, {:s}".format(password))
 
    def cal_shorts(self):
        eg.msgbox("Apply 4W short to front and back port")
        self.conn.writeln("Cal:Step 3")
        self.conn.writeln("Cal? OFF")
        fertig = False
        while not fertig:
            ans = self.conn.readln()
            if ans != "":
                fertig = True
        
        if ans != "+0":
            raise Exception("Calibration was not successfull ans:{:s}".
                format(ans))
        else:
            print("ACV zero finished")

        self.conn.writeln("Cal:Step 13")
        self.conn.writeln("Cal? OFF")
        fertig = False
        while not fertig:
            ans = self.conn.readln()
            if ans != "":
                fertig = True
        
        if ans != "+0":
            raise Exception("Calibration was not successfull ans:{:s}".
                format(ans))
        else:
            print("ZVDC finished")


        self.conn.writeln("Cal:Step 18")
        self.conn.writeln("Cal? OFF")
        fertig = False
        while not fertig:
            ans = self.conn.readln()
            if ans != "":
                fertig = True
        
        if ans != "+0":
            raise Exception("Calibration was not successfull ans:{:s}".
                format(ans))
        else:
            print("DFVDC finished")


        self.conn.writeln("Cal:Step 22")
        self.conn.writeln("Cal? OFF")
        fertig = False
        while not fertig:
            ans = self.conn.readln()
            if ans != "":
                fertig = True
        
        if ans != "+0":
            raise Exception("Calibration was not successfull ans:{:s}".
                format(ans))
        else:
            print("Ohm zero finished")

        self.conn.writeln("Cal:Step 29")
        self.conn.writeln("Cal? OFF")
        fertig = False
        while not fertig:
            ans = self.conn.readln()
            if ans != "":
                fertig = True
        
        if ans != "+0":
            raise Exception("Calibration was not successfull ans:{:s}".
                format(ans))
        else:
            print("Ratio short finished")
            
        eg.msgbox("Switch to rear port")

        self.conn.writeln("Cal:Step 32")
        self.conn.writeln("Cal? OFF")
        fertig = False
        while not fertig:
            ans = self.conn.readln()
            if ans != "":
                fertig = True
        
        if ans != "+0":
            raise Exception("Calibration was not successfull ans:{:s}".
                format(ans))
        else:
            print("Rear Ohm zero finished")


        self.conn.writeln("Cal:Step 37")
        self.conn.writeln("Cal? OFF")
        fertig = False
        while not fertig:
            ans = self.conn.readln()
            if ans != "":
                fertig = True
        
        if ans != "+0":
            raise Exception("Calibration was not successfull ans:{:s}".
                format(ans))
        else:
            print("Rear DCV zero finished")

        self.conn.writeln("Cal:Step 39")
        self.conn.writeln("Cal? OFF")
        fertig = False
        while not fertig:
            ans = self.conn.readln()
            if ans != "":
                fertig = True
        
        if ans != "+0":
            raise Exception("Calibration was not successfull ans:{:s}".
                format(ans))
        else:
            print("Rear Ratio short finished")

    def cal_current_shorts(self):
        eg.msgbox("Switch to front port. Short 400mA to LO")
        self.conn.writeln("Cal:Step 41")
        self.conn.writeln("Cal? OFF")
        fertig = False
        while not fertig:
            ans = self.conn.readln()
            if ans != "":
                fertig = True
        
        if ans != "+0":
            raise Exception("Calibration was not successfull ans:{:s}".
                format(ans))
        else:
            print("Low I zero finished")

        eg.msgbox("Short 10A to LO")
        self.conn.writeln("Cal:Step 56")
        self.conn.writeln("Cal? OFF")
        fertig = False
        while not fertig:
            ans = self.conn.readln()
            if ans != "":
                fertig = True
        
        if ans != "+0":
            raise Exception("Calibration was not successfull ans:{:s}".
                format(ans))
        else:
            print("Hi I zero finished")

   
    def cal_open(self):
        eg.msgbox("Leave ports open")
        self.conn.writeln("Cal:Step 0")
        self.conn.writeln("Cal? OFF")
        fertig = False
        while not fertig:
            ans = self.conn.readln()
            if ans != "":
                fertig = True
        
        if ans != "+0":
            raise Exception("Calibration was not successfull ans:{:s}".
                format(ans))

    def wait_for_end_of_cal(self):
        fertig = False
        while not fertig:
            ans = self.conn.readln()
            if ans != "":
                fertig = True
        
        if ans != "+0":
            raise Exception("Calibration was not successfull ans:{:s}".
                format(ans))
        
        self.last_ans = ans
        
    def get_support_devices(self):
        if self.multimeter is None:
            self.multimeter = n_mul.device()
            self.multimeter.connect()
        
        if self.calibrator is None:
            self.calibrator = n_cal.device()
            self.calibrator.connect()


    def cal_ac_linearity(self):
        self.get_support_devices()

        eg.msgbox("Connect Calibrator and Multimeter in parallel to 8846 voltage")
        self.conn.writeln("Cal:Step 62")
        cal_value = float(self.conn.readln("Cal:Value?"))
        self.multimeter.volt_ac.activate(10)
        if abs(cal_value-1.19) >= 0.1:
            raise Exception("Wrong calibration value {:.3e}".format(cal_value))

        self.calibrator.volt_ac.stimulate(cal_value, 1200)
        self.multimeter.volt_ac.measure(1200,10,count=3)
        self.conn.writeln(
            "Cal:Value ACLIN, {:.5e}".format(self.multimeter.volt_ac.last.value))
        
        self.conn.writeln("Cal? OFF")
        self.wait_for_end_of_cal()

        self.conn.writeln("Cal:Step 63")
        cal_value = float(self.conn.readln("Cal:Value?"))
        self.multimeter.volt_ac.activate(1)
        if abs(cal_value-0.8) >= 0.1:
            raise Exception("Wrong calibration value {:.3e}".format(cal_value))

        self.calibrator.volt_ac.stimulate(cal_value, 1200)
        self.multimeter.volt_ac.measure(1200,1,count=3)
        self.conn.writeln(
            "Cal:Value ACLIN, {:.5e}".format(self.multimeter.volt_ac.last.value))
        
        self.conn.writeln("Cal? OFF")
        self.wait_for_end_of_cal()

        self.conn.writeln("Cal:Step 64")
        cal_value = float(self.conn.readln("Cal:Value?"))
        self.multimeter.volt_ac.activate(1)
        if abs(cal_value-0.4) >= 0.1:
            raise Exception("Wrong calibration value {:.3e}".format(cal_value))

        self.calibrator.volt_ac.stimulate(cal_value, 1200)
        self.multimeter.volt_ac.measure(1200,1,count=3)
        self.conn.writeln(
            "Cal:Value ACLIN, {:.5e}".format(self.multimeter.volt_ac.last.value))
        
        self.conn.writeln("Cal? OFF")
        self.wait_for_end_of_cal()

        self.conn.writeln("Cal:Step 65")
        cal_value = float(self.conn.readln("Cal:Value?"))
        self.multimeter.volt_ac.activate(1)
        if abs(cal_value-0.005) >= 0.001:
            raise Exception("Wrong calibration value {:.3e}".format(cal_value))

        self.calibrator.volt_ac.stimulate(cal_value, 1200)
        self.multimeter.volt_ac.measure(1200,0.1,count=3)
        self.conn.writeln(
            "Cal:Value ACLIN, {:.5e}".format(self.multimeter.volt_ac.last.value))
        
        self.conn.writeln("Cal? OFF")
        self.wait_for_end_of_cal()


    def cal_acv_gain(self):
        self.get_support_devices()

        eg.msgbox("Connect Calibrator and Multimeter in parallel to 8846 voltage")

        self.conn.writeln("Cal:Step 66")
        frequ = 1200
        cal_value = float(self.conn.readln("Cal:Value?"))
        self.multimeter.volt_ac.activate(cal_value)
        if abs(cal_value-0.1) >= 0.01:
            raise Exception("Wrong calibration value {:.3e}".format(cal_value))

        self.calibrator.volt_ac.stimulate(cal_value, frequ)
        self.multimeter.volt_ac.measure(frequ,cal_value,count=3)
        self.conn.writeln(
            "Cal:Value GVAC, {:.5e}".format(self.multimeter.volt_ac.last.value))
        
        time.sleep(0.1)        
        self.conn.writeln("Cal? ON")
        self.wait_for_end_of_cal()

        self.conn.writeln("Cal:Step 67")
        self.conn.writeln(
            "Cal:Value GVACS, {:.5e}".format(self.multimeter.volt_ac.last.value))
        
        time.sleep(0.1)        
        self.conn.writeln("Cal? ON")
        self.wait_for_end_of_cal()
        
        self.conn.writeln("Cal:Step 68")
        frequ = 50000
        cal_value = float(self.conn.readln("Cal:Value?"))
        self.multimeter.volt_ac.activate(cal_value)
        if abs(cal_value-0.1) >= 0.01:
            raise Exception("Wrong calibration value {:.3e}".format(cal_value))

        self.calibrator.volt_ac.stimulate(cal_value, frequ)
        self.multimeter.volt_ac.measure(frequ,cal_value,count=3)
        self.conn.writeln(
            "Cal:Value ACPOLE, {:.5e}".format(self.multimeter.volt_ac.last.value))
        
        time.sleep(0.1)        
        self.conn.writeln("Cal? ON")
        self.wait_for_end_of_cal()


        #1V
        self.conn.writeln("Cal:Step 69")
        frequ = 1200
        cal_value = float(self.conn.readln("Cal:Value?"))
        self.multimeter.volt_ac.activate(cal_value)
        if abs(cal_value-1) >= 0.1:
            raise Exception("Wrong calibration value {:.3e}".format(cal_value))

        self.calibrator.volt_ac.stimulate(cal_value, frequ)
        self.multimeter.volt_ac.measure(frequ,cal_value,count=3)
        self.conn.writeln(
            "Cal:Value GVAC, {:.5e}".format(self.multimeter.volt_ac.last.value))
        
        time.sleep(0.1)        
        self.conn.writeln("Cal? ON")
        self.wait_for_end_of_cal()

        self.conn.writeln("Cal:Step 70")
        self.conn.writeln(
            "Cal:Value GVACS, {:.5e}".format(self.multimeter.volt_ac.last.value))
        
        time.sleep(0.1)        
        self.conn.writeln("Cal? ON")
        self.wait_for_end_of_cal()

        self.conn.writeln("Cal:Step 71")
        # assumption calibrator is right at low frequency
        frequ = 10
        cal_value = float(self.conn.readln("Cal:Value?")) 
        self.calibrator.volt_ac.stimulate(cal_value, frequ)
        time.sleep(0.1)        
        self.conn.writeln("Cal? ON")
        self.wait_for_end_of_cal()

        
        self.conn.writeln("Cal:Step 72")
        frequ = 50000
        cal_value = float(self.conn.readln("Cal:Value?"))
        self.multimeter.volt_ac.activate(cal_value)
        if abs(cal_value-1) >= 0.1:
            raise Exception("Wrong calibration value {:.3e}".format(cal_value))

        self.calibrator.volt_ac.stimulate(cal_value, frequ)
        self.multimeter.volt_ac.measure(frequ,cal_value,count=3)
        self.conn.writeln(
            "Cal:Value ACPOLE, {:.5e}".format(self.multimeter.volt_ac.last.value))
        
        time.sleep(0.1)        
        self.conn.writeln("Cal? ON")
        self.wait_for_end_of_cal()



        #10V
        self.conn.writeln("Cal:Step 73")
        frequ = 1200
        cal_value = float(self.conn.readln("Cal:Value?"))
        self.multimeter.volt_ac.activate(cal_value)
        if abs(cal_value-10) >= 0.1:
            raise Exception("Wrong calibration value {:.3e}".format(cal_value))

        self.calibrator.volt_ac.stimulate(cal_value, frequ)
        self.multimeter.volt_ac.measure(frequ,cal_value,count=3)
        self.conn.writeln(
            "Cal:Value GVAC, {:.5e}".format(self.multimeter.volt_ac.last.value))
        
        time.sleep(0.1)
        self.conn.writeln("Cal? ON")
        self.wait_for_end_of_cal()

        self.conn.writeln("Cal:Step 74")
        self.conn.writeln(
            "Cal:Value GVACS, {:.5e}".format(self.multimeter.volt_ac.last.value))
        
        time.sleep(0.1)
        self.conn.writeln("Cal? ON")
        self.wait_for_end_of_cal()
        
        self.conn.writeln("Cal:Step 75")
        frequ = 50000
        cal_value = float(self.conn.readln("Cal:Value?"))
        self.multimeter.volt_ac.activate(cal_value)
        if abs(cal_value-10) >= 0.1:
            raise Exception("Wrong calibration value {:.3e}".format(cal_value))

        self.calibrator.volt_ac.stimulate(cal_value, frequ)
        self.multimeter.volt_ac.measure(frequ,cal_value,count=3)
        self.conn.writeln(
            "Cal:Value ACPOLE, {:.5e}".format(self.multimeter.volt_ac.last.value))
        
        time.sleep(0.1)
        self.conn.writeln("Cal? ON")
        self.wait_for_end_of_cal()


        #100V
        self.conn.writeln("Cal:Step 76")
        frequ = 1200
        cal_value = float(self.conn.readln("Cal:Value?"))
        self.multimeter.volt_ac.activate(cal_value)
        if abs(cal_value-100) >= 1:
            raise Exception("Wrong calibration value {:.3e}".format(cal_value))

        self.calibrator.volt_ac.stimulate(cal_value, frequ)
        self.multimeter.volt_ac.measure(frequ,cal_value,count=3)
        self.conn.writeln(
            "Cal:Value GVAC, {:.5e}".format(self.multimeter.volt_ac.last.value))
        
        time.sleep(0.1)
        self.conn.writeln("Cal? ON")
        self.wait_for_end_of_cal()

        self.conn.writeln("Cal:Step 77")
        self.conn.writeln(
            "Cal:Value GVACS, {:.5e}".format(self.multimeter.volt_ac.last.value))
        
        time.sleep(0.1)
        self.conn.writeln("Cal? ON")
        self.wait_for_end_of_cal()


        #700V
        self.conn.writeln("Cal:Step 79")
        frequ = 1200
        cal_value = float(self.conn.readln("Cal:Value?"))
        self.multimeter.volt_ac.activate(cal_value)
        if abs(cal_value-750) >= 1:
            raise Exception("Wrong calibration value {:.3e}".format(cal_value))

        cal_value = 700
        self.calibrator.volt_ac.stimulate(cal_value, frequ)
        self.multimeter.volt_ac.measure(frequ,cal_value,count=3)
        self.conn.writeln(
            "Cal:Value GVAC, {:.5e}".format(self.multimeter.volt_ac.last.value))
        
        time.sleep(0.1)
        self.conn.writeln("Cal? ON")
        self.wait_for_end_of_cal()

        self.conn.writeln("Cal:Step 80")
        self.conn.writeln(
            "Cal:Value GVACS, {:.5e}".format(self.multimeter.volt_ac.last.value))
        
        time.sleep(0.1)
        self.conn.writeln("Cal? ON")
        self.wait_for_end_of_cal()
        
        
    def cal_acv_hv_poles(self):
        self.get_support_devices()

        msg = "50kHZ AC Poles. Connect HV Source to Signal generator."
        eg.msgbox(msg)

        self.conn.writeln("Cal:Step 78")
        frequ = 50000
        cal_value = float(self.conn.readln("Cal:Value?"))
        self.multimeter.volt_ac.activate(cal_value)
        if abs(cal_value-100) >= 0.1:
            raise Exception("Wrong calibration value {:.3e}".format(cal_value))

        msg = "Adjust external source to 50kHZ 100V."
        eg.msgbox(msg)

        self.multimeter.volt_ac.measure(frequ,cal_value,count=3)
        self.conn.writeln(
            "Cal:Value ACPOLE, {:.5e}".format(self.multimeter.volt_ac.last.value))
        
        time.sleep(0.1)        
        self.conn.writeln("Cal? ON")
        self.wait_for_end_of_cal()


        self.conn.writeln("Cal:Step 81")
        frequ = 50000
        cal_value = 400
        self.multimeter.volt_ac.activate(cal_value)

        msg = "Adjust external source to 50kHZ 500V."
        eg.msgbox(msg)

        self.multimeter.volt_ac.measure(frequ,cal_value,count=3)
        self.conn.writeln(
            "Cal:Value ACPOLE, {:.5e}".format(self.multimeter.volt_ac.last.value))
        
        time.sleep(0.1)        
        self.conn.writeln("Cal? ON")
        self.wait_for_end_of_cal()


    def cal_vdc_gain(self):
        self.get_support_devices()

        eg.msgbox("Connect Calibrator and Multimeter in parallel to 8846 voltage")

        cal_datas = [
            (82, 1000, 900),
            (83, -1000, -900),
            (84, 100, 100),
            (85, -100, -100),
            (86, 10, 10),
            (87, -10, -10),
            (88, 1, 1),
            (89, -1, -1),
            (90, 0.1, 0.1),
            (91, -0.1, -0.1),
        ]
        
        for cal_data in cal_datas:
            self.conn.writeln("Cal:Step {:d}".format(cal_data[0]))
            cal_value = float(self.conn.readln("Cal:Value?"))
            if abs(cal_value-cal_data[1]) >= 0.1:
                raise Exception("Wrong calibration value {:.3e}".format(cal_value))
            cal_value = cal_data[2]
            self.multimeter.volt_dc.activate(cal_value)
    
            self.calibrator.volt_dc.stimulate(cal_value)
            self.multimeter.volt_dc.measure(cal_value,count=3)
            self.conn.writeln(
                "Cal:Value GVDC, {:.5e}".format(self.multimeter.volt_dc.last.value))
            
            time.sleep(0.1)        
            self.conn.writeln("Cal? ON")
            self.wait_for_end_of_cal()

    def cal_hi_idc_and_ac_gain(self):
        self.get_support_devices()

        eg.msgbox("Connect 10A Current input to calibrator")

        cal_datas = [
            (92, 1, 1),
            (93, -1, -1),
            (94, 10, 10),
            (95, -10, -10),
        ]
        
        for cal_data in cal_datas:
            self.conn.writeln("Cal:Step {:d}".format(cal_data[0]))
            cal_value = float(self.conn.readln("Cal:Value?"))
            if abs(cal_value-cal_data[1]) >= 0.1:
                raise Exception("Wrong calibration value {:.3e}".format(cal_value))
            cal_value = cal_data[2]
    
            self.calibrator.cur_dc.stimulate(cal_value)
            
            time.sleep(0.1)        
            self.conn.writeln("Cal? ON")
            self.wait_for_end_of_cal()


        cal_datas = [
            (96, 10, 10),
            (97, 10, 10),
            (98, 1, 1),
            (99, 1, 1),
        ]
        
        # we have to use 1kHz instead of 1.2kHz
        for cal_data in cal_datas:
            self.conn.writeln("Cal:Step {:d}".format(cal_data[0]))
            cal_value = float(self.conn.readln("Cal:Value?"))
            if abs(cal_value-cal_data[1]) >= 0.1:
                raise Exception("Wrong calibration value {:.3e}".format(cal_value))
            cal_value = cal_data[2]
            self.calibrator.cur_ac.stimulate(cal_value,1000)
            
            time.sleep(0.1)        
            self.conn.writeln("Cal? ON")
            self.wait_for_end_of_cal()


    def cal_lo_idc_and_ac_gain(self):
        self.get_support_devices()

        eg.msgbox("Connect 0.4A Current input to calibrator")

        cal_datas = [
            (100, 0.329),
            (101, 0.329),
            (102, 0.1),
            (103, 0.1),
            (104, 0.01),
            (105, 0.01),
            (106, 0.001),
            (107, 0.001),
            (108, 0.0001),
            (109, 0.0001),
        ]
        
        for cal_data in cal_datas:
            self.conn.writeln("Cal:Step {:d}".format(cal_data[0]))
            cal_value = float(self.conn.readln("Cal:Value?"))
            if abs(cal_value-cal_data[1]) >= 0.1:
                raise Exception("Wrong calibration value {:.3e}".format(cal_value))
    
            self.calibrator.cur_ac.stimulate(cal_value, 1200)
            
            time.sleep(0.1)        
            self.conn.writeln("Cal? ON")
            self.wait_for_end_of_cal()


        cal_datas = [
            (110, 0.0001),
            (111, -0.0001),
            (112, 0.001),
            (113, -0.001),
            (114, 0.01),
            (115, -0.01),
            (116, 0.1),
            (117, -0.1),
            (118, 0.329),
            (119, -0.329),
        ]
        
        for cal_data in cal_datas:
            self.conn.writeln("Cal:Step {:d}".format(cal_data[0]))
            cal_value = float(self.conn.readln("Cal:Value?"))
            if abs(cal_value-cal_data[1]) >= 0.1:
                raise Exception("Wrong calibration value {:.3e}".format(cal_value))
    
            self.calibrator.cur_dc.stimulate(cal_value)
            
            time.sleep(0.1)        
            self.conn.writeln("Cal? ON")
            self.wait_for_end_of_cal()


    def cal_ohm_gain(self):
        self.get_support_devices()

        eg.msgbox("Connect Calibrator in 2W res mode to 8846")

        cal_datas = [
            (120, 100e6),
        ]
        
        for cal_data in cal_datas:
            self.conn.writeln("Cal:Step {:d}".format(cal_data[0]))
            cal_value = float(self.conn.readln("Cal:Value?"))
            if abs(cal_value-cal_data[1]) >= 0.1:
                raise Exception("Wrong calibration value {:.3e}".format(cal_value))
    
            self.calibrator.res.settings["Comp"] = "off"
            self.calibrator.res.stimulate(cal_value)
            
            time.sleep(0.1)        
            self.conn.writeln("Cal? ON")
            self.wait_for_end_of_cal()

        eg.msgbox("Connect Calibrator in 2W res mode to 8846 in 4W mode")

        cal_datas = [
            (121, 10e6),
            (122, 1e6),
            (123, 100e3),
        ]
        
        for cal_data in cal_datas:
            self.conn.writeln("Cal:Step {:d}".format(cal_data[0]))
            cal_value = float(self.conn.readln("Cal:Value?"))
            if abs(cal_value-cal_data[1]) >= 0.1:
                raise Exception("Wrong calibration value {:.3e}".format(cal_value))
    
            self.calibrator.res.settings["Comp"] = "off"
            self.calibrator.res.stimulate(cal_value)
            
            time.sleep(0.1)        
            self.conn.writeln("Cal? ON")
            self.wait_for_end_of_cal()

        eg.msgbox("Connect Calibrator in 2W res mode to 8846 in 4W mode")

        cal_datas = [
            (124, 10e3),
            (125, 1e3),
            (126, 100),
            (127, 10),
        ]
        
        for cal_data in cal_datas:
            self.conn.writeln("Cal:Step {:d}".format(cal_data[0]))
            cal_value = float(self.conn.readln("Cal:Value?"))
            if abs(cal_value-cal_data[1]) >= 0.1:
                raise Exception("Wrong calibration value {:.3e}".format(cal_value))

            self.calibrator.res.settings["Comp"] = "4 wire"
    
            self.calibrator.res.stimulate(cal_value)
            
            time.sleep(0.1)        
            self.conn.writeln("Cal? ON")
            self.wait_for_end_of_cal()


    def cal_misc_gain(self):

        msg = "Attach 1GOhm in 2W mode"
        eg.msgbox(msg)

        self.conn.writeln("Cal:Step 128")
        cal_value = float(self.conn.readln("Cal:Value?"))
        if abs(cal_value-1e9) >= 10:
            raise Exception("Wrong calibration value {:.3e}".format(cal_value))

        r_cal_value =  1.005425e9
        self.conn.writeln(
            "Cal:Value GRES, {:.6e}".format(r_cal_value))
        
        time.sleep(0.1)        
        self.conn.writeln("Cal? ON")
        self.wait_for_end_of_cal()


        msg = "Attach 10nF Genrad 1419"
        eg.msgbox(msg)

        self.conn.writeln("Cal:Step 129")
        cal_value = float(self.conn.readln("Cal:Value?"))
        if abs(cal_value-10e-9) >= 0.1e-9:
            raise Exception("Wrong calibration value {:.3e}".format(cal_value))

        c_cal_value =  10.050e-9 + 39.9e-12
        self.conn.writeln(
            "Cal:Value GCAP1, {:.6e}".format(c_cal_value))
        
        time.sleep(0.1)        
        self.conn.writeln("Cal? ON")
        self.wait_for_end_of_cal()

        self.conn.writeln("Cal:Step 130")
        cal_value = float(self.conn.readln("Cal:Value?"))
        if abs(cal_value-10e-9) >= 0.1e-9:
            raise Exception("Wrong calibration value {:.3e}".format(cal_value))

        self.conn.writeln(
            "Cal:Value GCap2, {:.6e}".format(c_cal_value))
        
        time.sleep(0.1)        
        self.conn.writeln("Cal? ON")
        self.wait_for_end_of_cal()

    def cal_save_cal_constants(self):
        self.conn.writeln("Cal:REC")

    def connect(self , device=c_dev.fluke_8846A_01 , serial_number = "auto", simulation = False):
        """open interface and identify device"""
        self.conn = n_support.SerialDeviceConnection()
        self.conn.target = device
        self.conn.writeln("*rst;*CLS")  
        self.conn.writeln("*IDN?")  
        self.idn=self.conn.readln().split(",")
        if self.simulation:
            self.idn = ['FLUKE', '8846A', '1867008', '08/02/10-11:53']
        if self.idn[0] != "FLUKE" or self.idn[1] != "8846A":
            raise Exception("Wrong device connected:" + self.idn.__str__())
        self.conn.writeln("SYST:REM")        
        #self.conn.writeln("SYST:RWL")        
        self.serial_number=self.idn[2]
        self.calibrator = None
        self.multimeter = None
        pass

    def disconnect(self):
        self.conn.writeln("SYST:LOC;*STB?")
        to=n_support.TimeOut(10)
        while to.is_timed_out() == False:
            answer = self.conn.readln()
            if answer == "1":
                self.conn.close()
                to.set_timed_out()
            elif answer != "":
                print(("Schliesse Verbindung nicht, da antowrt of STB :" + answer))
                to.set_timed_out()
        self.active_settings = None        
        pass                  
    
    def procError(self):
        err_list = list()
        while True:
            self.conn.writeln("*ESR?;Syst:err?")
            err_info=self.conn.readln()
            if err_info[0:2] == "+0":
                break
            else:
                err_list.append(err_info)
                
        return err_list



if __name__ == '__main__':
    dev=device()
    dev.connect()
    #dev.cal_lock_unlock(lock=False)
    #dev.cal_shorts()
    #dev.cal_misc_gain()
    
    
