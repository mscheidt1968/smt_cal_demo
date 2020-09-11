# -*- coding: utf-8 -*-
"""
Created on Sat Dec 29 13:39:11 2012

@author: Scheidt
"""
import smt_cal_demo.utilities.easygui as eg
from smt_cal_demo.calibration.models.support_v01 import Var
import smt_cal_demo.calibration.tokens.reporting as c_rpt

class EnvironmentNotSet(Exception):
    pass

class ElPropertyFormatException(Exception):
    pass

# the device should be able to understand the requirments in the testpoint
class DeviceUnderTest(object):
    """Contains functions needed to interact with a device to test"""

        
    def set_el_property(self, prop_to_set, property_name, testpoint, processing_instructions):
        """ writes data of required property to prop_to_set"""
        if hasattr(self,"el_properties"):
            prop_to_set.v = self.el_properties[property_name].v
            prop_to_set.u = self.el_properties[property_name].u
            return
        if hasattr(self,"last"):
            if hasattr(self.last,"el_properties"):
                if property_name in self.last.el_properties:
                    prop_to_set.v = self.last.el_properties[property_name].v
                    prop_to_set.u = self.last.el_properties[property_name].u
                    return
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

    def activate_function(self, test_point=dict() ,processing_instructions= dict()):
        """Activate a function of this equipment."""
        return

    def read_indications(self, test_point=dict() ,processing_instructions= dict()):
        """Reads indcations and stores data in last variable."""
        return list()

    def prepare(self, test_point, processing_instructions, environment = None):
        """Chance to modify wiring and so on if function is changing"""
        pass

    def switch_to_safe_state(self):
        """Brings system to an safe state regularly."""
        pass
    
    def test_finished(self):
        """called when a dut object is not used anymore"""
        pass
        
class Environment(object):
    """Contains functions needed to interact with the surrounding equipment"""
    
    def __init__(self):
        self.additional_standards = dict()
    
    def switch_to_safe_state(self):
        """Brings system to an safe state regularly."""
        pass

    def emergency_stop(self):
        """Brings system to an as safe as possible state"""
        pass

    def prepare(self, setup, test_point, processing_instructions, dut = None):
        """Chance to make bigger setup changes"""
        pass
    
    def get_equipment_ids(self):
        """A list of scheidt messtechnik unique identifiers"""
        return list()
        
    
class Procedure(object):
    """Basic structure of a mesaurement procedure
    
    Environment is a class providing infrastructure like
    calibrators, multimeters, temperature and so on
    """

    def set_el_property(self, prop_to_set, property_name, processing_instructions):
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
            raise Exception("Property " + property_name + " not found")
    
        return
    
   
    def execute(self,dut, env, testpoint, processing_instructions):
        """Starts a procedure"""
        pass
    

    def result_string(self):
        """Representation of measured data as unicode string.
        
        Fits headerstring function"""
        
        hl=self.header_list()
        rl=self.result_list()

        info = ""        
        for k1 in range(len(hl)):
            if len(hl[k1]) == 3:
                if (type(rl[k1]) is str) or (type(rl[k1]) is str):
                    info += "{:>16s}\t".format(rl[k1])
                elif (type(rl[k1]) is Var):
                    info += "{:16e}\t".format(rl[k1].v)
                else:
                    info += "{:16e}\t".format(rl[k1])
            elif hl[k1][3] == c_rpt.exp_unc_limited:
                if (type(rl[k1][0]) is not Var):
                    raise Exception("Var type expeccted")
                else:
                    if rl[k1][0].v < rl[k1][1][0]:
                        info += "{:16s}\t{:16s}\t".format(rl[k1][1][1],"-")
                    elif rl[k1][0].v > rl[k1][2][0]:
                        info += "{:16s}\t{:16s}\t".format(rl[k1][2][1],"-")
                    else:
                        info += "{:16e}\t{:16e}\t".format(rl[k1][0].v,rl[k1][0].u)
            elif hl[k1][3] == c_rpt.exp_unc:
                info += "{:16e}\t{:16e}\t".format(rl[k1].v,rl[k1].u)
            else:
                if (type(rl[k1]) is str):
                    info += "{:>16s}\t".format(rl[k1])
                elif (type(rl[k1]) is Var):
                    info += "{:16e}\t".format(rl[k1].v)
                else:
                    info += "{:16e}\t".format(rl[k1])

        return info
    
    def header_string(self):
        """returns header as unicode string for output of data
        
        headerstring fits datastring function"""

        hl=self.header_list()
        info = ""        
        for k1 in range(len(hl)):
            if len(hl[k1]) == 3:
                info += "{:>16s}\t".format(hl[k1][0])
            elif hl[k1][3] == c_rpt.exp_unc:
                info += "{:>16s}\t{:>16s}\t".format(hl[k1][0],"Unc.")
            elif hl[k1][3] == c_rpt.exp_unc_limited:
                info += "{:>16s}\t{:>16s}\t".format(hl[k1][0],"Unc.")
            else:
                info += "{:>16s}\t".format(hl[k1][0])

        return info        

    def header_list(self):
        """returns header as a list of unicode string for output of data"""
        return list()
        
    def result_list(self):
        """returns a list of result data"""
        return list()
        
    def method_info(self):
        """Information on measurement method"""
        return ""