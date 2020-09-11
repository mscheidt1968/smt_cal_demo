# -*- coding: utf-8 -*-
"""
Created on Sat Dec 29 14:26:19 2012

@author: Scheidt
"""
import smt_cal_demo.utilities.easygui as eg
import smt_cal_demo.calibration.procedures.base_classes_v01 as b_c 
from smt_cal_demo.calibration.devices.fluke.fluke5500e_v01 import device as fluke5500e

from smt_cal_demo.calibration.models.support_v01 import Var

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

    
class Environment(b_c.Environment):
    
    def __init__(self):
        super(Environment,self).__init__()
        self.setup = ""
        self.calibrator = fluke5500e()
        self.calibrator.connect()
        self.el_properties = dict()
        self.el_properties_std_cable = dict()
        self.el_properties_std_cable[c_elp.C_leads] = Var(42e-12,5e-12*0.289*2,c_phy.F,"Capacity of cabling")
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

    def release(self):
        """Releasses attached devices, so that a restart is possible"""
        self.switch_to_safe_state()
        self.calibrator.disconnect()                
        
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
        else:
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
    
    env.calibrator.volt_dc.stimulate(10)
