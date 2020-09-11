# -*- coding: utf-8 -*-
"""
Created on Thu Jan 03 12:43:13 2013

@author: Scheidt
"""

import numpy as np

import smt_cal_demo.utilities.easygui as eg
import smt_cal_demo.calibration.procedures.base_classes_v01 as b_c 
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
        # indicate that this cant be used in another thread
        self.notthreaded = True
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
        msg = "Activate function to accomplish following settings:"
        for key,item in test_point.items():
            if key == "resistance":
                msg += "\n" + key + " = " + "{:.3e}".format(item)
            else:
                msg += "\n" + key + " = " + str(item)

        msg += "\nFinally please enter the adjusted value or leave blank, if value is as requested."
        if c_exm.no_ui in c_exm.execution_mode:
            answer = ""
        else:
            answer = eg.enterbox(msg,"")

        if answer != "":        
            self.last.value = float(answer)
            self.last.unc_of_value = 0
            self.last.unc_of_dispcorr = 0
        else:
            if c_tst.capacitance in test_point:
                self.last.value = test_point[c_tst.capacitance]
            elif c_tst.voltage in test_point:
                self.last.value = test_point[c_tst.voltage]
            elif c_tst.power in test_point:
                self.last.value = test_point[c_tst.power]
            elif c_tst.resistance in test_point:
                self.last.value = test_point[c_tst.resistance]
            elif c_tst.current in test_point:
                self.last.value = test_point[c_tst.current]
            elif c_tst.frequency in test_point:
                self.last.value = test_point[c_tst.frequency]
            elif c_tst.time_interval in test_point:
                self.last.value = test_point[c_tst.time_interval]
            self.last.unc_of_value = 0
            self.last.unc_of_dispcorr = 0

        for key,item in processing_instructions.items():
            if key[0] == "@":
                self.last.el_properties[key[1:]] = Var(float(item.split(" ")[0]),
                                                float(item.split(" ")[1])*0.289*2,
                                                item.split(" ")[2])
        return

    def read_indications(self,
                    test_point=dict(),
                    processing_instructions=dict(),
                    sim_value=None):
        if c_exm.no_ui in c_exm.execution_mode and not(sim_value is None):
            self.last = sim_value
        else:
            """Return a list of indications from device under test."""
            scale_disp = processing_instructions[c_tst.scale_disp] if c_tst.scale_disp in processing_instructions else 1
            disp_unit = ""        
            if scale_disp == 1e3:
                disp_unit = "in kilo units"
            elif scale_disp == 1e6:
                disp_unit = "in Mega units"
            elif scale_disp == 1e6:
                disp_unit = "in Giga units"
            elif scale_disp == 1e-3:
                disp_unit = "in milli units"
            elif scale_disp == 1e-6:
                disp_unit = "in mikro units"
            elif scale_disp == 1e-9:
                disp_unit = "in nano units"
            elif scale_disp == 1e-12:
                disp_unit = "in piko units"
            elif scale_disp == 1:
                disp_unit = "in base units"
            else:
                disp_unit = "in " + str(1/float(scale_disp)) + " units"
    
    
            msg = "Testpoint is:"
            for key,item in test_point.items():
                if key == "resistance":
                    msg += "\n" + key + " = " + "{:.3e}".format(item)
                else:
                    msg += "\n" + key + " = " + str(item)
                    
                
            msg += "Enter the indication of the DUT" + disp_unit
    
            if c_tst.count in processing_instructions:
                repetition = processing_instructions[c_tst.count]
            else:
                repetition = 1
    
            self.last.values = list()        
            prop_unc = 0
            const_unc = 0
            while repetition>0:
                success = False
                while not success:        
                    repetition -= 1
                    data_entry = eg.multenterbox(msg,c_title,("Indication","Uncertainty (fix or %)","Residual repetitions"),("",self.last_uncertainty_entry,str(repetition)))
                    self.last_uncertainty_entry = data_entry[1]
                    try:
                        indication = data_entry[0]
                        repetition = float(data_entry[2])
                        self.last.values.append(float(indication) * scale_disp)
                        if self.last_uncertainty_entry == "":
                            if indication.find(".")==-1:
                                self.last.unc_of_dispcorr = scale_disp * 0.289 * 2
                            else:
                                self.last.unc_of_dispcorr = scale_disp * 0.289 * 2 * 10 * abs(float(data_entry+"1" ) - float(data_entry))
                        else:
                            if self.last_uncertainty_entry[-1] == "%":
                                prop_unc = float(self.last_uncertainty_entry[:-1])/100
                                const_unc = 0
                            else:
                                const_unc = float(self.last_uncertainty_entry) * 0.5               
                                prop_unc = 0
    
                        success = True
                    except ElPropertyFormatException as exc:
                        eg.msgbox("Try again because:" + exc.args[0])
                    except ValueError as exc:
                        eg.msgbox("Try again because:" + exc.args[0])
            
            self.last.calc_value()            
            if prop_unc != 0 or const_unc != 0:
                self.last.unc_of_dispcorr = prop_unc * self.last.value + const_unc * scale_disp

        self.last.el_properties = dict()
        for key,item in processing_instructions.items():
            if key[0] == "@":
                self.last.el_properties[key[1:]] = Var(float(item.split(" ")[0]),
                                                float(item.split(" ")[1])*0.289*2,
                                                item.split(" ")[2])
                              
        

    def prepare(self, test_point, processing_instructions, environment = None):
        """Chance to modify wiring and so on if function is changing"""
        """Chance to make bigger setup changes"""
        sub_function = test_point[c_tst.sub_function] if c_tst.sub_function in test_point else ""
        orientation = test_point[c_tst.orientation] if c_tst.orientation in test_point else ""
        if self.setup != test_point[c_fct.Function] + sub_function + str(orientation):
            if environment is None:
                pass
            else:
                environment.switch_to_safe_state()
            msg = "Wire the DUT such to accomplish " + test_point[c_fct.Function] + " " + sub_function + " function"
            if orientation!= "":
                msg += "Set orientation of connector to : " + str(orientation)

            if c_exm.no_ui not in c_exm.execution_mode:
                eg.msgbox(msg)

        self.setup = test_point[c_fct.Function] + sub_function + str(orientation)



    def switch_to_safe_state(self):
        """Brings system to an safe state regularly."""
        if c_exm.no_ui not in c_exm.execution_mode:
            eg.msgbox("Bring system to a save state.")
    
    def test_finished(self):
        """called when a dut object is not used anymore"""
        pass
    
    def info(self):
        answer = eg.enterbox("Please enter details about the settings of DUT for the report")
        return answer
        
if __name__=="__main__":
    print("Local tests")
    dut = DUT()
    dut.read_indications(dict(),dict(count=3))
    