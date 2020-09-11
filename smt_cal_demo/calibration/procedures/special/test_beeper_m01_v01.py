# -*- coding: utf-8 -*-
"""
Created on Mon Jan 07 12:53:30 2013

@author: scheidt
"""

import time

import smt_cal_demo.utilities.easygui as eg

import smt_cal_demo.calibration.procedures.base_classes_v01 as b_c
import smt_cal_demo.calibration.models.direct.direct_applied_with_base_corrections as ns_model
import smt_cal_demo.calibration.models.support_v01 as n_sup
import smt_cal_demo.calibration.tokens.electrical_properties as c_el
import smt_cal_demo.calibration.tokens.device_functions as c_fct
import smt_cal_demo.calibration.tokens.physical_units as c_phy
import smt_cal_demo.calibration.tokens.testpoint_keys as c_tst
import smt_cal_demo.calibration.tokens.reporting as c_rpt

from smt_cal_demo.calibration.models.support_v01 import Var

c_question = "Is beeper on?"

class TestpointError(Exception):
    pass

class ProcessingInstructionsError(Exception):
    pass

class Procedure(b_c.Procedure):
    """Stimulate dut with a resistance""" 

    
    def __init__(self):
        # the following variables will contain maintained for serialization  
        self.testpoint = dict()
        self.processing_instructions = dict()
    

    def method_info(self):
        return (
        """Direct application of a resistance to the DUT
        """)
    
    def execute(self, dut, env, testpoint = dict(), processing_instructions = dict()):
        """Starts the procedure using provided parameters."""

        # make a local copy of relevant data to make them available when class is
        # stored in a database
        self.testpoint = dict(testpoint)
        self.processing_instructions = dict(processing_instructions)
        if c_tst.count not in self.processing_instructions:
            self.processing_instructions[c_tst.count]=1
            
        self.model = ns_model.Model(c_phy.Ohm)  
        

        # Prepare partners
        env.prepare(c_fct.stimulate_+c_fct.res_2w, testpoint, processing_instructions)
        dut.prepare(testpoint, processing_instructions, env)
        
        # Activate function of DUT
        envfct = env.calibrator.res

        envfct.settings["Comp"] = "off"
        envfct.stimulate(testpoint[c_tst.resistance])

        # it might be necessary to wait for stabilization
        if c_tst.delay in processing_instructions:
            time.sleep(processing_instructions[c_tst.delay])
        
        self.answer = "yes" if eg.ynbox(c_question) == 1 else "no"

        self.model.x.v = envfct.last.value
        self.model.x.u = 0.045 * 2 * 0.289

        self.model.d_x_corr.v = envfct.last.correction
        self.model.d_x_corr.u = envfct.last.unc_of_correction
        self.model.d_x_disp.v = envfct.last.dispcorr
        self.model.d_x_disp.u = envfct.last.unc_of_dispcorr
        self.model.d_x_drift.v = envfct.last.drift        
        self.model.d_x_drift.u = envfct.last.unc_of_drift        

        self.result_x  = Var(None,None,c_phy.V,"Corrected applied resistance")
        self.result_x.v = self.model.f()
        self.result_x.u = n_sup.calculate_unc(self.model)

        self.equipment_ids = env.get_equipment_ids()


    def result_string(self):
        """Returns a formatted string with the calibration data."""

        zw="{:14.6g} {:8.1e} {:>50s} {:>10s}".format(
                    self.result_x.v,
                    self.result_x.u * 2,
                    c_question,
                    self.answer)
                
        return zw
    
    def header_string(self):
        """Delivers a header fitting to result_string."""
        zw="{:>14s} {:>8s} {:>50s} {:>10s}".format(
                    "Applied","Exp Unc","Question", "Answer")
        return zw
        
    def result_list(self):
        zw = list()
        return [
                    self.result_x,
                    c_question,
                    self.answer
                    ]
        
    def header_list(self):
        zw = list()
        zw.append((c_rpt.applied,c_phy.Ohm,c_rpt.environment,c_rpt.exp_unc))
        zw.append((c_rpt.question,c_phy.string,c_rpt.not_grouped))
        zw.append((c_rpt.answer,c_phy.string,c_rpt.dut))
        return zw
        

# the following section is used for testing. It is executed if 
# the script is started for its own        
if __name__ == '__main__':
    pass
    import smt_cal_demo.calibration.environments.fluke5500e_v01 as Env
    import smt_cal_demo.calibration.dut.generic_manual_v01 as Dut
    
    env = Env.Environment()
    dut = Dut.DUT()
    
    pro = Procedure()
    testpoint = { 
                 c_fct.Function: c_fct.continuity,
                 c_tst.resistance: 10}
                 
    pro.execute(dut, env, testpoint , dict())
    
    print((pro.header_string())); print((pro.result_string()))
    
    testpoint = { 
             c_fct.Function: c_fct.continuity,
             c_tst.resistance: 200}
                 
    pro.execute(dut, env, testpoint , dict())
    
    print((pro.result_string()))