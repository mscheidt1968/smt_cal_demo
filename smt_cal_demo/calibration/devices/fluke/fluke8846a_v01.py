# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 13:15:56 2012

@author: Scheidt
"""

import unittest
import numpy as np
import smt_cal_demo.calibration.tokens.devices as c_dev
import smt_cal_demo.calibration.tokens.electrical_properties as c_el
import smt_cal_demo.calibration.tokens.device_functions as c_fct
import smt_cal_demo.calibration.tokens.physical_units as c_phy
import smt_cal_demo.calibration.devices.support as n_support
import smt_cal_demo.calibration.tokens.execution_modes as c_exm
from smt_cal_demo.calibration.models.support_v01 import Var

c_Filter = "Filter"
c_Filters_3Hz = "3Hz"
c_Filters_20Hz = "20Hz"
c_Filters_200Hz = "200Hz"


class MeasurementDesc(object):

    def __init__(self):
        self.values = None
        self.value = None
        self.unc_of_value = None
        self.meas_ranges = None
        self.settings = None
        self.correction = 0
        self.unc_of_correction= 0
        self.frequency = None
        self.el_properties = None
        self.dispcorr = 0
        self.unc_of_dispcorr = 0
        self.drift = 0
        self.unc_of_drift = 0
    
    def calc_value(self,values):
        self.values = values
        self.value = np.mean(values)
        if len(values) < 3:
            # no statistics reasonable
            self.unc_of_value = 0
        else:
            self.unc_of_value = np.std(values, ddof=1)
            
        
class fct(object):
    
    
    def __init__(self,device):
        self.last = None
        self.device = device  #links to device data
        self.settings = dict()

    def activate(self):
        """ call this to prepare instrument to measure with the current settings """
        #switches system to measuring functionality
        #has to be called when setting where modified
        self.device.active_settings=self.settings
        pass
        
    def measure(self):
        """ returns a current value """
        if not self.device.active_settings is self.settings:
            self.activate()
        #returns a current value from device
        if self.device.simulation == True:
            value = self.simulation_fct(self)
        return value 
        
    def correction(self,value,settings):
        """ get a correction for this value with its uncertainty """
        return [0,0]
        
    def correct(self, value, settings):
        """ just applies correction to the current value """
        return value + self.correction(value, settings)
        
    def uncertainty(self,value,settings):
        #
        pass

    
class Volt_AC(fct):
    
    

    def __init__(self,device):
        super(Volt_AC,self).__init__(device)
        self.settings={c_fct.Function : c_fct.volt_ac,
                  c_Filter : c_Filters_20Hz,
                  }
        self.el_properties = {
                            c_el.C_p : Var(100e-12, 0.289 * 2 * 50e-12,c_phy.F ,"Capacity parallel to input" ),
                            c_el.R_p : Var(1e6, 2e-2 * 1e6,c_phy.Ohm ,"Resistance parallel to input" )
                        }
        self.ranges={
                        c_fct.range_100m : {"min" : 0.001, "max" : 0.1, "res": 100e-9},
                        c_fct.range_1 : {"min" : 0.01, "max" : 1, "res": 1e-6}, 
                        c_fct.range_10 : {"min" : 0.1, "max" : 10, "res": 10e-6}, 
                        c_fct.range_100 : {"min" : 1, "max" : 100, "res": 100e-6}, 
                        c_fct.range_1k : {"min" : 10, "max" : 1000, "res": 1e-3}, 
                    }
            
        self.baseSpec1yr={
                    c_fct.range_100m : { "finterval" : [3, 5, 10, 20e3, 50e3, 100e3, 300e3],
                              "specs": 
                                [                            
                                    { "p%" : 1, "fix%Range" : 0.04},
                                    { "p%" : 0.35, "fix%Range" : 0.04},
                                    { "p%" : 0.06, "fix%Range" : 0.04},
                                    { "p%" : 0.12, "fix%Range" : 0.05},
                                    { "p%" : 0.6, "fix%Range" : 0.08},
                                    { "p%" : 4, "fix%Range" : 0.5}
                                ]
                            } ,
                    c_fct.range_1 :   { "finterval" : [3, 5, 10, 20e3, 50e3, 100e3, 300e3],
                              "specs":
                                [
                                    { "p%" : 1, "fix%Range" : 0.03},
                                    { "p%" : 0.35, "fix%Range" : 0.03},
                                    { "p%" : 0.06, "fix%Range" : 0.03},
                                    { "p%" : 0.12, "fix%Range" : 0.05},
                                    { "p%" : 0.6, "fix%Range" : 0.08},
                                    { "p%" : 4, "fix%Range" : 0.5}
                                ]
                            },
                    c_fct.range_10 : { "finterval" : [3, 5, 10, 20e3, 50e3, 100e3, 300e3],
                              "specs" : 
                                [   { "p%" : 1, "fix%Range" : 0.03},
                                    { "p%" : 0.35, "fix%Range" : 0.03},
                                    { "p%" : 0.06, "fix%Range" : 0.03},
                                    { "p%" : 0.12, "fix%Range" : 0.05},
                                    { "p%" : 0.6, "fix%Range" : 0.08},
                                    { "p%" : 4, "fix%Range" : 0.5}
                                ]
                            } ,
                    c_fct.range_100 : { "finterval" : [3, 5, 10, 20e3, 50e3, 100e3, 300e3],
                              "specs" : 
                                [   { "p%" : 1, "fix%Range" : 0.03},
                                    { "p%" : 0.35, "fix%Range" : 0.03},
                                    { "p%" : 0.06, "fix%Range" : 0.03},
                                    { "p%" : 0.12, "fix%Range" : 0.05},
                                    { "p%" : 0.6, "fix%Range" : 0.08},
                                    { "p%" : 4, "fix%Range" : 0.5}
                                ]
                            } ,
                    c_fct.range_1k : { "finterval" : [3, 5, 10, 20e3, 50e3, 100e3, 300e3],
                              "specs" : 
                                [   { "p%" : 1, "fix%Range" : 0.0225},
                                    { "p%" : 0.35, "fix%Range" : 0.0225},
                                    { "p%" : 0.06, "fix%Range" : 0.0225},
                                    { "p%" : 0.12, "fix%Range" : 0.0375},
                                    { "p%" : 0.6, "fix%Range" : 0.068},
                                    { "p%" : 4.0, "fix%Range" : 0.375}
                                ]
                            }
                    }

    def get_el_properties(self, range_used, settings):
        return self.el_properties

    def activate(self):
        #switches system to measuring functionality
        #has to be called when setting where modified
        filter = None
        if self.settings[c_Filter] == c_Filters_3Hz:
            filter = 3
        elif self.settings[c_Filter] == c_Filters_20Hz:
            filter = 20
        elif self.settings[c_Filter] == c_Filters_200Hz:
            filter = 200
        
        self.device.conn.writeln("Conf:Volt:AC Def,Min")
        self.device.conn.writeln("Volt:AC:Band {:d}".format(filter))
        self.device.active_settings = self.settings
        pass
        
        
    def measure(self, frequency = 50, set_range = None, count = 1):
        #returns a current value from device
        if not self.device.active_settings is self.settings:
            self.lastrange = None
            self.activate()

        range_switch = False
        if (self.lastrange is None) or (self.lastrange != set_range):
            range_switch = True
        self.lastrange = set_range             

        if self.device.simulation == True:
            values = self.simulation_fct(self)
        else:
            filter = None
            if self.settings[c_Filter] == c_Filters_3Hz:
                filter = 3
            elif self.settings[c_Filter] == c_Filters_20Hz:
                filter = 20
            elif self.settings[c_Filter] == c_Filters_200Hz:
                filter = 200

            self.device.conn.writeln("Volt:AC:Band {:d}".format(filter))

            if set_range == None:
                # measure with autorange
                self.device.conn.writeln("volt:ac:range:auto on")
            else:
                self.device.conn.writeln("volt:ac:range {:.6e}".format(set_range))
            
            if range_switch:
                self.device.conn.writeln("read?")
                to=n_support.TimeOut(10)
                while to.is_timed_out() == False:
                    answer = self.device.conn.readln()
                    if not answer == "":
                        to.set_timed_out()
                
                
            values = list()
            used_ranges = list()
            for k1 in range(count):
                self.device.conn.writeln("read?")
                to=n_support.TimeOut(10)
                while to.is_timed_out() == False:
                    answer = self.device.conn.readln()
                    if not answer == "":
                        to.set_timed_out()
                if answer == "":
                    raise n_support.MeasuringError("no result received")
                else:
                    values.append(float(answer))
                    used_ranges.append(float(self.device.conn.readln("volt:ac:range?")))
                pass
            self.device.conn.timeout = 1

        self.last = MeasurementDesc()        
        self.last.calc_value(values)
        self.last.frequency = frequency    
        self.last.meas_ranges = used_ranges
        self.last.settings = self.settings
        self.last.correction = 0
        self.last.unc_of_correction = 0
        self.last.drift = 0
        self.last.unc_of_drift = 0.5 * self.uncertainty( 
                                    self.last.value, frequency , 
                                    used_ranges[-1], self.settings)
        self.last.el_properties = self.get_el_properties(used_ranges[-1], self.settings)
        
        return self.last.value 
        
    def correction(self, value, frequency, settings):
        """ get a correction for this value with its uncertainty """
        return [0,0]
        
    def uncertainty(self, value, frequency, range_used, settings):
        #
        avalue = abs(value)
        if range_used is None:
            range_of_value = n_support.find_rangeAC(
                                avalue, frequency, self.ranges)
        else:
            range_of_value = n_support.find_rangeAC(
                                range_used, frequency, self.ranges)
        maxvalue_of_range = self.ranges[range_of_value]["max"]
        zw_uncertainty = n_support.uncertainty_from_AC_spec(
                            avalue, frequency, self.baseSpec1yr[range_of_value], maxvalue_of_range)
        if settings["Filter"] == "20Hz":
            if frequency <20 :
                zw_uncertainty += 0.25e-2 * avalue            
            elif frequency <40 :
                zw_uncertainty += 0.02e-2 * avalue            
            elif frequency <100 :
                zw_uncertainty += 0.01e-2 * avalue            
            pass
        elif settings["Filter"] == "200Hz":
            if frequency <40 :
                raise n_support.UnspecifiedMeasurementError("Frequency with this filter option must be >40Hz")            
            elif frequency <100 :
                zw_uncertainty += 0.55e-2 * avalue            
            elif frequency <200 :
                zw_uncertainty += 0.2e-2 * avalue            
            elif frequency <1000 :
                zw_uncertainty += 0.02e-2 * avalue            
            pass                
        pass

        if avalue < 0.01 * maxvalue_of_range:
            raise n_support.UnspecifiedMeasurementError("AC voltage must be larger than 1% of range")
        if avalue < 0.05 * maxvalue_of_range:
            if frequency < 50e3 :
                zw_uncertainty += maxvalue_of_range * 0.1e-2
            elif frequency < 100e3 :
                zw_uncertainty += maxvalue_of_range * 0.13e-2
            else:
                raise n_support.UnspecifiedMeasurementError(
                         "AC voltage frequency must be lower than 100kHz")
        return zw_uncertainty       



class Volt_DC(fct):

    
    def __init__(self,device):
        super(Volt_DC,self).__init__(device)
        self.lastrange = None
        self.settings={c_fct.Function : c_fct.volt_dc,
                  c_fct.NPLC : 10,
                  }
        self.ranges={ 
                        c_fct.range_100m : {"min" : 0, "max" : 0.1, "res": 1e-9},
                        c_fct.range_1 : {"min" : 0, "max" : 1, "res": 1e-6}, 
                        c_fct.range_10 : {"min" : 0, "max" : 10, "res": 10e-6}, 
                        c_fct.range_100 : {"min" : 0, "max" : 100, "res": 100e-6}, 
                        c_fct.range_1k : {"min" : 0, "max" : 1000, "res": 1e-3}, 
                    }
        self.baseSpec1yr={
                        c_fct.range_100m : {"p%" : 0.0037, "fix%Range" : 0.0035},
                        c_fct.range_1 : {"p%" : 0.0025, "fix%Range" : 0.0007},
                        c_fct.range_10 : {"p%" : 0.0024, "fix%Range" : 0.0005},
                        c_fct.range_100 : {"p%" : 0.0038, "fix%Range" : 0.0006},
                        c_fct.range_1k : {"p%" : 0.0041, "fix%Range" : 0.001},
                    }
        self.el_properties_lo_z = {
                            c_el.R_p : Var(10e6, 1e-2 * 10e6,c_phy.Ohm ,"Resistance parallel to input" )
                        }
        self.el_properties_hi_z = {
                            c_el.R_p : Var(10e9, 10e-2 * 10e9,c_phy.Ohm ,"Resistance parallel to input" )
                        }


    def get_el_properties(self, range_used, settings):
        return self.el_properties_lo_z

    def activate(self):
        #switches system to measuring functionality
        #has to be called when setting where modified
        
        nplc = 10
        if self.settings[c_fct.NPLC] <= 0.02:
            nplc = 0.02
        elif self.settings[c_fct.NPLC] <= 0.2:
            nplc = 0.2
        elif self.settings[c_fct.NPLC] <= 1:
            nplc = 1
        elif self.settings[c_fct.NPLC] <= 10:
            nplc = 10
        else:
            nplc = 100
            
        self.settings[c_fct.NPLC] = nplc
        self.device.conn.writeln("Conf:Volt:DC 1000,Min")
        self.device.conn.writeln("Volt:DC:NPLC {:f}".format(nplc))
        self.device.active_settings = self.settings
        pass

    def measure(self, set_range = None, count = 1):
        #returns a current value from device
        if not self.device.active_settings is self.settings:
            self.lastrange = None
            self.activate()

        range_switch = False
        if (self.lastrange is None) or (self.lastrange != set_range):
            range_switch = True
        self.lastrange = set_range             

            
        if self.device.simulation == True:
            values = self.simulation_fct(self)
        else:
            nplc = 10
            if self.settings[c_fct.NPLC] <= 0.02:
                nplc = 0.02
            elif self.settings[c_fct.NPLC] <= 0.2:
                nplc = 0.2
            elif self.settings[c_fct.NPLC] <= 1:
                nplc = 1
            elif self.settings[c_fct.NPLC] <= 10:
                nplc = 10
            else:
                nplc = 100
                
            self.settings[c_fct.NPLC] = nplc
            self.device.conn.writeln("volt:dc:NPLC {:f}".format(nplc))

            if set_range == None:
                # measure with autorange
                self.device.conn.writeln("volt:dc:range:auto on")
            else:
                self.device.conn.writeln("volt:dc:range {:.6e}".format(set_range*1.1))

            if range_switch:
                self.device.conn.writeln("read?")
                to=n_support.TimeOut(10)
                while to.is_timed_out() == False:
                    answer = self.device.conn.readln()
                    if not answer == "":
                        to.set_timed_out()
                
            values = list()
            used_ranges = list()
            
            for k1 in range(count):
                self.device.conn.writeln("read?")
                to=n_support.TimeOut(10)
                while to.is_timed_out() == False:                
                    answer = self.device.conn.readln()
                    if not answer == "":
                        to.set_timed_out()
                if answer == "":
                    raise n_support.MeasuringError("no result received")
                else:
                    values.append(float(answer))
                    used_ranges.append(float(self.device.conn.readln("volt:dc:range?")))
                pass
        
        self.last = MeasurementDesc()        
        self.last.calc_value(values)
        self.last.frequency = None    
        self.last.meas_ranges = used_ranges
        self.last.settings = self.settings
        self.last.correction = 0
        self.last.unc_of_correction = 0
        self.last.drift = 0
        self.last.unc_of_drift = 0.5 * self.uncertainty( 
                                    self.last.value, 
                                    used_ranges[-1], self.settings)
        self.last.el_properties = self.get_el_properties(used_ranges[-1], self.settings)
        return self.last.value 

    def correction(self, value, settings):
        """ get a correction for this value with its uncertainty """
        return [0,0]
        
    def uncertainty(self, value, range_used, settings):
        #
        avalue = abs(value)
        if range_used is None:
            range_of_value = n_support.find_range(
                                avalue, self.ranges)
        else:
            range_of_value = n_support.find_range(
                                range_used, self.ranges)
        maxvalue_of_range = self.ranges[range_of_value]["max"]
        zw_uncertainty = n_support.uncertainty_from_spec(
                            avalue, self.baseSpec1yr[range_of_value], maxvalue_of_range)
        if settings["NPLC"] <= 0.02:
            zw_uncertainty += 0.017e-2 * maxvalue_of_range + 17e-6           
        elif settings["NPLC"] <= 0.2:
            zw_uncertainty += 0.0025e-2 * maxvalue_of_range + 12e-6           
        elif settings["NPLC"] <= 1:
            zw_uncertainty += 0.001e-2 * maxvalue_of_range           
        return zw_uncertainty       


class Cur_AC(fct):


    def __init__(self,device):
        super(Cur_AC,self).__init__(device)
        self.settings={c_fct.Function : c_fct.cur_ac,
                  c_Filter : c_Filters_20Hz,
                  }
        self.el_properties_100Ohm = {
                            c_el.C_p : Var(100e-12, 0.289 * 2 * 100e-12,c_phy.F ,"Capacity parallel to input (not specified)" ),
                            c_el.R_p : Var(100, 1e-2 * 100,c_phy.Ohm ,"Resistance parallel to input" )
                        }
        self.el_properties_1Ohm = {
                            c_el.C_p : Var(100e-12, 0.289 * 2 * 100e-12,c_phy.F ,"Capacity parallel to input (not specified)" ),
                            c_el.R_p : Var(1, 1e-2 * 1,c_phy.Ohm ,"Resistance parallel to input" )
                        }
        self.el_properties_10mOhm = {
                            c_el.C_p : Var(100e-12, 0.289 * 2 * 100e-12,c_phy.F ,"Capacity parallel to input (not specified)" ),
                            c_el.R_p : Var(10e-3, 1e-2 * 10e-3,c_phy.Ohm ,"Resistance parallel to input" )
                        }
        self.ranges={
                        c_fct.range_100u : {"min" : 1e-6, "max" : 100e-6, "res": 100e-12},
                        c_fct.range_1m : {"min" : 0.01e-3, "max" : 1e-3, "res": 1e-9}, 
                        c_fct.range_10m : {"min" : 0.1e-3, "max" : 10e-3, "res": 10e-9}, 
                        c_fct.range_100m : {"min" : 1e-3, "max" : 100e-3, "res": 100e-9}, 
                        c_fct.range_400m : {"min" : 4e-3, "max" : 400e-3, "res": 1e-6}, 
                        c_fct.range_1 : {"min" : 0.01, "max" : 1, "res": 1e-6}, 
                        c_fct.range_3 : {"min" : 0.03, "max" : 3, "res": 10e-6}, 
                        c_fct.range_10 : {"min" : 0.1, "max" : 10, "res": 10e-6}, 
                    }
        self.baseSpec1yr={
                    c_fct.range_100u : { "finterval" : [3, 5, 10, 5e3, 10e3],
                              "specs": 
                                [                            
                                    { "p%" : 1.1, "fix%Range" : 0.06},
                                    { "p%" : 0.35, "fix%Range" : 0.06},
                                    { "p%" : 0.15, "fix%Range" : 0.06},
                                    { "p%" : 0.35, "fix%Range" : 0.7},
                                ]
                            } ,
                    c_fct.range_1m : { "finterval" : [3, 5, 10, 5e3, 10e3],
                              "specs": 
                                [                            
                                    { "p%" : 1.0, "fix%Range" : 0.04},
                                    { "p%" : 0.3, "fix%Range" : 0.04},
                                    { "p%" : 0.1, "fix%Range" : 0.04},
                                    { "p%" : 0.2, "fix%Range" : 0.25},
                                ]
                            } ,
                    c_fct.range_10m : { "finterval" : [3, 5, 10, 5e3, 10e3],
                              "specs": 
                                [                            
                                    { "p%" : 1.1, "fix%Range" : 0.06},
                                    { "p%" : 0.35, "fix%Range" : 0.06},
                                    { "p%" : 0.15, "fix%Range" : 0.06},
                                    { "p%" : 0.35, "fix%Range" : 0.7},
                                ]
                            } ,
                    c_fct.range_100m : { "finterval" : [3, 5, 10, 5e3, 10e3],
                              "specs": 
                                [                            
                                    { "p%" : 1.0, "fix%Range" : 0.04},
                                    { "p%" : 0.3, "fix%Range" : 0.04},
                                    { "p%" : 0.1, "fix%Range" : 0.04},
                                    { "p%" : 0.2, "fix%Range" : 0.25},
                                ]
                            } ,
                    c_fct.range_400m : { "finterval" : [3, 5, 10, 5e3, 10e3],
                              "specs": 
                                [                            
                                    { "p%" : 1.0, "fix%Range" : 0.1},
                                    { "p%" : 0.3, "fix%Range" : 0.1},
                                    { "p%" : 0.1, "fix%Range" : 0.1},
                                    { "p%" : 0.2, "fix%Range" : 0.7},
                                ]
                            } ,
                    c_fct.range_1 : { "finterval" : [3, 5, 10, 5e3, 10e3],
                              "specs": 
                                [                            
                                    { "p%" : 1.0, "fix%Range" : 0.04},
                                    { "p%" : 0.3, "fix%Range" : 0.04},
                                    { "p%" : 0.1, "fix%Range" : 0.04},
                                    { "p%" : 0.35, "fix%Range" : 0.7},
                                ]
                            } ,
                    c_fct.range_3 : { "finterval" : [3, 5, 10, 5e3, 10e3],
                              "specs": 
                                [                            
                                    { "p%" : 1.1, "fix%Range" : 0.06},
                                    { "p%" : 0.35, "fix%Range" : 0.06},
                                    { "p%" : 0.15, "fix%Range" : 0.06},
                                    { "p%" : 0.35, "fix%Range" : 0.7},
                                ]
                            } ,
                    c_fct.range_10 : { "finterval" : [3, 5, 10, 5e3, 10e3],
                              "specs": 
                                [                            
                                    { "p%" : 1.1, "fix%Range" : 0.06},
                                    { "p%" : 0.35, "fix%Range" : 0.06},
                                    { "p%" : 0.15, "fix%Range" : 0.06},
                                    { "p%" : 0.35, "fix%Range" : 0.7},
                                ]
                            } 
                    }


    def get_el_properties(self, range_used, settings):
        if range_used<=1e-3:
            return self.el_properties_100Ohm
        elif range_used<=400e-3:
            return self.el_properties_1Ohm
        return self.el_properties_10mOhm

    def activate(self):
        #switches system to measuring functionality
        #has to be called when setting where modified
        filter = None
        if self.settings[c_Filter] == c_Filters_3Hz:
            filter = 3
        elif self.settings[c_Filter] == c_Filters_20Hz:
            filter = 20
        elif self.settings[c_Filter] == c_Filters_200Hz:
            filter = 200
        
        self.device.conn.writeln("Conf:Curr:AC Def,Min")
        self.device.conn.writeln("Curr:AC:Band {:d}".format(filter))
        self.device.active_settings = self.settings
        pass
        
    def measure(self, frequency = 50, set_range = None, count = 1):
        #returns a current value from device
        if not self.device.active_settings is self.settings:
            self.lastrange = None
            self.activate()

        range_switch = False
        if (self.lastrange is None) or (self.lastrange != set_range):
            range_switch = True
        self.lastrange = set_range             
            
        if self.device.simulation == True:
            values = self.simulation_fct(self)
        else:
            filter = None
            if self.settings[c_Filter] == c_Filters_3Hz:
                filter = 3
            elif self.settings[c_Filter] == c_Filters_20Hz:
                filter = 20
            elif self.settings[c_Filter] == c_Filters_200Hz:
                filter = 200
            
            self.device.conn.writeln("Curr:AC:Band {:d}".format(filter))

            if set_range == None:
                # measure with autorange
                self.device.conn.writeln("curr:ac:range:auto on")
            else:
                self.device.conn.writeln("curr:ac:range {:.6e}".format(set_range))
                
            if range_switch:
                self.device.conn.writeln("read?")
                to=n_support.TimeOut(10)
                while to.is_timed_out() == False:
                    answer = self.device.conn.readln()
                    if not answer == "":
                        to.set_timed_out()

            values = list()
            used_ranges = list()
            
            for k1 in range(count):
                self.device.conn.writeln("read?")
                to=n_support.TimeOut(10)
                while to.is_timed_out() == False:
                    answer = self.device.conn.readln()
                    if not answer == "":
                        to.set_timed_out()
                if answer == "":
                    raise n_support.MeasuringError("no result received")
                else:
                    values.append(float(answer))
                    used_ranges.append(float(self.device.conn.readln("curr:ac:range?")))
                pass
            self.device.conn.timeout = 1
        
        self.last = MeasurementDesc()        
        self.last.calc_value(values)
        self.last.frequency = frequency    
        self.last.meas_ranges = used_ranges
        self.last.settings = self.settings
        self.last.correction = 0
        self.last.unc_of_correction = 0
        self.last.drift = 0
        self.last.unc_of_drift = 0.5 * self.uncertainty( 
                                    self.last.value, frequency , 
                                    used_ranges[-1], self.settings)
        self.last.el_properties = self.get_el_properties(used_ranges[-1], self.settings)
        return self.last.value 
        
    def correction(self, value, frequency, settings):
        """ get a correction for this value with its uncertainty """
        return [0,0]
        
    def uncertainty(self, value, frequency, range_used, settings):
        #
        avalue = abs(value)
        if range_used is None:
            range_of_value = n_support.find_rangeAC(
                                avalue, frequency, self.ranges)
        else:
            range_of_value = n_support.find_rangeAC(
                                range_used, frequency, self.ranges)
        maxvalue_of_range = self.ranges[range_of_value]["max"]
        zw_uncertainty = n_support.uncertainty_from_AC_spec(
                            avalue, frequency, self.baseSpec1yr[range_of_value], maxvalue_of_range)
        if settings[c_Filter] == c_Filters_20Hz:
            if frequency <20 :
                zw_uncertainty += 0.25e-2 * avalue            
            elif frequency <40 :
                zw_uncertainty += 0.02e-2 * avalue            
            elif frequency <100 :
                zw_uncertainty += 0.01e-2 * avalue            
            pass
        elif settings[c_Filter] == c_Filters_200Hz:
            if frequency <40 :
                raise n_support.UnspecifiedMeasurementError("Frequency with this filter option must be >40Hz")            
            elif frequency <100 :
                zw_uncertainty += 0.55e-2 * avalue            
            elif frequency <200 :
                zw_uncertainty += 0.2e-2 * avalue            
            elif frequency <1000 :
                zw_uncertainty += 0.02e-2 * avalue            
            pass                
        pass

        if avalue < 0.01 * maxvalue_of_range:
            raise n_support.UnspecifiedMeasurementError("AC current must be larger than 1% of range")
        if avalue < 0.05 * maxvalue_of_range:
            zw_uncertainty += maxvalue_of_range * 0.1e-2

        return zw_uncertainty       



class Cur_DC(fct):

    
    def __init__(self,device):
        super(Cur_DC,self).__init__(device)
        self.settings={c_fct.Function : c_fct.cur_dc,
                  c_fct.NPLC: 10,
                  }

        self.el_properties_100Ohm = {
                            c_el.R_p : Var(100, 1e-2 * 100,c_phy.Ohm ,"Resistance parallel to input" )
                        }
        self.el_properties_1Ohm = {
                            c_el.R_p : Var(1, 1e-2 * 1,c_phy.Ohm ,"Resistance parallel to input" )
                        }
        self.el_properties_10mOhm = {
                            c_el.R_p : Var(10e-3, 1e-2 * 10e-3,c_phy.Ohm ,"Resistance parallel to input" )
                        }

        self.ranges={
                        c_fct.range_100u : {"min" : 0, "max" : 100e-6, "res": 100e-12},
                        c_fct.range_1m : {"min" : 0, "max" : 1e-3, "res": 1e-9}, 
                        c_fct.range_10m : {"min" : 0, "max" : 10e-3, "res": 10e-9}, 
                        c_fct.range_100m : {"min" : 0, "max" : 100e-3, "res": 100e-9}, 
                        c_fct.range_400m : {"min" : 0, "max" : 400e-3, "res": 1e-6}, 
                        c_fct.range_1 : {"min" : 0, "max" : 1, "res": 1e-6}, 
                        c_fct.range_3 : {"min" : 0, "max" : 3, "res": 10e-6}, 
                        c_fct.range_10 : {"min" : 0, "max" : 10, "res": 10e-6}, 
                    }
        self.baseSpec1yr={
                        c_fct.range_100u : {"p%" : 0.05, "fix%Range" : 0.025},
                        c_fct.range_1m : {"p%" : 0.05, "fix%Range" : 0.005},
                        c_fct.range_10m : {"p%" : 0.05, "fix%Range" : 0.02},
                        c_fct.range_100m : {"p%" : 0.05, "fix%Range" : 0.005},
                        c_fct.range_400m : {"p%" : 0.05, "fix%Range" : 0.005},
                        c_fct.range_1 : {"p%" : 0.05, "fix%Range" : 0.02},
                        c_fct.range_3 : {"p%" : 0.1, "fix%Range" : 0.02},
                        c_fct.range_10 : {"p%" : 0.15, "fix%Range" : 0.008},
                    }

    def get_el_properties(self, range_used, settings):
        if range_used<=1e-3:
            return self.el_properties_100Ohm
        elif range_used<=400e-3:
            return self.el_properties_1Ohm
        return self.el_properties_10mOhm

    def activate(self):
        #switches system to measuring functionality
        #has to be called when setting where modified
        
        nplc = 10
        if self.settings[c_fct.NPLC] <= 0.02:
            nplc = 0.02
        elif self.settings[c_fct.NPLC] <= 0.2:
            nplc = 0.2
        elif self.settings[c_fct.NPLC] <= 1:
            nplc = 1
        elif self.settings[c_fct.NPLC] <= 10:
            nplc = 10
        else:
            nplc = 100
            
        self.settings[c_fct.NPLC] = nplc
        
        self.device.conn.writeln("Conf:Curr:DC def,Min")
        self.device.conn.writeln("Curr:DC:NPLC {:f}".format(nplc))
        self.device.active_settings = self.settings
        pass

    def measure(self, set_range = None, count = 1):
        #returns a current value from device
        if not self.device.active_settings is self.settings:
            self.lastrange = None
            self.activate()

        range_switch = False
        if (self.lastrange is None) or (self.lastrange != set_range):
            range_switch = True
        self.lastrange = set_range             
            
        if self.device.simulation == True:
            values = self.simulation_fct(self)
        else:
            nplc = 10
            if self.settings[c_fct.NPLC] <= 0.02:
                nplc = 0.02
            elif self.settings[c_fct.NPLC] <= 0.2:
                nplc = 0.2
            elif self.settings[c_fct.NPLC] <= 1:
                nplc = 1
            elif self.settings[c_fct.NPLC] <= 10:
                nplc = 10
            else:
                nplc = 100
                
            self.settings[c_fct.NPLC] = nplc
            self.device.conn.writeln("Curr:DC:NPLC {:f}".format(nplc))
            if set_range == None:
                # measure with autorange
                self.device.conn.writeln("curr:dc:range:auto on")
            else:
                self.device.conn.writeln("curr:dc:range {:.6e}".format(set_range))

            if range_switch:
                self.device.conn.writeln("read?")
                to=n_support.TimeOut(10)
                while to.is_timed_out() == False:
                    answer = self.device.conn.readln()
                    if not answer == "":
                        to.set_timed_out()
                
            values = list()
            used_ranges = list()
            for k1 in range(count):
                self.device.conn.writeln("read?")
                to=n_support.TimeOut(10)
                while to.is_timed_out() == False:                
                    answer = self.device.conn.readln()
                    if not answer == "":
                        to.set_timed_out()
                if answer == "":
                    raise n_support.MeasuringError("no result received")
                else:
                    values.append(float(answer))
                    used_ranges.append(float(self.device.conn.readln("curr:dc:range?")))
                pass
        
        self.last = MeasurementDesc()        
        self.last.calc_value(values)
        self.last.frequency = None    
        self.last.meas_ranges = used_ranges
        self.last.settings = self.settings
        self.last.correction = 0
        self.last.unc_of_correction = 0
        self.last.drift = 0
        self.last.unc_of_drift = 0.5 * self.uncertainty( 
                                    self.last.value, 
                                    used_ranges[-1], self.settings)
        self.last.el_properties = self.get_el_properties(used_ranges[-1], self.settings)
        return self.last.value 


    def sample(self, set_range = None, count = 1):
        #returns a current value from device
        if not self.device.active_settings is self.settings:
            self.lastrange = None
            self.activate()

        range_switch = False
        if (self.lastrange is None) or (self.lastrange != set_range):
            range_switch = True
        self.lastrange = set_range             
            
        nplc = 10
        if self.settings[c_fct.NPLC] <= 0.02:
            nplc = 0.02
        elif self.settings[c_fct.NPLC] <= 0.2:
            nplc = 0.2
        elif self.settings[c_fct.NPLC] <= 1:
            nplc = 1
        elif self.settings[c_fct.NPLC] <= 10:
            nplc = 10
        else:
            nplc = 100
            
        self.settings[c_fct.NPLC] = nplc
        self.device.conn.writeln("Curr:DC:NPLC {:f}".format(nplc))
        if set_range == None:
            # measure with autorange
            self.device.conn.writeln("curr:dc:range:auto on")
        else:
            self.device.conn.writeln("curr:dc:range {:.6e}".format(set_range))

        if range_switch:
            self.device.conn.writeln("read?")
            to=n_support.TimeOut(10)
            while to.is_timed_out() == False:
                answer = self.device.conn.readln()
                if not answer == "":
                    to.set_timed_out()
          

        self.device.conn.writeln('DATA:FEED RDG_STORE, "CALC"')
        self.device.conn.writeln('DISP off')
        self.device.conn.writeln('Curr:DC:NPLC 0.02')
        self.device.conn.writeln('zero:auto 0')
        self.device.conn.writeln('trig:sour imm')
        self.device.conn.writeln('trig:del 0')
        self.device.conn.writeln('trig:coun 1')

        self.device.conn.writeln("Sample:Count {:f}".format(count))
        self.device.conn.writeln(":INIT; *OPC?")
        to=n_support.TimeOut(100)
        while to.is_timed_out() == False:                
            answer = self.device.conn.readln()
            if not answer == "":
                to.set_timed_out()
        if answer == "":
            raise n_support.MeasuringError("no result received")

        self.device.conn.writeln('DISP on')


        self.device.conn.writeln("fetch?")
        to=n_support.TimeOut(10)
        while to.is_timed_out() == False:                
            answer = self.device.conn.readln()
            if not answer == "":
                to.set_timed_out()
        if answer == "":
            raise n_support.MeasuringError("no result received")

        samples = answer.split(",")

        self.device.conn.writeln("Sample:Count 1")
        self.settings[c_fct.NPLC] = nplc
        self.device.conn.writeln("Curr:DC:NPLC {:f}".format(nplc))
        self.device.conn.writeln('zero:auto 1')
        self.device.conn.writeln('trig:sour imm')
        self.device.conn.writeln('trig:del 3')
        self.device.conn.writeln('trig:coun 1')
          
        values = list()
        for sample in samples:
            values.append(float(sample))

        
        self.device.conn.writeln("Sample:Count 1")
        used_range = float(self.device.conn.readln("curr:dc:range?"))
        
        self.last = MeasurementDesc()        
        self.last.calc_value(values)
        self.last.frequency = None    
        self.last.meas_ranges = used_range
        self.last.settings = self.settings
        self.last.correction = 0
        self.last.unc_of_correction = 0
        self.last.drift = 0
        self.last.unc_of_drift = 0.5 * self.uncertainty( 
                                    self.last.value, 
                                    used_range, self.settings)
        self.last.el_properties = self.get_el_properties(used_range, self.settings)
        return self.last.values 


    def correction(self, value, settings):
        """ get a correction for this value with its uncertainty """
        return [0,0]
        
    def uncertainty(self, value, range_used, settings):
        #
        avalue = abs(value)
        if range_used is None:
            range_of_value = n_support.find_range(
                                avalue, self.ranges)
        else:
            range_of_value = n_support.find_range(
                                range_used, self.ranges)
        maxvalue_of_range = self.ranges[range_of_value]["max"]
        zw_uncertainty = n_support.uncertainty_from_spec(
                            avalue, self.baseSpec1yr[range_of_value], maxvalue_of_range)
        if settings["NPLC"] <= 0.02:
            zw_uncertainty += 0.017e-2 * maxvalue_of_range + 17e-6           
        elif settings["NPLC"] <= 0.2:
            zw_uncertainty += 0.0025e-2 * maxvalue_of_range + 12e-6           
        elif settings["NPLC"] <= 1:
            zw_uncertainty += 0.001e-2 * maxvalue_of_range           
        return zw_uncertainty       



class Res_2W(fct):

    
    def __init__(self,device):
        super(Res_2W,self).__init__(device)
        self.settings={c_fct.Function : c_fct.res_2w,
                  c_fct.NPLC : 10,
                  }
                  
        self.el_properties_5mA = {
                            c_el.I_meas : Var(5e-3, 1e-2 * 5e-3,c_phy.A ,"Measurement current" ),
                            c_el.R_p : Var(10e9, 10e-2 * 10e9,c_phy.Ohm ,"Resistance parallel to input" )
                        }
        self.el_properties_1mA = {
                            c_el.I_meas : Var(1e-3, 1e-2 * 1e-3,c_phy.A ,"Measurement current" ),
                            c_el.R_p : Var(10e9, 10e-2 * 10e9,c_phy.Ohm ,"Resistance parallel to input" )
                        }
        self.el_properties_100uA = {
                            c_el.I_meas : Var(100e-6, 1e-2 * 100e-6,c_phy.A ,"Measurement current" ),
                            c_el.R_p : Var(10e9, 10e-2 * 10e9,c_phy.Ohm ,"Resistance parallel to input" )
                        }
        self.el_properties_10uA = {
                            c_el.I_meas : Var(10e-6, 1e-2 * 10e-6,c_phy.A ,"Measurement current" ),
                            c_el.R_p : Var(10e9, 10e-2 * 10e9,c_phy.Ohm ,"Resistance parallel to input" )
                        }
        self.el_properties_1uA = {
                            c_el.I_meas : Var(1e-6, 1e-2 * 10e-6,c_phy.A ,"Measurement current" ),
                            c_el.R_p : Var(10e9, 10e-2 * 10e9,c_phy.Ohm ,"Resistance parallel to input" )
                        }
        self.el_properties_1uA10M = {
                            c_el.I_meas : Var(1e-6, 1e-2 * 10e-6,c_phy.A ,"Measurement current" ),
                            c_el.R_p : Var(10e6, 0.1e-2 * 10e6,c_phy.Ohm ,"Resistance parallel to input" )
                        }
                  
        self.ranges={ 
                        c_fct.range_10 : {"min" : 0, "max" : 10, "res": 10e-6},
                        c_fct.range_100 : {"min" : 0, "max" : 100, "res": 100e-6}, 
                        c_fct.range_1k : {"min" : 0, "max" : 1e3, "res": 1e-3}, 
                        c_fct.range_10k : {"min" : 0, "max" : 1e4, "res": 10e-3}, 
                        c_fct.range_100k : {"min" : 0, "max" : 1e5, "res": 100e-3}, 
                        c_fct.range_1M : {"min" : 0, "max" : 1e6, "res": 1}, 
                        c_fct.range_10M : {"min" : 0, "max" : 1e7, "res": 10}, 
                        c_fct.range_100M : {"min" : 0, "max" : 1e8, "res": 100}, 
                        c_fct.range_1G : {"min" : 0, "max" : 1e9, "res": 1e3}, 
                    }
        self.baseSpec1yr={
                        c_fct.range_10 : {"p%" : 0.01, "fix%Range" : 0.03},
                        c_fct.range_100 : {"p%" : 0.01, "fix%Range" : 0.004},
                        c_fct.range_1k : {"p%" : 0.01, "fix%Range" : 0.001},
                        c_fct.range_10k : {"p%" : 0.01, "fix%Range" : 0.001},
                        c_fct.range_100k : {"p%" : 0.01, "fix%Range" : 0.001},
                        c_fct.range_1M : {"p%" : 0.01, "fix%Range" : 0.001},
                        c_fct.range_10M : {"p%" : 0.04, "fix%Range" : 0.001},
                        c_fct.range_100M : {"p%" : 0.8, "fix%Range" : 0.01},
                        c_fct.range_1G : {"p%" : 2.0, "fix%Range" : 0.01},
                    }

    def get_el_properties(self, range_used, settings):
        if range_used<=10:
            return self.el_properties_5mA
        elif range_used<=1e3:
            return self.el_properties_1mA
        elif range_used<=1e5:
            return self.el_properties_100uA
        elif range_used<=1e6:
            return self.el_properties_10uA
        elif range_used<=1e7:
            return self.el_properties_1uA
        return self.el_properties_1uA10M


    def activate(self):
        #switches system to measuring functionality
        #has to be called when setting where modified
        
        nplc = 10
        if self.settings[c_fct.NPLC] <= 0.02:
            nplc = 0.02
        elif self.settings[c_fct.NPLC] <= 0.2:
            nplc = 0.2
        elif self.settings[c_fct.NPLC] <= 1:
            nplc = 1
        elif self.settings[c_fct.NPLC] <= 10:
            nplc = 10
        else:
            nplc = 100
            
        self.settings[c_fct.NPLC] = nplc
        self.device.conn.writeln("Conf:Res def,Min")
        self.device.conn.writeln("Res:NPLC {:f}".format(nplc))
        self.device.active_settings = self.settings
        pass

    def measure(self, set_range = None, count = 1):
        #returns a current value from device
        if not self.device.active_settings is self.settings:
            self.lastrange = None
            self.activate()

        range_switch = False
        if (self.lastrange is None) or (self.lastrange != set_range):
            range_switch = True
        self.lastrange = set_range             
            
        if self.device.simulation == True:
            values = self.simulation_fct(self)
        else:
            nplc = 10
            if self.settings[c_fct.NPLC] <= 0.02:
                nplc = 0.02
            elif self.settings[c_fct.NPLC] <= 0.2:
                nplc = 0.2
            elif self.settings[c_fct.NPLC] <= 1:
                nplc = 1
            elif self.settings[c_fct.NPLC] <= 10:
                nplc = 10
            else:
                nplc = 100
                
            self.settings[c_fct.NPLC] = nplc
            self.device.conn.writeln("Res:NPLC {:f}".format(nplc))

            if set_range == None:
                # measure with autorange
                self.device.conn.writeln("res:range:auto on")
            else:
                self.device.conn.writeln("res:range {:.6e}".format(set_range))

            if range_switch:
                self.device.conn.writeln("read?")
                to=n_support.TimeOut(10)
                while to.is_timed_out() == False:
                    answer = self.device.conn.readln()
                    if not answer == "":
                        to.set_timed_out()
                
            values = list()
            used_ranges = list()
            
            for k1 in range(count):
                self.device.conn.writeln("read?")
                to=n_support.TimeOut(10)
                while to.is_timed_out() == False:                
                    answer = self.device.conn.readln()
                    if not answer == "":
                        to.set_timed_out()
                if answer == "":
                    raise n_support.MeasuringError("no result received")
                else:
                    values.append(float(answer))
                    used_ranges.append(float(self.device.conn.readln("res:range?")))
                pass
        
        self.last = MeasurementDesc()        
        self.last.calc_value(values)
        self.last.frequency = None    
        self.last.meas_ranges = used_ranges
        self.last.settings = self.settings
        self.last.correction = 0
        self.last.unc_of_correction = 0
        self.last.drift = 0
        self.last.unc_of_drift = 0.5 * self.uncertainty( 
                                    self.last.value, 
                                    used_ranges[-1], self.settings)
        self.last.el_properties = self.get_el_properties(used_ranges[-1], self.settings)                
        return self.last.value 

    def correction(self, value, settings):
        """ get a correction for this value with its uncertainty """
        return [0,0]
        
    def uncertainty(self, value, range_used, settings):
        #
        avalue = abs(value)
        if range_used is None:
            range_of_value = n_support.find_range(
                                avalue, self.ranges)
        else:
            range_of_value = n_support.find_range(
                                range_used, self.ranges)
        maxvalue_of_range = self.ranges[range_of_value]["max"]
        zw_uncertainty = n_support.uncertainty_from_spec(
                            avalue, self.baseSpec1yr[range_of_value], maxvalue_of_range)
        if settings[c_fct.NPLC] <= 0.02:
            zw_uncertainty += 0.017e-2 * maxvalue_of_range + 15e-3           
        elif settings[c_fct.NPLC] <= 0.2:
            zw_uncertainty += 0.003e-2 * maxvalue_of_range + 7e-3           
        elif settings[c_fct.NPLC] <= 1:
            zw_uncertainty += 0.001e-2 * maxvalue_of_range           
        return zw_uncertainty       



class Res_4W(fct):


    def __init__(self,device):
        super(Res_4W,self).__init__(device)
        self.settings={c_fct.Function : c_fct.res_4w,
                  c_fct.NPLC : 10,
                  }

        self.el_properties_5mA = {
                            c_el.I_meas : Var(5e-3, 1e-2 * 5e-3,c_phy.A ,"Measurement current" ),
                            c_el.R_p : Var(10e9, 10e-2 * 10e9,c_phy.Ohm ,"Resistance parallel to input" )
                        }
        self.el_properties_1mA = {
                            c_el.I_meas : Var(1e-3, 1e-2 * 1e-3,c_phy.A ,"Measurement current" ),
                            c_el.R_p : Var(10e9, 10e-2 * 10e9,c_phy.Ohm ,"Resistance parallel to input" )
                        }
        self.el_properties_100uA = {
                            c_el.I_meas : Var(100e-6, 1e-2 * 100e-6,c_phy.A ,"Measurement current" ),
                            c_el.R_p : Var(10e9, 10e-2 * 10e9,c_phy.Ohm ,"Resistance parallel to input" )
                        }
        self.el_properties_10uA = {
                            c_el.I_meas : Var(10e-6, 1e-2 * 10e-6,c_phy.A ,"Measurement current" ),
                            c_el.R_p : Var(10e9, 10e-2 * 10e9,c_phy.Ohm ,"Resistance parallel to input" )
                        }
        self.el_properties_1uA = {
                            c_el.I_meas : Var(1e-6, 1e-2 * 1e-6,c_phy.A ,"Measurement current" ),
                            c_el.R_p : Var(10e9, 10e-2 * 10e9,c_phy.Ohm ,"Resistance parallel to input" )
                        }
        self.el_properties_1uA10M = {
                            c_el.I_meas : Var(1e-6, 1e-2 * 1e-6,c_phy.A ,"Measurement current" ),
                            c_el.R_p : Var(10e6, 0.1e-2 * 10e6,c_phy.Ohm ,"Resistance parallel to input" )
                        }
                  
        self.ranges={ 
                        c_fct.range_10 : {"min" : 0, "max" : 10, "res": 10e-6},
                        c_fct.range_100 : {"min" : 0, "max" : 100, "res": 100e-6}, 
                        c_fct.range_1k : {"min" : 0, "max" : 1e3, "res": 1e-3}, 
                        c_fct.range_10k : {"min" : 0, "max" : 1e4, "res": 10e-3}, 
                        c_fct.range_100k : {"min" : 0, "max" : 1e5, "res": 100e-3}, 
                        c_fct.range_1M : {"min" : 0, "max" : 1e6, "res": 1}, 
                        c_fct.range_10M : {"min" : 0, "max" : 1e7, "res": 10}, 
                        c_fct.range_100M : {"min" : 0, "max" : 1e8, "res": 100}, 
                        c_fct.range_1G : {"min" : 0, "max" : 1e9, "res": 1e3}, 
                    }
        self.baseSpec1yr={
                        c_fct.range_10 : {"p%" : 0.01, "fix%Range" : 0.03},
                        c_fct.range_100 : {"p%" : 0.01, "fix%Range" : 0.004},
                        c_fct.range_1k : {"p%" : 0.01, "fix%Range" : 0.001},
                        c_fct.range_10k : {"p%" : 0.01, "fix%Range" : 0.001},
                        c_fct.range_100k : {"p%" : 0.01, "fix%Range" : 0.001},
                        c_fct.range_1M : {"p%" : 0.01, "fix%Range" : 0.001},
                        c_fct.range_10M : {"p%" : 0.04, "fix%Range" : 0.001},
                        c_fct.range_100M : {"p%" : 0.8, "fix%Range" : 0.01},
                        c_fct.range_1G : {"p%" : 2.0, "fix%Range" : 0.01},
                    }


    def get_el_properties(self, range_used, settings):
        if range_used<=10:
            return self.el_properties_5mA
        elif range_used<=1e3:
            return self.el_properties_1mA
        elif range_used<=1e5:
            return self.el_properties_100uA
        elif range_used<=1e6:
            return self.el_properties_10uA
        elif range_used<=1e7:
            return self.el_properties_1uA
        return self.el_properties_1uA10M


    def activate(self):
        #switches system to measuring functionality
        #has to be called when setting where modified
        
        nplc = 10
        if self.settings[c_fct.NPLC] <= 0.02:
            nplc = 0.02
        elif self.settings[c_fct.NPLC] <= 0.2:
            nplc = 0.2
        elif self.settings[c_fct.NPLC] <= 1:
            nplc = 1
        elif self.settings[c_fct.NPLC] <= 10:
            nplc = 10
        else:
            nplc = 100
            
        self.settings[c_fct.NPLC] = nplc
        self.device.conn.writeln("Conf:FRes def,Min")
        self.device.conn.writeln("FRes:NPLC {:f}".format(nplc))
        self.device.active_settings = self.settings
        pass

    def measure(self, set_range = None, count = 1):
        #returns a current value from device
        if not self.device.active_settings is self.settings:
            self.lastrange = None
            self.activate()

        range_switch = False
        if (self.lastrange is None) or (self.lastrange != set_range):
            range_switch = True
        self.lastrange = set_range             
            
        if self.device.simulation == True:
            values = self.simulation_fct(self)
        else:
            nplc = 10
            if self.settings[c_fct.NPLC] <= 0.02:
                nplc = 0.02
            elif self.settings[c_fct.NPLC] <= 0.2:
                nplc = 0.2
            elif self.settings[c_fct.NPLC] <= 1:
                nplc = 1
            elif self.settings[c_fct.NPLC] <= 10:
                nplc = 10
            else:
                nplc = 100
                
            self.settings[c_fct.NPLC] = nplc
            self.device.conn.writeln("FRes:NPLC {:f}".format(nplc))

            if set_range == None:
                # measure with autorange
                self.device.conn.writeln("Fres:range:auto on")
            else:
                self.device.conn.writeln("Fres:range {:.6e}".format(set_range))

            if range_switch:
                self.device.conn.writeln("read?")
                to=n_support.TimeOut(10)
                while to.is_timed_out() == False:
                    answer = self.device.conn.readln()
                    if not answer == "":
                        to.set_timed_out()
                
            values = list()
            used_ranges = list()
            
            for k1 in range(count):
                self.device.conn.writeln("read?")
                to=n_support.TimeOut(10)
                while to.is_timed_out() == False:                
                    answer = self.device.conn.readln()
                    if not answer == "":
                        to.set_timed_out()
                if answer == "":
                    raise n_support.MeasuringError("no result received")
                else:
                    values.append(float(answer))
                    used_ranges.append(float(self.device.conn.readln("Fres:range?")))
                pass
        
        self.last = MeasurementDesc()        
        self.last.calc_value(values)
        self.last.frequency = None    
        self.last.meas_ranges = used_ranges
        self.last.settings = self.settings
        self.last.correction = 0
        self.last.unc_of_correction = 0
        self.last.drift = 0
        self.last.unc_of_drift = 0.5 * self.uncertainty( 
                                    self.last.value, 
                                    used_ranges[-1], self.settings)
        self.last.el_properties = self.get_el_properties(used_ranges[-1], self.settings)                                
        return self.last.value 

    def correction(self, value, settings):
        """ get a correction for this value with its uncertainty """
        return [0,0]
        
    def uncertainty(self, value, range_used, settings):
        #
        avalue = abs(value)

        if range_used is None:
            range_of_value = n_support.find_range(
                                avalue, self.ranges)
        else:
            range_of_value = n_support.find_range(
                                range_used, self.ranges)
        maxvalue_of_range = self.ranges[range_of_value]["max"]
        zw_uncertainty = n_support.uncertainty_from_spec(
                            avalue, self.baseSpec1yr[range_of_value], maxvalue_of_range)
        if settings[c_fct.NPLC] <= 0.02:
            zw_uncertainty += 0.017e-2 * maxvalue_of_range + 15e-3           
        elif settings[c_fct.NPLC] <= 0.2:
            zw_uncertainty += 0.003e-2 * maxvalue_of_range + 7e-3           
        elif settings[c_fct.NPLC] <= 1:
            zw_uncertainty += 0.001e-2 * maxvalue_of_range           
        return zw_uncertainty       


class Cap (fct):

    
    def __init__(self,device):
        super(Cap,self).__init__(device)
        self.settings={c_fct.Function : c_fct.cap,
                  }
        self.ranges={ 
                        c_fct.range_1n : {"min" : 0, "max" : 1e-9, "res" : 1e-12},
                        c_fct.range_10n : {"min" : 0, "max" : 1e-8, "res" : 10e-12},
                        c_fct.range_100n : {"min" : 0, "max" : 1e-7, "res" : 100e-12},
                        c_fct.range_1u : {"min" : 0, "max" : 1e-6, "res" : 1e-9},
                        c_fct.range_10u : {"min" : 0, "max" : 1e-5, "res" : 10e-9},
                        c_fct.range_100u : {"min" : 0, "max" : 1e-4, "res" : 100e-9},
                        c_fct.range_1m : {"min" : 0, "max" : 1e-3, "res" : 1e-6},
                        c_fct.range_10m : {"min" : 0, "max" : 1e-2, "res" : 10e-6},
                        c_fct.range_100m : {"min" : 0, "max" : 1e-1, "res" : 100e-6},
                    }
        self.baseSpec1yr={
                        c_fct.range_1n : {"p%" : 2.0, "fix%Range" : 2.5},
                        c_fct.range_10n : {"p%" : 1.0, "fix%Range" : 0.5},
                        c_fct.range_100n : {"p%" : 1.0, "fix%Range" : 0.5},
                        c_fct.range_1u : {"p%" : 1.0, "fix%Range" : 0.5},
                        c_fct.range_10u : {"p%" : 1.0, "fix%Range" : 0.5},
                        c_fct.range_100u : {"p%" : 1.0, "fix%Range" : 0.5},
                        c_fct.range_1m : {"p%" : 1.0, "fix%Range" : 0.5},
                        c_fct.range_10m : {"p%" : 1.0, "fix%Range" : 0.5},
                        c_fct.range_100m : {"p%" : 4.0, "fix%Range" : 0.2},
                    }


    def get_el_properties(self, range_used, settings):
        # currently we have no model parameter
        # function is not well documented
        return dict()

    def activate(self):
        #switches system to measuring functionality
        #has to be called when setting where modified
        
        self.device.conn.writeln("Conf:Cap def,Min")
        self.device.active_settings = self.settings
        pass

    def measure(self, set_range = None, count = 1):
        #returns a current value from device
        if not self.device.active_settings is self.settings:
            self.lastrange = None
            self.activate()

        range_switch = False
        if (self.lastrange is None) or (self.lastrange != set_range):
            range_switch = True
        self.lastrange = set_range             
            
        if self.device.simulation == True:
            values = self.simulation_fct(self)
        else:
            if set_range is None:
                # measure with autorange
                self.device.conn.writeln("Cap:range:auto on")
            else:
                self.device.conn.writeln("Cap:range {:.6e}".format(set_range))

            if range_switch:
                self.device.conn.writeln("read?")
                to=n_support.TimeOut(10)
                while to.is_timed_out() == False:
                    answer = self.device.conn.readln()
                    if not answer == "":
                        to.set_timed_out()

            values = list()
            used_ranges = list()
            
            for k1 in range(count):
                self.device.conn.writeln("read?")
                to=n_support.TimeOut(10)
                while to.is_timed_out() == False:                
                    answer = self.device.conn.readln()
                    if not answer == "":
                        to.set_timed_out()
                if answer == "":
                    raise n_support.MeasuringError("no result received")
                else:
                    values.append(float(answer))
                    used_ranges.append(float(self.device.conn.readln("Cap:range?")))
                pass
        
        self.last = MeasurementDesc()        
        self.last.calc_value(values)
        self.last.frequency = None    
        self.last.meas_ranges = used_ranges
        self.last.settings = self.settings
        self.last.correction = 0
        self.last.unc_of_correction = 0
        self.last.drift = 0
        self.last.unc_of_drift = 0.5 * self.uncertainty( 
                                    self.last.value, 
                                    used_ranges[-1], self.settings)
        self.last.el_properties = self.get_el_properties(used_ranges[-1], self.settings)
        return self.last.value 

    def correction(self, value, settings):
        """ get a correction for this value with its uncertainty """
        return [0,0]
        
    def uncertainty(self, value, range_used, settings):
        #
        avalue = abs(value)

        if range_used is None:
            range_of_value = n_support.find_range(
                                avalue, self.ranges)
        else:
            range_of_value = n_support.find_range(
                                range_used, self.ranges)
        maxvalue_of_range = self.ranges[range_of_value]["max"]
        zw_uncertainty = n_support.uncertainty_from_spec(
                            avalue, self.baseSpec1yr[range_of_value], maxvalue_of_range)

        return zw_uncertainty       




class device(object):
    """Interaction object with 8846 multimeter connected via RS232"""

    def __init__(self):
        self.conn = None
        self.active_settings = None
        self.simulation = False
        self.serial_number = ""



        self.volt_dc = Volt_DC(self)
        self.volt_ac = Volt_AC(self)
        self.cur_dc = Cur_DC(self)
        self.cur_ac = Cur_AC(self)
        self.res_2w = Res_2W(self)
        self.res_4w = Res_4W(self)
        self.cap = Cap(self)

    def connect(self , device=c_dev.fluke_8846A_01 , serial_number = "auto", simulation = False):
        """open interface and identify device"""
        if c_exm.no_io in c_exm.execution_mode:
            self.serial_number = serial_number
            return

        self.conn = n_support.SerialDeviceConnection()
        self.conn.target = device
#
#    def connect(self , port="auto" , serial_number = "auto", simulation = False):
#        """open interface and identify device"""
#        self.simulation = simulation
#        self.port = port        
#        if port=="auto":
#            if self.simulation == True:
#                self.port = 1
#            else:
#                portmap=n_support.Rs232PortMap()[0]
#                for key,item in portmap.iteritems():
#                    if item["Model"] == "8846A":
#                        if serial_number == "auto":
#                            self.port = key
#                        else:
#                            if item["SN"] == serial_number:
#                                self.port =key
#                            
#            
#
#        if self.port == "auto":
#            # raise error
#            raise n_support.InstrumentNotFound("SN: " + self.serial_number.__str__())
#            
#        self.conn=n_support.SerialPortConnection(simulation=self.simulation)
#        self.conn.port=self.port
#        
#        self.conn.open()
        self.conn.writeln("*rst;*CLS")  
        self.conn.writeln("*IDN?")  
        self.idn=self.conn.readln().split(",")
        if self.simulation:
            self.idn = ['FLUKE', '8846A', '1867008', '08/02/10-11:53']
        if self.idn[0] != "FLUKE" or self.idn[1] != "8846A":
            raise Exception("Wrong device connected:" + self.idn.__str__())
        self.conn.writeln("SYST:RWL")        
        self.serial_number=self.idn[2]
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
    import smt_cal_demo.calibration.devices.fluke.fluke5500e_v01 as n_cal
    unittest.main(exit=False)
    dev=device()
    online = False
    try:
        dev.connect()
        online = True
    except:
        pass

    if online:    
        cal = n_cal.device()
        cal.connect()
#        test_fct = dev.volt_dc
#        print(test_fct.measure(set_range=10, count=5))
#        print("Measured={0:7f} std: {1:.1e} unc: {2:.1e}".format(
#            test_fct.last.value,test_fct.last.unc_of_value,test_fct.last.unc_of_drift))
#    
        test_fct = dev.volt_ac
        cal.volt_ac.stimulate(1,50)
        print(test_fct.measure(frequency=50,set_range=1, count=2))
        print("Measured={0:7f} std: {1:.1e} unc: {2:.1e}".format(
            test_fct.last.value,test_fct.last.unc_of_value,test_fct.last.unc_of_drift))
        cal.volt_ac.stimulate(1,300e3)
        print(test_fct.measure(frequency=300e3,set_range=1, count=2))
        print("Measured={0:7f} std: {1:.1e} unc: {2:.1e}".format(
            test_fct.last.value,test_fct.last.unc_of_value,test_fct.last.unc_of_drift))

#        test_fct = dev.res_2w
#        print((test_fct.measure(set_range=10, count=5)))
#        print(("Measured={0:7f} std: {1:.1e} unc: {2:.1e}".format(
#            test_fct.last.value,test_fct.last.unc_of_value,test_fct.last.unc_of_drift)))
#
#        test_fct = dev.res_4w
#        print((test_fct.measure(set_range=10, count=5)))
#        print(("Measured={0:7f} std: {1:.1e} unc: {2:.1e}".format(
#            test_fct.last.value,test_fct.last.unc_of_value,test_fct.last.unc_of_drift)))
#
#        test_fct = dev.cur_ac
#        print((test_fct.measure(set_range=10, count=5)))
#        print(("Measured={0:7f} std: {1:.1e} unc: {2:.1e}".format(
#            test_fct.last.value,test_fct.last.unc_of_value,test_fct.last.unc_of_drift)))

#        test_fct = dev.cur_dc
#        print((test_fct.measure(set_range=10, count=5)))
#        print(("Measured={0:7f} std: {1:.1e} unc: {2:.1e}".format(
#            test_fct.last.value,test_fct.last.unc_of_value,test_fct.last.unc_of_drift)))
            