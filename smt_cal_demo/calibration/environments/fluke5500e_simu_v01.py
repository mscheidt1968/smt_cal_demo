# -*- coding: utf-8 -*-
"""
Created on Tue Dec 31 15:42:25 2013

@author: Scheidt
"""

import numpy as np

import smt_cal_demo.utilities.easygui as eg
import smt_cal_demo.calibration.procedures.base_classes_v01 as b_c 

from smt_cal_demo.calibration.models.support_v01 import Var
import smt_cal_demo.calibration.tokens.electrical_properties as c_el
import smt_cal_demo.calibration.tokens.device_functions as c_fct
import smt_cal_demo.calibration.tokens.testpoint_keys as c_tst
import smt_cal_demo.calibration.tokens.physical_units as c_phy
import smt_cal_demo.calibration.tokens.electrical_properties as c_elp

c_stim_voltage = "stim_voltage"
c_stim_current = "stim_current"
c_stim_res_2w_comp = "stim_res_2w_comp"
c_stim_res_4w = "stim_res_4w"
c_stim_cap = "stim capacitance"
c_stim_thermocouple = "stim thermocouple"

c_apply_4w_short = "apply 4w short"
c_apply_short = "apply short"
c_apply_open = "apply open"


class SetupError(Exception):
    pass


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
    
    device = None  #links to device data
    simulation_fct = lambda x,y: 0
    settings = dict()
    
    last = StimulationDesc()

    def __init__(self,device):
        self.device = device

    def activate(self):
        """ call this to prepare instrument to measure with the current settings """
        #switches system to measuring functionality
        #has to be called when setting where modified
        self.device.active_settings=self.settings
        pass
        
    def stimulate(self):
        """ returns a current value """
        if not device.active_settings is self.settings:
            self.activate()
        #returns a current value from device
        if self.device.simulation == True:
            value = self.simulation_fct(self)
        return (value,self.device.active_settings) 
        
    def correction(self,value,settings):
        """ get a correction for this value with its uncertainty """
        return [0,0]
        
    def correct(self, value, settings):
        """ just applies correction to the current value """
        return value + self.correction(value, settings)
        
    def uncertainty(self,value,settings):
        #
        pass


class VoltAc(fct):


    
    def stimulate(self, voltage, frequency):
        self.el_properties_5mOhm = {
                                c_el.R_s : Var(5e-3, 0.289 * 2 * 10e-2 * 5e-3, c_phy.Ohm, "Series Resistance of voltage source")
                            }

        self.last.value = voltage
        self.last.unc_of_value = 1e-4*voltage
        self.last.meas_range = None
        self.last.settings = None
        self.last.correction = 0
        self.last.unc_of_correction= 0
        self.last.frequency = frequency
        self.last.unc_of_frequency_drift = 1e-6*frequency
        self.last.el_properties = self.el_properties_5mOhm
        self.last.dispcorr = 0
        self.last.unc_of_dispcorr = 0
        self.last.drift = 0
        self.last.unc_of_drift = 0
            
        pass
    
    
class CalibSimu(object):

    def __init__(self):
        self.volt_ac = VoltAc(self)

    def connect(self):
        pass
    
    def standby(self):
        pass

   
class Environment(b_c.Environment):
    
    def __init__(self):
        self.setup = ""
        self.calibrator = CalibSimu()
        self.calibrator.connect()
        self.el_properties = dict()
        self.el_properties_std_cable = dict()
        self.el_properties_std_cable[c_elp.C_leads] = Var(50e-12,5e-12*0.289*2,c_phy.F,"Capacity of cabling")
        self.el_properties_std_cable[c_elp.L_leads] = Var(1e-9,0.1e-9*0.289*2,c_phy.F,"Inductivity of cabling")
        self.el_properties_std_cable[c_elp.R_leads] = Var(0.046,0.1 * 0.046 * 0.289 *2,c_phy.F,"Resitance of 1m 0.75mm^2 cabling")
        self.el_properties_cable_short = dict()
        self.el_properties_cable_short[c_elp.R_leads] = Var(0.0005,0.1 * 0.0005 * 0.289 *2,c_phy.Ohm,"Resitance of a short")
        self.el_properties_cable_2W_comp = dict()
        self.el_properties_cable_2W_comp[c_elp.R_leads] = Var(0.005,0.1 * 0.005 * 0.289 *2,c_phy.Ohm,"Resitance of cables when 2 wiring with compensations is used")
        self.el_properties_cable_4W_comp = dict()
        self.el_properties_cable_4W_comp[c_elp.R_leads] = Var(0.001,0.1 * 0.001 * 0.289 *2,c_phy.Ohm,"Resitance of contacts when 4 wire resistance measurement is used")
        self.el_properties_std_thermal =dict()
        self.el_properties_std_thermal[c_elp.U_thermo] = Var(0,1e-6 * 2 * 0.289, c_phy.V, "thermal voltage")
        self.el_properties_std1 = dict()
        self.el_properties_std1.update(self.el_properties_std_cable)
        self.el_properties_std1.update(self.el_properties_std_thermal)

    def emergeny_stop(self):
        self.calibrator.standby()
        
    def switch_to_safe_state(self):
        self.calibrator.standby()

    def prepare(self, setup, test_point, processing_instructions, dut = None):
        if setup == c_fct.stimulate_ + c_fct.volt_dc or setup == c_fct.stimulate_ + c_fct.volt_ac:
            self.el_properties = self.el_properties_std1
            if self.setup != c_stim_voltage:
                self.switch_to_safe_state()
                eg.msgbox("Wire calibrator for voltage stimulation")
                self.setup = c_stim_voltage
        elif setup == c_fct.stimulate_ + c_fct.cur_dc or setup == c_fct.stimulate_ + c_fct.cur_ac:
            self.el_properties = self.el_properties_std1
            if self.setup != c_stim_current:
                self.switch_to_safe_state()
                eg.msgbox("Wire calibrator for current stimulation")
                self.setup = c_stim_current
        elif setup == c_fct.stimulate_ + c_fct.res_2w:
            self.el_properties = self.el_properties_std1
            self.el_properties.update(self.el_properties_cable_2W_comp)
            if self.setup != c_stim_res_2w_comp:
                self.switch_to_safe_state()
                eg.msgbox("Wire calibrator for 2 wire resistance emulation with leads compensation")
                self.setup = c_stim_res_2w_comp
        elif setup == c_fct.stimulate_ + c_fct.res_4w:
            self.el_properties = self.el_properties_std1
            self.el_properties.update(self.el_properties_cable_4W_comp)
            if self.setup != c_stim_res_4w:
                self.switch_to_safe_state()
                eg.msgbox("Wire calibrator for resistance emulation 4 wire")
                self.setup = c_stim_res_4w
        elif setup == c_fct.stimulate_ + c_fct.cap:
            self.el_properties = self.el_properties_std1
            if self.setup != c_stim_cap:
                self.switch_to_safe_state()
                eg.msgbox("Wire calibrator to emulate capacity")
            self.setup = c_stim_cap
        elif setup == c_fct.stimulate_ + c_fct.thermocouple:
            self.el_properties = self.el_properties_std1
            if self.setup != c_stim_thermocouple:
                self.switch_to_safe_state()
                eg.msgbox("Wire calibrator to emulate a thermocouple. Use tc output.")
            self.setup = c_stim_thermocouple
        elif setup == c_fct.apply_short:
            self.el_properties = self.el_properties_std1
            self.el_properties.update(self.el_properties_cable_short)
            if self.setup != c_apply_short:
                self.switch_to_safe_state()
                eg.msgbox("Disconnect calibrator and apply a short to the DUT")
            self.setup = c_apply_short
        elif setup == c_fct.apply_short4w:
            self.el_properties = self.el_properties_std1
            self.el_properties.update(self.el_properties_cable_short)
            if self.setup != c_apply_4w_short:
                self.switch_to_safe_state()
                eg.msgbox("Disconnect calibrator and apply a short on all 4 input ports of DUT")
            self.setup = c_apply_4w_short
        elif setup == c_fct.apply_open:
            self.el_properties = self.el_properties_std1
            if self.setup != c_apply_open:
                self.switch_to_safe_state()
                eg.msgbox("Disconnect calibrator and leave input ports of DUT open")
            self.setup = c_apply_open
        else:
            raise SetupError("Requested setup " + setup + " not defined")
        pass


    def get_equipment_ids(self):
        """A list of scheidt messtechnik unique identifiers"""
        if (self.setup == c_apply_4w_short or
            self.setup == c_apply_open or
            self.setup == c_apply_short or
            self.setup == c_stim_cap or
            self.setup == c_stim_current or
            self.setup == c_stim_res_2w_comp or
            self.setup == c_stim_res_4w or
            self.setup == c_stim_voltage or 
            self.setup == c_stim_thermocouple
            ):
            instrument_list = ["121004_ASC_04"]
        return instrument_list
    

    def set_el_property(self, prop_to_set, property_name, testpoint, processing_instructions):
        """ writes data of required property to prop_to_set"""
        if property_name in self.el_properties:
            prop_to_set.v = self.el_properties[property_name].v
            prop_to_set.u = self.el_properties[property_name].u
        else:
            pass
            raise ElPropertyMissing("Requested property " + property_name + " not available")
        return
                
        
        
if __name__ == '__main__':
    env=Environment()
    print("First time")
    env.prepare(c_fct.stimulate_+c_fct.volt_ac,None,None)
    print("Second time")
    env.prepare(c_fct.stimulate_+c_fct.volt_dc,None,None)
    
    print("First time")
    env.prepare(c_fct.stimulate_+c_fct.cur_ac,None,None)
    print("Second time")
    env.prepare(c_fct.stimulate_+c_fct.cur_dc,None,None)
    
