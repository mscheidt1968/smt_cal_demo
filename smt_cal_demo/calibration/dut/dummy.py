# -*- coding: utf-8 -*-
"""
Created on Thu Jan 03 12:43:13 2013

@author: Scheidt
"""

import numpy as np

import smt_cal_demo.utilities.easygui as eg
import smt_cal_demo.calibration.procedures.base_classes_v01 as b_c 
import smt_cal_demo.calibration.devices.fluke.fluke8846a_v01 as fluke8846a
import smt_cal_demo.calibration.tokens.device_functions as c_fct
import smt_cal_demo.calibration.tokens.testpoint_keys as c_tst
import smt_cal_demo.calibration.tokens.physical_units as c_phy
import smt_cal_demo.calibration.tokens.execution_modes as c_exm
from smt_cal_demo.calibration.models.support_v01 import Var

c_title = "Calibration DUT"

class ElPropertyFormatException(Exception):
    pass

class MeasurementDesc(object):

    def __init__(self):
        self.values = None
        self.value = None
        self.unc_of_value = None
        self.meas_ranges = None
        self.settings = dict()
        self.correction = 0
        self.unc_of_correction= 0
        self.frequency = None
        self.el_properties = dict()
        self.dispcorr = 0
        self.unc_of_dispcorr = 0
        self.drift = 0
        self.unc_of_drift = 0
    
    def calc_value(self):
        self.value = np.mean(self.values)
        if len(self.values)<2:
            # no statistics reasonable
            self.unc_of_value = 0
        else:
            self.unc_of_value = np.std(self.values, ddof=1)


class DUT(b_c.DeviceUnderTest):
    """Contains functions needed to interact with a device to test"""
    
    def __init__(self):
        self.setup = ""
        self.last = MeasurementDesc()
        self.last_uncertainty_entry = "1%"
        
    def release(self):
        """ release connected devices"""
        pass
        
    def get_el_property(self, name, proto, test_point, processing_instructions= dict()):
        msg = "Please enter the property {:s} of the DUT.".format(name)
        msg += "Description {:s}".format(proto.description)
        answer = eg.multenterbox(msg, c_title, ("Value:", "Uncertainty"))
        zw = Var(float(answer[0]), float(answer[1]), proto.unit, proto.description)
        return zw


    def set_el_property(self, prop_to_set, property_name, testpoint, processing_instructions):
        """ writes data of required property to prop_to_set"""
        if "@" + property_name in processing_instructions:
            value = processing_instructions["@" + property_name]
            try:
                prop_to_set.v = float(value.split(" ")[0])
                prop_to_set.u = float(value.split(" ")[1])
            except:
                raise ElPropertyFormatException("Property " + property_name + " found but format of value: " +value + " not usable")
            pass
        else:
            msg = "Please enter the property {:s} of the DUT.".format(property_name)
            msg += "Description {:s}".format(prop_to_set.description)
            success = False
            while not success:
                try:
                    answer = eg.multenterbox(msg, c_title, ("Value:", "Uncertainty"))
                    prop_to_set.v = float(answer[0])
                    prop_to_set.u = float(answer[1])
                    success = True
                except:
                    eg.msgbox("Please enter float numbers")
    
        return

    
    def activate_function(self, test_point=dict() ,processing_instructions= dict(), environment = None):
        """Activate a function of this equipment."""
        pass

    def read_indications(self,
                    test_point=dict(),
                    processing_instructions=dict(),
                    sim_value=None):
        if c_exm.no_ui in c_exm.execution_mode and not(sim_value is None):
            self.last = sim_value
                              
        

    def prepare(self, test_point, processing_instructions, environment = None):
        """Chance to modify wiring and so on if function is changing"""
        """Chance to make bigger setup changes"""
        pass



    def switch_to_safe_state(self):
        """Brings system to an safe state regularly."""
        pass
    
    def test_finished(self):
        """called when a dut object is not used anymore"""
        pass
    
    def info(self):
        return ""
        
if __name__=="__main__":
    print("Local tests")
    dut = DUT()
    