# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 12:05:00 2012

@author: Scheidt
@tested: 3.01.2013 12:13 MSC
"""
import winsound
import smt_cal_demo.utilities.easygui as eg
import logging
import smt_cal_demo.calibration.devices.support as n_support
import smt_cal_demo.calibration.tokens.devices as c_dev
import smt_cal_demo.calibration.tokens.electrical_properties as c_el
import smt_cal_demo.calibration.tokens.device_functions as c_fct
import smt_cal_demo.calibration.tokens.physical_units as c_phy
import smt_cal_demo.calibration.tokens.execution_modes as c_exm
from smt_cal_demo.calibration.models.support_v01 import Var

c_tc_type = "tc_type"

class ElPropertyMissing(Exception):
    pass


class StimulationDesc(object):
    
    def __init__(self):
        self.value = None
        self.unc_of_value = 0
        self.meas_range = None
        self.settings = None
        self.correction = 0
        self.unc_of_correction= 0
        self.frequency = None
        self.unc_of_frequency_drift = 0
        self.el_properties = None
        self.dispcorr = 0
        self.unc_of_dispcorr = 0
        self.drift = 0
        self.unc_of_drift = 0
    
        
class fct(object):

    def __init__(self,device):
        self.device = device  #links to device data
        self.settings = dict()
        self.last = StimulationDesc()


class Volt_AC(fct):
        
    
    def __init__(self,device):
        super(Volt_AC,self).__init__(device)
        self.settings = {
                c_fct.Function : c_fct.volt_ac,
                }

        self.ranges={
                        "_format" : "AC",
                        "0.033" : {"min" : 0.001, "<max" : 0.033 , "fmin" : 10 , "fmax" : 500e3 },
                        "0.33" : {"min" : 0.033, "<max" : 0.33 , "fmin" : 10 , "fmax" : 500e3 },
                        "3.3" : {"min" : 0.33, "<max" : 3.3 , "fmin" : 10 , "fmax" : 500e3 }, 
                        "33" : {"min" : 3.3, "<max" : 33 , "fmin" : 10 , "fmax" : 100e3 }, 
                        "330" : {"min" : 33, "<max" : 330 , "fmin" : 10 , "fmax" : 20e3 }, 
                        "1000" : {"min" : 330, "<max" : 1020 , "fmin" : 10 , "fmax" : 10e3 } 
                    }
                    
        self.el_properties_50Ohm = {
                                c_el.R_s : Var(50, 1e-2 * 50, c_phy.Ohm, "Series Resistance of voltage source")
                            }
        self.el_properties_5mOhm = {
                                c_el.R_s : Var(5e-3, 0.289 * 2 * 10e-2 * 5e-3, c_phy.Ohm, "Series Resistance of voltage source")
                            }

        self.baseSpec1yr = dict()
        self.baseSpec1yr["_format"] = "AC"
        self.baseSpec1yr["0.033"]={
                        "finterval" : [10, 45, 10e3, 20e3, 
                                    50e3, 100e3, 500e3],
                        "specs": 
                            [
                                { "p%" : 0.35, "fixu" : 20},
                                { "p%" : 0.15, "fixu" : 20},
                                { "p%" : 0.2 , "fixu" : 20},
                                { "p%" : 0.25, "fixu" : 20},
                                { "p%" : 0.35, "fixu" : 33},
                                { "p%" : 1   , "fixu" : 60},
                            ]
                        }
        self.baseSpec1yr["0.33"]={
                        "finterval" : [10, 45, 10e3, 20e3, 
                                    50e3, 100e3, 500e3],
                        "specs": 
                            [
                                { "p%" : 0.25 , "fixu" : 50},
                                { "p%" : 0.05 , "fixu" : 20},
                                { "p%" : 0.1  , "fixu" : 20},
                                { "p%" : 0.16 , "fixu" : 40},
                                { "p%" : 0.24 , "fixu" : 170},
                                { "p%" : 0.7  , "fixu" : 330},
                            ]
                        }
        self.baseSpec1yr["3.3"]={
                        "finterval" : [10, 45, 10e3, 20e3, 
                                    50e3, 100e3, 500e3],
                        "specs": 
                            [
                                { "p%" : 0.15 , "fixu" : 250},
                                { "p%" : 0.03 , "fixu" : 60},
                                { "p%" : 0.08 , "fixu" : 60},
                                { "p%" : 0.14 , "fixu" : 300},
                                { "p%" : 0.24 , "fixu" : 1700},
                                { "p%" : 0.5  , "fixu" : 3300},
                            ]
                        }
        self.baseSpec1yr["33"]={
                        "finterval" : [10, 45, 10e3, 20e3, 
                                    50e3, 100e3],
                        "specs": 
                            [
                                { "p%" : 0.15 , "fixu" : 2500},
                                { "p%" : 0.04 , "fixu" : 600},
                                { "p%" : 0.08 , "fixu" : 2600},
                                { "p%" : 0.19 , "fixu" : 5000},
                                { "p%" : 0.24 , "fixu" : 17000},
                            ]
                        }
        self.baseSpec1yr["330"]={
                        "finterval" : [45, 1e3, 10e3, 20e3],
                        "specs": 
                            [
                                { "p%" : 0.05 , "fixm" : 6.6},
                                { "p%" : 0.08 , "fixm" : 15},
                                { "p%" : 0.09 , "fixm" : 17},
                            ]
                        }
        self.baseSpec1yr["1000"]={
                        "finterval" : [45, 1e3, 5e3, 10e3],
                        "specs": 
                            [
                                { "p%" : 0.05 , "fixm" : 80},
                                { "p%" : 0.20 , "fixm" : 100},
                                { "p%" : 0.20 , "fixm" : 500},
                            ]
                        }
                        

    def get_el_properties(self, range_used, settings):
        # currently we have no model parameter
        # function is not well documented
        if range_used < 0.33:
            return self.el_properties_50Ohm
        else:
            return self.el_properties_5mOhm


    def uncertainty(self, value, frequency, range_used = None ,settings = None):
        avalue = abs(value)
        if range_used == None:
            range_key = n_support.find_rangeAC(avalue,frequency,self.ranges)
        else:
            range_key = n_support.find_rangeAC(range_used,frequency,self.ranges)
        

        zw_uncertainty = n_support.uncertainty_from_AC_spec(
                            avalue, frequency, 
                            self.baseSpec1yr[range_key], 
                            self.ranges[range_key]["<max"])       

        return zw_uncertainty              

    def uncertainty_f(self,frequency):
        if frequency < 0.01:
            raise n_support.OutOfRange("Uncertainty of frequency " + str(frequency) + " not specified")
        elif frequency < 10e3:
            return 25e-6*frequency + 1e-3
        elif frequency < 2e6:
            return 25e-6*frequency + 15e-3
        else:
            raise n_support.OutOfRange("Uncertainty of frequency " + str(frequency) + " not specified")
             
                            
    def stimulate(self, voltage, frequency):
        if not self.device.active_settings is self.settings:
            self.device.standby()
            self.device.active_settings = self.settings
        
        self.last = StimulationDesc()

        if c_exm.no_io in c_exm.execution_mode:
            if voltage < 0.1*33e-3:
                raise Exception("AC Voltages below 3.3mV specified")
            elif voltage < 33e-3:
                used_range = 32.9e-3
            elif voltage < 0.33:
                used_range = 329e-3
            elif voltage <3.3:
                used_range = 3.29
            elif voltage <33:
                used_range = 32.9
            elif voltage <330:
                used_range = 329
            elif voltage <= 1000:
                used_range = 999
            else:
                raise Exception("Voltage above 1000V specified")
            
            out_value = voltage
            out_frequency = frequency
            pass
        else:
            self.device.conn.writeln("OUT {0:.6e}V,{1:.6e}Hz".format(voltage,frequency))            
            to=n_support.TimeOut(10)
            self.device.conn.writeln("*OPC?")
            while to.is_timed_out() == False:
                answer_opc = self.device.conn.readln()
                if answer_opc == "1":
                    to.set_timed_out()
                elif answer_opc == "0":
                    self.device.conn.writeln("*OPC?")

            if self.device.conn.readln("oper?") == "0":
                self.device.conn.writeln("oper")
                to=n_support.TimeOut(20)
                self.device.conn.writeln("*OPC?")
                while to.is_timed_out() == False:
                    answer_opc = self.device.conn.readln()                
                    if answer_opc == "1":
                        to.set_timed_out()
                    elif answer_opc == "0":
                        self.device.conn.writeln("*OPC?")
        
            stay_on_check = False
            while stay_on_check == False:
                if self.device.conn.readln("oper?") == "0":
                    Freq = 2500  # Set Frequency To 2500 Hertz
                    Dur = 1000  # Set Duration To 1000 ms == 1 second
                    winsound.Beep(Freq, Dur)
                    if eg.ynbox("Calibrator doesn't stay on. Check everything and switch on manually if possible. Try again?")==0:
                        raise n_support.OutputError("Kalibrator bleibt nicht betriebsbereit")            
                else:
                    stay_on_check = True
            
            answer_range = self.device.conn.readln("range?").split(",")
            answer_out =self.device.conn.readln("out?").split(",")
            out_value = float(answer_out[0])
            out_frequency = float(answer_out[4])
            range_names={
                        "AC33MV" : 32.9e-3 ,
                        "AC330MV" : 329e-3 ,
                        "AC3_3V" : 3.29 ,
                        "AC33V": 32.9 ,
                        "AC330V": 329.0 ,
                        "AC1000V": 999.0
            }
            used_range = range_names[answer_range[0]]

        self.last.value = out_value
        self.last.frequency = out_frequency  
        self.last.unc_of_frequency_drift = 0.5 * self.uncertainty_f(out_frequency)
        self.last.unc_of_drift = 0.5 * self.uncertainty(
                out_value, out_frequency, used_range, self.settings)            
        self.last.correction = 0
        self.last.unc_of_correction = 0
        self.last.settings = self.settings
        self.last.meas_range = used_range        
        self.last.el_properties = self.get_el_properties(used_range, self.settings)
        return out_value        
    

class Volt_DC(fct):
    
    def __init__(self,device):
        super(Volt_DC,self).__init__(device)

        self.settings = {
                c_fct.Function : c_fct.volt_dc,
                }

        self.ranges={
                        "_format" : "DC",
                        "330e-3" : {"min" : 0, "<max" : 0.33 },
                        "3.3" : {"min" : 0, "<max" : 3.3 },
                        "33" : {"min" : 0, "<max" : 33 }, 
                        "330" : {"min" : 30, "<max" : 330 }, 
                        "1020" : {"min" : 100, "<max" : 1020.000001 } 
                    }

        self.el_properties_50Ohm = {
                                c_el.R_s : Var(50, 1e-2 * 50, c_phy.Ohm, "Series Resistance of voltage source")
                            }
        self.el_properties_5mOhm = {
                                c_el.R_s : Var(5e-3, 0.289 * 2 * 10e-2 * 5e-3, c_phy.Ohm, "Series Resistance of voltage source")
                            }

        self.baseSpec1yr = dict()
        self.baseSpec1yr["_format"] = "DC"
        self.baseSpec1yr["330e-3"]={ "p%" : 0.006, "fixu" : 3}
        self.baseSpec1yr["3.3"]={ "p%" : 0.005, "fixu" : 5}
        self.baseSpec1yr["33"]={ "p%" : 0.005, "fixu" : 50}
        self.baseSpec1yr["330"]={ "p%" : 0.0055, "fixu" : 500}
        self.baseSpec1yr["1020"]={ "p%" : 0.0055, "fixu" : 1500}
                        

    def get_el_properties(self, range_used, settings = None):
        if range_used is None:
            range_used = self.last.meas_range
        if range_used < 0.33:
            return self.el_properties_50Ohm
        else:
            return self.el_properties_5mOhm

    def set_el_property(self, prop_to_set, property_name, range_used = None, **add_args):
        """ writes data of required property to prop_to_set"""
        if property_name == c_el.R_s:    
            if range_used is None:
                range_used = self.last.meas_range
            if range_used < 0.33:
                zw = self.el_properties_50Ohm[c_el.R_s]
            else:
                zw = self.el_properties_5mOhm[c_el.R_s]
            prop_to_set.v = zw.v
            prop_to_set.u = zw.u
        else:
            pass
            raise ElPropertyMissing("Requested property " + property_name + " not available")
        return


    def uncertainty(self, value = None, range_used = None , *pos_args, **add_args):
        if value is None:
            value = self.last.value
        avalue = abs(value)
        if range_used == None:
            range_key = n_support.find_range(avalue,self.ranges)
        else:
            range_key = n_support.find_range(range_used,self.ranges)
        

        zw_uncertainty = n_support.uncertainty_from_spec(
                            avalue, 
                            self.baseSpec1yr[range_key], 
                            self.ranges[range_key]["<max"])       

        return zw_uncertainty                            
                            
    
    def stimulate(self, voltage):
        if not self.device.active_settings is self.settings:
            self.device.standby()
            self.device.active_settings = self.settings
        
        if c_exm.no_io in c_exm.execution_mode:
            if voltage < 0.33:
                used_range = 329e-3
            elif voltage <3.3:
                used_range = 3.29
            elif voltage <33:
                used_range = 32.9
            elif voltage <330:
                used_range = 329
            elif voltage <= 1000:
                used_range = 999
            else:
                raise Exception("Voltage above 1000V specified")
            
            out_value = voltage
            logging.info("SW does not simulate range locking")    
        else:
            self.device.conn.writeln("OUT {0:.6e}V,0Hz".format(voltage))            
            to=n_support.TimeOut(10)
            self.device.conn.writeln("*OPC?")
            while to.is_timed_out() == False:
                answer_opc = self.device.conn.readln()
                if answer_opc == "1":
                    to.set_timed_out()
                elif answer_opc == "0":
                    self.device.conn.writeln("*OPC?")
                

            if self.device.conn.readln("oper?") == "0":
                self.device.conn.writeln("oper")
                to=n_support.TimeOut(10)
                self.device.conn.writeln("*OPC?")
                while to.is_timed_out() == False:
                    answer_opc = self.device.conn.readln()                
                    if answer_opc == "1":
                        to.set_timed_out()
                    elif answer_opc == "0":
                        self.device.conn.writeln("*OPC?")

            stay_on_check = False
            while stay_on_check == False:
                if self.device.conn.readln("oper?") == "0":
                    Freq = 2500  # Set Frequency To 2500 Hertz
                    Dur = 1000  # Set Duration To 1000 ms == 1 second
                    winsound.Beep(Freq, Dur)
                    if eg.ynbox("Calibrator doesn't stay on. Check everything and switch on manually if possible. Try again?")==0:
                        raise n_support.OutputError("Kalibrator bleibt nicht betriebsbereit")            
                else:
                    stay_on_check = True
            
            
            answer_range = self.device.conn.readln("range?").split(",")
            answer_out =self.device.conn.readln("out?").split(",")
            out_value = float(answer_out[0])
            range_names={
                        "DC330MV" : 329e-3 ,
                        "DC3_3V" : 3.29 ,
                        "DC33V": 32.9 ,
                        "DC330V": 329.0 ,
                        "DC1000V": 999.0
            }
            used_range = range_names[answer_range[0]]
            
        self.last.value = out_value
        self.last.frequency = None        
        self.last.unc_of_drift = 0.5 * self.uncertainty(
                out_value, used_range, self.settings)            
        self.last.correction = 0
        self.last.unc_of_correction = 0
        self.last.settings = self.settings
        self.last.meas_range = used_range        
        self.last.el_properties = self.get_el_properties(used_range, self.settings)

            
        return out_value        


class Cur_AC(fct):
    
    def __init__(self,device):
        super(Cur_AC,self).__init__(device)
        self.settings = {
                    c_fct.Function : c_fct.cur_ac,
                    }
        
        self.ranges={
                        "_format" : "AC",
                        "0.33e-3" : {"min" : 0.029e-3, "<max" : 0.33e-3 , "fmin" : 10 , "fmax" : 10e3 },
                        "3.3e-3" : {"min" : 0.33e-3, "<max" : 3.3e-3 , "fmin" : 10 , "fmax" : 10e3 }, 
                        "33e-3" : {"min" : 3.3e-3, "<max" : 33e-3 , "fmin" : 10 , "fmax" : 10e3 }, 
                        "330e-3" : {"min" : 33e-3, "<max" : 330e-3 , "fmin" : 10 , "fmax" : 10e3 }, 
                        "2.2" : {"min" : 330e-3, "<max" : 2.2 , "fmin" : 10 , "fmax" : 5e3 }, 
                        "11" : {"min" : 2.2, "<max" : 11.000001 , "fmin" : 45 , "fmax" : 1e3 } 
                    }

        self.baseSpec1yr = dict()
        self.baseSpec1yr["_format"] = "AC"
        self.baseSpec1yr["0.33e-3"]={
                        "finterval" : [10, 20, 45, 1e3, 
                                    5e3, 10e3],
                        "specs": 
                            [
                                { "p%" : 0.25 , "fixu" : 0.15},
                                { "p%" : 0.125 , "fixu" : 0.15},
                                { "p%" : 0.125  , "fixu" : 0.25},
                                { "p%" : 0.4 , "fixu" : 0.15},
                                { "p%" : 1.25 , "fixu" : 0.15},
                            ]
                        }
        self.baseSpec1yr["3.3e-3"]={
                        "finterval" : [10, 20, 45, 1e3, 
                                    5e3, 10e3],
                        "specs": 
                            [
                                { "p%" : 0.2 , "fixu" : 0.3},
                                { "p%" : 0.1 , "fixu" : 0.3},
                                { "p%" : 0.1  , "fixu" : 0.3},
                                { "p%" : 0.2 , "fixu" : 0.3},
                                { "p%" : 0.6 , "fixu" : 0.3},
                            ]
                        }
        self.baseSpec1yr["33e-3"]={
                        "finterval" : [10, 20, 45, 1e3, 
                                    5e3, 10e3],
                        "specs": 
                            [
                                { "p%" : 0.2 , "fixu" : 3.0},
                                { "p%" : 0.1 , "fixu" : 3.0},
                                { "p%" : 0.09  , "fixu" : 3.0},
                                { "p%" : 0.2 , "fixu" : 3.0},
                                { "p%" : 0.6 , "fixu" : 3.0},
                            ]
                        }
        self.baseSpec1yr["330e-3"]={
                        "finterval" : [10, 20, 45, 1e3, 
                                    5e3, 10e3],
                        "specs": 
                            [
                                { "p%" : 0.2 , "fixu" : 30.0},
                                { "p%" : 0.1 , "fixu" : 30.0},
                                { "p%" : 0.09  , "fixu" : 30.0},
                                { "p%" : 0.2 , "fixu" : 30.0},
                                { "p%" : 0.6 , "fixu" : 30.0},
                            ]
                        }
        self.baseSpec1yr["2.2"]={
                        "finterval" : [10, 45, 1e3, 5e3],
                        "specs": 
                            [
                                { "p%" : 0.2 , "fixu" : 300.0},
                                { "p%" : 0.1 , "fixu" : 300.0},
                                { "p%" : 0.75  , "fixu" : 300.0},
                            ]
                        }
        self.baseSpec1yr["11"]={
                        "finterval" : [45, 65, 500, 1e3],
                        "specs": 
                            [
                                { "p%" : 0.06 , "fixu" : 2000.0},
                                { "p%" : 0.1 , "fixu" : 2000.0},
                                { "p%" : 0.33  , "fixu" : 2000.0},
                            ]
                        }
                        

    def get_el_properties(self, range_used, settings):
        # currently we have no model parameter
        # function is not well documented
        return dict()


    def uncertainty(self, value, frequency, range_used = None ,settings = None):
        avalue = abs(value)
        if range_used == None:
            range_key = n_support.find_rangeAC(avalue,frequency,self.ranges)
        else:
            range_key = n_support.find_rangeAC(range_used,frequency,self.ranges)
        

        zw_uncertainty = n_support.uncertainty_from_AC_spec(
                            avalue, frequency, 
                            self.baseSpec1yr[range_key], 
                            self.ranges[range_key]["<max"])       

        return zw_uncertainty                            
                            

    def uncertainty_f(self, frequency):
        if frequency < 0.01:
            raise n_support.OutOfRange("Uncertainty of frequency " + str(frequency) + " not specified")
        elif frequency < 10e3:
            return 25e-6*frequency + 1e-3
        elif frequency < 2e6:
            return 25e-6*frequency + 15e-3
        else:
            raise n_support.OutOfRange("Uncertainty of frequency " + str(frequency) + " not specified")

    
    def stimulate(self, current, frequency):
        if not self.device.active_settings is self.settings:
            self.device.standby()
            self.device.active_settings = self.settings

        if c_exm.no_io in c_exm.execution_mode:
            if current < 33e-6:
                raise Exception("AC-Current <33e-6 specified")
            elif current <330e-6:
                used_range = 329e-6
            elif current <3.3e-3:
                used_range = 3.29e-2
            elif current <33e-3:
                used_range = 32.9e-3
            elif current <330e-3:
                used_range = 329e-3
            elif current <2.2:
                used_range = 2.19
            elif current <= 11:
                used_range = 11
            else:
                raise Exception("Current above 11A specified")
            
            out_value = current
            out_frequency = frequency
            logging.info("SW does not simulate range locking")    
        else:        
            self.device.conn.writeln("OUT {0:.6e}A,{1:.6e}Hz".format(current,frequency)) 
            to=n_support.TimeOut(10)
            self.device.conn.writeln("*OPC?")
            while to.is_timed_out() == False:
                answer_opc = self.device.conn.readln()
                if answer_opc == "1":
                    to.set_timed_out()
                elif answer_opc == "0":
                    self.device.conn.writeln("*OPC?")
                    
    
            if self.device.conn.readln("oper?") == "0":
                self.device.conn.writeln("oper")
                to=n_support.TimeOut(10)
                self.device.conn.writeln("*OPC?")
                while to.is_timed_out() == False:
                    answer_opc = self.device.conn.readln()                
                    if answer_opc == "1":
                        to.set_timed_out()
                    elif answer_opc == "0":
                        self.device.conn.writeln("*OPC?")
                
            stay_on_check = False
            while stay_on_check == False:
                if self.device.conn.readln("oper?") == "0":
                    Freq = 2500  # Set Frequency To 2500 Hertz
                    Dur = 1000  # Set Duration To 1000 ms == 1 second
                    winsound.Beep(Freq, Dur)
                    if eg.ynbox("Calibrator doesn't stay on. Check everything and switch on manually if possible. Try again?")==0:
                        raise n_support.OutputError("Kalibrator bleibt nicht betriebsbereit")            
                else:
                    stay_on_check = True
                
            answer_range = self.device.conn.readln("range?").split(",")
            answer_out =self.device.conn.readln("out?").split(",")
            out_value = float(answer_out[0])
            out_frequency = float(answer_out[4])
            range_names={
                        "AC330UA_A" : 329e-6 ,
                        "AC3_3MA_A" : 3.29e-3 ,
                        "AC33MA_A" : 32.9e-3 ,
                        "AC330MA_A" : 329e-3 ,
                        "AC2_2A_A" : 2.19 ,
                        "AC11A_A": 11 ,
            }
            used_range = range_names[answer_range[0]]

        self.last.value = out_value
        self.last.frequency = out_frequency        
        self.last.unc_of_frequency_drift = 0.5 * self.uncertainty_f(out_frequency)
        self.last.unc_of_drift = 0.5 * self.uncertainty(
                out_value, out_frequency, used_range, self.settings)            
        self.last.correction = 0
        self.last.unc_of_correction = 0
        self.last.settings = self.settings
        self.last.meas_range = used_range        
        self.last.el_properties = self.get_el_properties(used_range, self.settings)
            
        return out_value        

    
class Cur_DC(fct):
    
    
    def __init__(self,device):
        super(Cur_DC,self).__init__(device)
        self.settings = {
                    c_fct.Function : c_fct.cur_dc,
                    }
                    
        self.el_properties = {
                                c_el.R_p : Var(10e6, 1e-2 * 10e6, c_phy.Ohm, "Parallel Resistance of current source")
                            }
                    
        self.ranges={
                        "_format" : "DC",
                        "3.3e-3" : {"min" : 0, "<max" : 3.3e-3 },
                        "33e-3" : {"min" : 0, "<max" : 3.3e-2 },
                        "330e-3" : {"min" : 0, "<max" : 3.3e-1 },
                        "2.2" : {"min" : 0, "<max" : 2.2 },
                        "11" : {"min" : 0, "<max" : 11.00001 },
                    }

        self.baseSpec1yr = dict()
        self.baseSpec1yr["_format"] = "DC"
        self.baseSpec1yr["3.3e-3"]={ "p%" : 0.013, "fixu" : 0.05 }
        self.baseSpec1yr["33e-3"]={ "p%" : 0.01, "fixu" : 0.25 }
        self.baseSpec1yr["330e-3"]={ "p%" : 0.01, "fixu" : 3.3 }
        self.baseSpec1yr["2.2"]={ "p%" : 0.03, "fixu" : 44 }
        self.baseSpec1yr["11"]={ "p%" : 0.06, "fixu" : 330 }
                        

    def get_el_properties(self, range_used, settings):
        # currently we have no model parameter
        # function is not well documented
        return self.el_properties


    def uncertainty(self, value, range_used = None ,settings = None):
        avalue = abs(value)
        if range_used == None:
            range_key = n_support.find_range(avalue,self.ranges)
        else:
            range_key = n_support.find_range(range_used,self.ranges)
        

        zw_uncertainty = n_support.uncertainty_from_spec(
                            avalue, 
                            self.baseSpec1yr[range_key], 
                            self.ranges[range_key]["<max"])       

        return zw_uncertainty                            
                            
    
    def stimulate(self, current):
        if not self.device.active_settings is self.settings:
            self.device.standby()
            self.device.active_settings = self.settings
        
        if c_exm.no_io in c_exm.execution_mode:
            if current < 3.3e-3:
                used_range = 3.29e-3
            elif current <33e-3:
                used_range = 3.29e-2
            elif current <330e-3:
                used_range = 3.29e-1
            elif current <2.2:
                used_range = 2.19
            elif current <= 11:
                used_range = 11
            else:
                raise Exception("Current above 11A specified")
            
            out_value = current
            logging.info("SW does not simulate range locking")    
        else:
            self.device.conn.writeln("OUT {0:.6e}A,0Hz".format(current))            
            to=n_support.TimeOut(10)
            self.device.conn.writeln("*OPC?")
            while to.is_timed_out() == False:
                answer_opc = self.device.conn.readln()
                if answer_opc == "1":
                    to.set_timed_out()
                elif answer_opc == "0":
                    self.device.conn.writeln("*OPC?")
                    
    
            if self.device.conn.readln("oper?") == "0":
                self.device.conn.writeln("oper")
                to=n_support.TimeOut(10)
                self.device.conn.writeln("*OPC?")
                while to.is_timed_out() == False:
                    answer_opc = self.device.conn.readln()                
                    if answer_opc == "1":
                        to.set_timed_out()
                    elif answer_opc == "0":
                        self.device.conn.writeln("*OPC?")
                
            stay_on_check = False
            while stay_on_check == False:
                if self.device.conn.readln("oper?") == "0":
                    Freq = 2500  # Set Frequency To 2500 Hertz
                    Dur = 1000  # Set Duration To 1000 ms == 1 second
                    winsound.Beep(Freq, Dur)
                    if eg.ynbox("Calibrator doesn't stay on. Check everything and switch on manually if possible. Try again?")==0:
                        raise n_support.OutputError("Kalibrator bleibt nicht betriebsbereit")            
                else:
                    stay_on_check = True
                
            answer_range = self.device.conn.readln("range?").split(",")
            answer_out =self.device.conn.readln("out?").split(",")
            out_value = float(answer_out[0])
            range_names={
                        "DC3_3MA_A" : 3.29e-3 ,
                        "DC33MA_A" : 3.29e-2 ,
                        "DC330MA_A" : 3.29e-1 ,
                        "DC2_2A_A": 2.19 ,
                        "DC11A_A": 11 ,
            }
            used_range = range_names[answer_range[0]]
            
        self.last.value = out_value
        self.last.frequency = None        
        self.last.unc_of_drift = 0.5 * self.uncertainty(
                out_value, used_range, self.settings)            
        self.last.correction = 0
        self.last.unc_of_correction = 0
        self.last.settings = self.settings
        self.last.meas_range = used_range        
        self.last.el_properties = self.get_el_properties(used_range, self.settings)

            
        return out_value        


class Res(fct):    
    
    
    def __init__(self,device):
        super(Res,self).__init__(device)
        self.settings = {
                    c_fct.Function : "Res",
                    "Comp" : "off"  # 2 wire 4 wire
                    }
        self.ranges={
                        "_format" : "DC",
                        "11" : {"min" : 0, "<max" : 1.1e1 },
                        "33" : {"min" : 1.1e1, "<max" : 3.3e1 },
                        "110" : {"min" : 3.3e1, "<max" : 1.10e2 },
                        "330" : {"min" : 1.1e2, "<max" : 3.3e2 },
                        "1.1e3" : {"min" : 330, "<max" : 1.1e3 },
                        "3.3e3" : {"min" : 1.1e3, "<max" : 3.3e3 },
                        "11e3" : {"min" : 3.3e3, "<max" : 1.1e4 },
                        "33e3" : {"min" : 1.1e4, "<max" : 3.3e4 },
                        "110e3" : {"min" : 3.3e4, "<max" : 1.1e5 },
                        "330e3" : {"min" : 1.1e5, "<max" : 3.3e5 },
                        "1.1e6" : {"min" : 3.3e5, "<max" : 1.1e6 },
                        "3.3e6" : {"min" : 1.1e6, "<max" : 3.3e6 },
                        "11e6" : {"min" : 3.3e6, "<max" : 1.1e7 },
                        "33e6" : {"min" : 1.1e7, "<max" : 3.3e7 },
                        "110e6" : {"min" : 3.3e7, "<max" : 1.1e8 },
                        "330e6" : {"min" : 1.1e8, "<max" : 3.3000001e8 },
                    }

        self.baseSpec1yr = dict()
        self.baseSpec1yr["_format"] = "DC"
        self.baseSpec1yr["11"]={ "p%" : 0.012, "fix" : 0.008}
        self.baseSpec1yr["33"]={ "p%" : 0.012, "fix" : 0.015}
        self.baseSpec1yr["110"]={ "p%" : 0.009, "fix" : 0.015}
        self.baseSpec1yr["330"]={ "p%" : 0.009, "fix" : 0.015}
        self.baseSpec1yr["1.1e3"]={ "p%" : 0.009, "fix" : 0.06}
        self.baseSpec1yr["3.3e3"]={ "p%" : 0.009, "fix" : 0.06}
        self.baseSpec1yr["11e3"]={ "p%" : 0.009, "fix" : 0.6}
        self.baseSpec1yr["33e3"]={ "p%" : 0.009, "fix" : 0.6}
        self.baseSpec1yr["110e3"]={ "p%" : 0.011, "fix" : 6}
        self.baseSpec1yr["330e3"]={ "p%" : 0.012, "fix" : 6}
        self.baseSpec1yr["1.1e6"]={ "p%" : 0.015, "fix" : 55}
        self.baseSpec1yr["3.3e6"]={ "p%" : 0.015, "fix" : 55}
        self.baseSpec1yr["11e6"]={ "p%" : 0.06, "fix" : 550}
        self.baseSpec1yr["33e6"]={ "p%" : 0.1, "fix" : 550}
        self.baseSpec1yr["110e6"]={ "p%" : 0.5, "fix" : 5500}
        self.baseSpec1yr["330e6"]={ "p%" : 0.5, "fix" : 16500}
                        

    def get_el_properties(self, range_used, settings):
        # currently we have no model parameter
        # function is not well documented
        return dict()


    def uncertainty(self, value, range_used = None ,settings = None):
        avalue = abs(value)
        if range_used == None:
            range_key = n_support.find_range(avalue,self.ranges)
        else:
            range_key = n_support.find_range(range_used,self.ranges)
        
        
        zw_uncertainty = n_support.uncertainty_from_spec(
                            avalue, 
                            self.baseSpec1yr[range_key], 
                            self.ranges[range_key]["<max"])       

        return zw_uncertainty                            
                            
    
    def stimulate(self, resistance):
        if not self.device.active_settings is self.settings:
            self.device.standby()
            self.device.active_settings = self.settings
        
        
        self.device.conn.writeln("OUT {0:.6e}Ohm".format(resistance))            

        if self.settings["Comp"] == "off":
            self.device.conn.writeln("ZCOMP NONE")            
        elif self.settings["Comp"] == "2 wire":
            self.device.conn.writeln("ZCOMP WIRE2")            
        elif self.settings["Comp"] == "4 wire":
            self.device.conn.writeln("ZCOMP WIRE4")
        else:
            raise n_support.SettingsError("Wrong Compensation setting")            
            
        to=n_support.TimeOut(10)
        self.device.conn.writeln("*OPC?")
        while to.is_timed_out() == False:
            answer_opc = self.device.conn.readln()
            if answer_opc == "1":
                to.set_timed_out()
            elif answer_opc == "0":
                self.device.conn.writeln("*OPC?")

        # process errors caused by trial to change compensation

        err_code = int(self.device.procError().split(",")[0])                
        while err_code!=0:
            if err_code == 539:
                self.settings["Comp"] = "off"
            elif err_code == 548:    
                self.settings["Comp"] = "off"
            
            err_code = int(self.device.procError().split(",")[0])              
            
        if self.device.conn.readln("oper?") == "0":
            self.device.conn.writeln("oper")
            to=n_support.TimeOut(10)
            self.device.conn.writeln("*OPC?")
            while to.is_timed_out() == False:
                answer_opc = self.device.conn.readln()                
                if answer_opc == "1":
                    to.set_timed_out()
                elif answer_opc == "0":
                    self.device.conn.writeln("*OPC?")
            
        if self.device.conn.readln("oper?") == "0":
            raise n_support.OutputError("Kalibrator bleibt nicht betriebsbereit")            
            
        answer_range = self.device.conn.readln("range?").split(",")
        answer_out =self.device.conn.readln("out?").split(",")
        out_value = float(answer_out[0])
        range_names={
                    "R11OHM" : 10.9 ,
                    "R33OHM" : 32.9 ,
                    "R110OHM": 109 ,
                    "R330OHM": 329.0 ,
                    "R1_1KOHM": 1.09e3 ,
                    "R3_3KOHM": 3.29e3 ,
                    "R11KOHM": 1.09e4 ,
                    "R33KOHM": 3.29e4 ,
                    "R110KOHM": 1.09e5 ,
                    "R330KOHM": 3.29e5 ,
                    "R1_1MOHM": 1.09e6 ,
                    "R3_3MOHM": 3.29e6 ,
                    "R11MOHM": 1.09e7 ,
                    "R33MOHM": 3.29e7 ,
                    "R110MOHM": 1.09e8 ,
                    "R330MOHM": 3.29e8 ,
        }
        used_range = range_names[answer_range[0]]
        self.last.value = out_value
        self.last.frequency = None        
        self.last.unc_of_drift = 0.5 * self.uncertainty(
                out_value, used_range, self.settings)            
        self.last.correction = 0
        self.last.unc_of_correction = 0
        self.last.settings = self.settings
        self.last.meas_range = used_range        
        self.last.el_properties = self.get_el_properties(used_range, self.settings)

            
        return out_value        

class Cap(fct):    
    
    def __init__(self,device):
        super(Cap,self).__init__(device)
        self.settings = {
                    c_fct.Function : c_fct.cap,
                    "Comp" : "off"  # 2 wire 4 wire
                    }
                    
        self.el_properties = {
                                c_el.C_p : Var(0, 0., c_phy.F, "Parallel offset capacity")
                            }
                    
        self.ranges={
                        "_format" : "DC",
                        "0.5e-9" : {"min" : 0.33e-9, "<max" : 0.5e-9 },
                        "1.1e-9" : {"min" : 0.5e-9, "<max" : 1.1e-9 },
                        "3.3e-9" : {"min" : 1.1e-9, "<max" : 3.3e-9 },
                        "11e-9" : {"min" : 3.3e-9, "<max" : 1.1e-8 },
                        "33e-9" : {"min" : 1.1e-8, "<max" : 3.3e-8 },
                        "110e-9" : {"min" : 3.3e-8, "<max" : 1.1e-7 },
                        "330e-9" : {"min" : 1.1e-7, "<max" : 3.3e-7 },
                        "1.1e-6" : {"min" : 3.3e-7, "<max" : 1.1e-6 },
                        "3.3e-6" : {"min" : 1.1e-6, "<max" : 3.3e-6 },
                        "11e-6" : {"min" : 3.3e-6, "<max" : 1.1e-5 },
                        "33e-6" : {"min" : 1.1e-5, "<max" : 3.3e-5 },
                        "110e-6" : {"min" : 3.3e-5, "<max" : 1.1e-4 },
                        "330e-6" : {"min" : 1.1e-5, "<max" : 3.3e-4 },
                        "1.1e-3" : {"min" : 3.3e-4, "<max" : 1.1e-3 },
                    }

        self.baseSpec1yr = dict()
        self.baseSpec1yr["_format"] = "DC"
        self.baseSpec1yr["0.5e-9"]={ "p%" : 0.5, "fixn" : 0.01}
        self.baseSpec1yr["1.1e-9"]={ "p%" : 0.5, "fixn" : 0.01}
        self.baseSpec1yr["3.3e-9"]={ "p%" : 0.5, "fixn" : 0.01}
        self.baseSpec1yr["11e-9"]={ "p%" : 0.5, "fixn" : 0.01}
        self.baseSpec1yr["33e-9"]={ "p%" : 0.25, "fixn" : 0.1}
        self.baseSpec1yr["110e-9"]={ "p%" : 0.25, "fixn" : 0.1}
        self.baseSpec1yr["330e-9"]={ "p%" : 0.25, "fixn" : 0.3}
        self.baseSpec1yr["1.1e-6"]={ "p%" : 0.25, "fixn" : 1}
        self.baseSpec1yr["3.3e-6"]={ "p%" : 0.35, "fixn" : 3}
        self.baseSpec1yr["11e-6"]={ "p%" : 0.35, "fixn" : 10}
        self.baseSpec1yr["33e-6"]={ "p%" : 0.4, "fixn" : 30}
        self.baseSpec1yr["110e-6"]={ "p%" : 0.5, "fixn" : 100}
        self.baseSpec1yr["330e-6"]={ "p%" : 0.7, "fixn" : 300}
        self.baseSpec1yr["1.1e-3"]={ "p%" : 1, "fixn" : 300}

                        
    def get_el_properties(self, range_used, settings):
        # currently we have no model parameter
        # function is not well documented
        return self.el_properties


    def uncertainty(self, value, range_used = None ,settings = None):
        avalue = abs(value)
        if range_used == None:
            range_key = n_support.find_range(avalue,self.ranges)
        else:
            range_key = n_support.find_range(range_used,self.ranges)
        
        
        zw_uncertainty = n_support.uncertainty_from_spec(
                            avalue, 
                            self.baseSpec1yr[range_key], 
                            self.ranges[range_key]["<max"])       

        return zw_uncertainty                            
                            
    
    def stimulate(self, capacity):
        if not self.device.active_settings is self.settings:
            self.device.standby()
            self.device.active_settings = self.settings
        
        
        self.device.conn.writeln("OUT {0:.6e}F".format(capacity))            

        if self.settings["Comp"] == "off":
            self.device.conn.writeln("ZCOMP NONE")            
        elif self.settings["Comp"] == "2 wire":
            self.device.conn.writeln("ZCOMP WIRE2")            
        elif self.settings["Comp"] == "4 wire":
            self.device.conn.writeln("ZCOMP WIRE4")
        else:
            raise n_support.SettingsError("Wrong Compensation setting")            
            
        to=n_support.TimeOut(10)
        self.device.conn.writeln("*OPC?")
        while to.is_timed_out() == False:
            answer_opc = self.device.conn.readln()
            if answer_opc == "1":
                to.set_timed_out()
            elif answer_opc == "0":
                self.device.conn.writeln("*OPC?")

        # process errors caused by trial to change compensation

        err_code = int(self.device.procError().split(",")[0])                
        while err_code!=0:
            if err_code == 539:
                self.settings["Comp"] = "off"
            elif err_code == 548:    
                self.settings["Comp"] = "off"
            
            err_code = int(self.device.procError().split(",")[0])              
            
        if self.device.conn.readln("oper?") == "0":
            self.device.conn.writeln("oper")
            to=n_support.TimeOut(10)
            self.device.conn.writeln("*OPC?")
            while to.is_timed_out() == False:
                answer_opc = self.device.conn.readln()                
                if answer_opc == "1":
                    to.set_timed_out()
                elif answer_opc == "0":
                    self.device.conn.writeln("*OPC?")
            
        if self.device.conn.readln("oper?") == "0":
            raise n_support.OutputError("Kalibrator bleibt nicht betriebsbereit")            
            
        answer_range = self.device.conn.readln("range?").split(",")
        answer_out =self.device.conn.readln("out?").split(",")
        out_value = float(answer_out[0])
        range_names={
                    "C500PF" : 4.9e-9 ,
                    "C1_1NF" : 1.09e-9 ,
                    "C3_3NF": 3.29e-9 ,
                    "C11NF": 1.09e-8 ,
                    "C33NF": 3.29e-8 ,
                    "C110NF": 1.09e-7 ,
                    "C330NF": 3.29e-7 ,
                    "C1_1UF" : 1.09e-6 ,
                    "C3_3UF": 3.29e-6 ,
                    "C11UF": 1.09e-5 ,
                    "C33UF": 3.29e-5 ,
                    "C110UF": 1.09e-4 ,
                    "C330UF": 3.29e-4 ,
                    "C1_1MF" : 1.09e-3 ,
        }
        used_range = range_names[answer_range[0]]
        self.last.value = out_value
        self.last.frequency = None        
        self.last.unc_of_drift = 0.5 * self.uncertainty(
                out_value, used_range, self.settings)            
        self.last.correction = 0
        self.last.unc_of_correction = 0
        self.last.settings = self.settings
        self.last.meas_range = used_range        
        self.last.el_properties = self.get_el_properties(used_range, self.settings)
            
        return out_value        


class Thermocouple(fct):    
    
    def __init__(self,device):
        super(Thermocouple,self).__init__(device)
        self.settings = {
                    c_fct.Function : c_fct.thermocouple,
                    }
                    
        self.el_properties = {}

        self.ranges = {
                    "_format": "Thermo",
                    "J": {"min" : -210., "max": 1200.},
                    "K": {"min" : -200., "max": 1372.},
                    "S": {"min" : 0., "max": 1767.},
                    "T": {"min" : -250., "max": 400.},
                    "X": {"min" : -0.33, "max": 0.33}
                    }                    

        self.baseSpec1yr = dict()
        self.baseSpec1yr["_format"] = "Thermo"
        self.baseSpec1yr["J"]={
                        "Tinterval" : [-210., -100., -30., 150., 760., 1200.],
                        "specs": 
                            [
                                { "fix" : 0.27},
                                { "fix" : 0.16},
                                { "fix" : 0.14},
                                { "fix" : 0.17},
                                { "fix" : 0.23},
                            ]
                        }
        self.baseSpec1yr["K"]={
                        "Tinterval" : [-200., -100., -25., 120., 1000., 1372.],
                        "specs": 
                            [
                                { "fix" : 0.33},
                                { "fix" : 0.18},
                                { "fix" : 0.16},
                                { "fix" : 0.26},
                                { "fix" : 0.40},
                            ]
                        }
        self.baseSpec1yr["S"]={
                        "Tinterval" : [0., 250., 1000., 1400., 1767.],
                        "specs": 
                            [
                                { "fix" : 0.47},
                                { "fix" : 0.36},
                                { "fix" : 0.37},
                                { "fix" : 0.46},
                            ]
                        }
        self.baseSpec1yr["T"]={
                        "Tinterval" : [-250., -150., 0., 120., 400.],
                        "specs": 
                            [
                                { "fix" : 0.63},
                                { "fix" : 0.24},
                                { "fix" : 0.16},
                                { "fix" : 0.14},
                            ]
                        }
        self.baseSpec1yr["X"]={
                        "Tinterval" : [-0.33, 0.33],
                        "specs": 
                            [
                                { "p%" : 0.006, "fixu" : 3},
                            ]
                        }

                        
    def get_el_properties(self, range_used, settings):
        # currently we have no model parameter
        # function is not well documented
        return self.el_properties


    def uncertainty(self, value, sensor_type):
        spec = self.baseSpec1yr[sensor_type]

        if sensor_type == "X":
            return (abs(value)*spec["specs"][0]["p%"] * 10e-6/ 100 + spec["specs"][0]["fixu"]*1e-6)

        if value < spec["Tinterval"][0] or value > spec["Tinterval"][-1]:        
            raise n_support.OutOfRange("Temperature {:f} is out of range".format(value))

        k1 = 1
        stop = False
        lo_index =None
        while not stop:
            if value <= spec["Tinterval"][k1]:
                lo_index = k1-1
                stop =True
            else:
                k1 += 1

        return spec["specs"][lo_index]["fix"]        
                            
    
    def stimulate(self, temperature, sensor_type):
        if not self.device.active_settings is self.settings:
            self.device.standby()
            self.device.active_settings = self.settings
        
        
        if sensor_type == "X":            
            self.device.conn.writeln("TSENS_TYPE TC")            
            self.device.conn.writeln("TCREF INT")            
            self.device.conn.writeln("TC_TYPE X")
            self.device.conn.writeln("OUT {0:.6e}CEL".format(temperature / 10e-6))
        else:       
            self.device.conn.writeln("TSENS_TYPE TC")            
            self.device.conn.writeln("TCREF INT")            
            self.device.conn.writeln("TC_TYPE {:1s}".format(sensor_type))
            self.device.conn.writeln("OUT {0:.6e}CEL".format(temperature))            

        to=n_support.TimeOut(10)
        self.device.conn.writeln("*OPC?")
        while to.is_timed_out() == False:
            answer_opc = self.device.conn.readln()
            if answer_opc == "1":
                to.set_timed_out()
            elif answer_opc == "0":
                self.device.conn.writeln("*OPC?")

        if self.device.conn.readln("oper?") == "0":
            self.device.conn.writeln("oper")
            to=n_support.TimeOut(10)
            self.device.conn.writeln("*OPC?")
            while to.is_timed_out() == False:
                answer_opc = self.device.conn.readln()                
                if answer_opc == "1":
                    to.set_timed_out()
                elif answer_opc == "0":
                    self.device.conn.writeln("*OPC?")
            
        if self.device.conn.readln("oper?") == "0":
            raise n_support.OutputError("Kalibrator bleibt nicht betriebsbereit")            
            
        sensor_type = self.device.conn.readln("TC_TYPE?")
        answer_out =self.device.conn.readln("out?").split(",")
        out_value = float(answer_out[0])
        used_range = sensor_type
        if sensor_type == "X":
            self.last.value = out_value * 10e-6
        else:
            self.last.value = out_value
        self.last.frequency = None        
        self.last.unc_of_drift = 0.5 * self.uncertainty(
                out_value, sensor_type)            
        self.last.correction = 0
        self.last.unc_of_correction = 0
        self.last.settings = self.settings
        self.last.meas_range = used_range        
        self.last.el_properties = self.get_el_properties(used_range, self.settings)
            
        return out_value        

    

class device(object):
    """Interaction object with 8846 multimeter connected via RS232"""

    def __init__(self):
        self.conn = None
        self.active_settings = None
        self.serial_number = ""
        self.volt_ac = Volt_AC(self)
        self.volt_dc = Volt_DC(self)
        self.cur_ac = Cur_AC(self)
        self.cur_dc = Cur_DC(self)
        self.res = Res(self)    
        self.cap = Cap(self)
        self.thermocouple = Thermocouple(self)


    def connect(self, device=c_dev.fluke_5500E_01, serial_number = "auto"):
        """open interface and identify device"""
        if c_exm.no_io in c_exm.execution_mode:
            self.serial_number = serial_number
            return
            
        self.conn = n_support.SerialDeviceConnection()
        self.conn.target = device
        
        self.conn.writeln("*rst;*CLS")  
        self.conn.writeln("*IDN?")  
        self.idn=self.conn.readln().split(",")
        if self.idn[0] != "FLUKE" or self.idn[1] != "5500E":
            raise Exception("Wrong device connected:" + self.idn.__str__())
        self.conn.writeln("Remote")        
        self.serial_number=self.idn[2]

        to=n_support.TimeOut(10)
        self.conn.writeln("*OPC?")
        while to.is_timed_out() == False:
            answer_opc = self.conn.readln()
            if answer_opc == "1":
                to.set_timed_out()
            elif answer_opc == "0":
                self.conn.writeln("*OPC?")
        pass
               
    def disconnect(self):
        if c_exm.no_io in c_exm.execution_mode:
            res = ""
        else:
            self.conn.writeln("stby;*wai;local;*STB?")
            while True:
                res=self.conn.readln()
                if res != "":
                    break
        self.active_settings = None
        return res
    
    def procError(self):
        if c_exm.no_io in c_exm.execution_mode:
            errInfo = ""
        else:
            self.conn.writeln("Err?")
            errInfo=self.conn.readln()
        return errInfo
        
    def standby(self):
        if c_exm.no_io not in c_exm.execution_mode:
            self.conn.writeln("STBY")
        self.active_settings = None

    def operate(self, execution_mode=set()):
        if c_exm.no_io not in execution_mode:
            self.conn.writeln("OPER")
        
    def lockRange(self):
        if c_exm.no_io in c_exm.execution_mode:
            raise Exception("Check usage for opimal simulation")
            locked = True
        else:
            self.conn.writeln("Rangelck on")
            locked = True
            err_msg = self.procError()
            err_code = int(err_msg.split(",")[0])                
            while err_code!=0:
                if err_code == 534:
                    locked =False
                err_msg = self.procError()
                err_code = int(err_msg.split(",")[0])
        
        return locked
        
    def unlockRange(self):
        if c_exm.no_io not in c_exm.execution_mode:
            self.conn.writeln("Rangelck off")


if __name__ == "__main__":
    import smt_cal_demo.utilities.easygui as eg
    dev=device()
    online = True
    try:
        dev.connect()
        online = True
    except:
        pass
    
    if online:
        dev.thermocouple.stimulate(0.1,"X")
        eg.msgbox("0.1 Volt Typ Volt Thermoelementemulation")
        raise Exception()
        dev.thermocouple.stimulate(100,"K")
        eg.msgbox("100 Grad Typ K Thermoelement")
        dev.thermocouple.stimulate(20,"S")
        eg.msgbox("20 Grad Typ S Thermoelement")
        dev.volt_ac.stimulate(10,10e3)
        eg.msgbox("10V 10kHZ")
        dev.volt_dc.stimulate(10)
        eg.msgbox("10V DC")
        dev.lockRange()
        dev.volt_dc.stimulate(1)
        eg.msgbox("1V DC range locked")
        dev.unlockRange()
        dev.res.stimulate(10e3)
        eg.msgbox("10 kOhm")
        dev.cap.stimulate(1e-6)
        eg.msgbox("1 uF")
        eg.msgbox("Rewire for current test")
        dev.cur_ac.stimulate(1e-3, 1e3)
        eg.msgbox("1 mA 1 kHz")
        dev.cur_dc.stimulate(1e-3)
        eg.msgbox("1 mA")
               
    