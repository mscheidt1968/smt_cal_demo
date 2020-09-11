# -*- coding: utf-8 -*-
"""
Created on Wed Jan 02 16:06:26 2013

@author: Scheidt
"""

import time

import smt_cal_demo.calibration.procedures.base_classes_v01 as b_c
import smt_cal_demo.calibration.models.direct.direct_stimulate_capacitance_m01_v01 as ns_model
import smt_cal_demo.calibration.models.support_v01 as n_support_v01
import smt_cal_demo.calibration.tokens.electrical_properties as c_el
import smt_cal_demo.calibration.tokens.device_functions as c_fct
import smt_cal_demo.calibration.tokens.physical_units as c_phy
import smt_cal_demo.calibration.tokens.testpoint_keys as c_tst
import smt_cal_demo.calibration.tokens.reporting as c_rpt

import smt_cal_demo.utilities.easygui as eg

from smt_cal_demo.calibration.models.support_v01 import Var

c_standard = "standard"

class TestpointError(Exception):
    pass

class ProcessingInstructionsError(Exception):
    pass

class Procedure(b_c.Procedure):
    """Stimulate dut with a capacitance""" 

    standard = None
    standard_id = None
    
    def __init__(self):
        # the following variables will contain maintained for serialization  
        self.testpoint = dict()
        self.processing_instructions = dict()
    

    def method_info(self):
        return (
        """*Direct application of a capacitance to the DUT. 
        """)
    
    def execute(self, dut, env, testpoint = dict(), processing_instructions = dict()):
        """Starts the procedure using provided parameters."""

        # make a local copy of relevant data to make them available when class is
        # stored in a database
        self.testpoint = dict(testpoint)
        self.processing_instructions = dict(processing_instructions)
        if c_tst.count not in self.processing_instructions:
            self.processing_instructions[c_tst.count]=1
            
        self.model = ns_model.Model()  
        

        # Prepare partners
        self.standard = None
        self.standard_id = ""

        if self.standard is None:
            env.prepare(c_fct.stimulate_+c_fct.cap, testpoint, processing_instructions)

        dut.prepare(testpoint, processing_instructions, env)
        
        # Activate function of DUT
        if self.standard is None:
            envfct = env.calibrator.cap
            envfct.stimulate(testpoint[c_tst.capacitance])

        # it might be necessary to wait for stabilization
        if c_tst.delay in processing_instructions:
            time.sleep(processing_instructions[c_tst.delay])
        
        dut.read_indications(testpoint, processing_instructions)
        
        if self.standard is None:
            self.model.x.v = envfct.last.value
            self.model.x.u = envfct.last.unc_of_value
    
            self.model.d_x_corr.v = envfct.last.correction
            self.model.d_x_corr.u = envfct.last.unc_of_correction
            self.model.d_x_disp.v = envfct.last.dispcorr
            self.model.d_x_disp.u = envfct.last.unc_of_dispcorr
            self.model.d_x_drift.v = envfct.last.drift        
            self.model.d_x_drift.u = envfct.last.unc_of_drift        
            if "Lead_compensation" in processing_instructions:
                if processing_instructions["Lead_compensation"] != "yes":
                    print("no lead compensation")
                    self.model.c_leads = Var(0.0,0.5e-12,c_phy.F,"")
                else:
                    self.model.c_leads = env.el_properties[c_el.C_leads]
            else:
                self.model.c_leads = env.el_properties[c_el.C_leads]
        else:
            self.model.x = self.standard.capacitance(testpoint, processing_instructions)
            self.model.d_x_corr.v = self.standard.last.correction
            self.model.d_x_corr.u = self.standard.last.unc_of_correction
            self.model.d_x_disp.v = self.standard.last.dispcorr
            self.model.d_x_disp.u = self.standard.last.unc_of_dispcorr
            self.model.d_x_drift.v = self.standard.last.drift        
            self.model.d_x_drift.u = self.standard.last.unc_of_drift
            if "@C_leads" in processing_instructions:
                self.set_el_property(self.model.c_leads,"C_leads", processing_instructions)
            else:
                self.model.c_leads = Var(0.0, 0.0, c_phy.F,"")
            


        
        self.model.y.v = 0
        self.model.y.u = 0
        self.model.d_y_corr.v = 0
        self.model.d_y_corr.u = 0
        self.model.d_y_disp.v = 0
        self.model.d_y_disp.u = 0
        self.model.d_y_drift.v = 0      
        self.model.d_y_drift.u = 0       

        self.result_x  = Var(None,None,c_phy.V,"Corrected applied capacitance")
        self.result_x.v = self.model.f()
        self.result_x.u = n_support_v01.calculate_unc(self.model)

        self.model.y.v = dut.last.value
        self.model.y.u = dut.last.unc_of_value

        self.model.d_y_corr.v = dut.last.correction
        self.model.d_y_corr.u = dut.last.unc_of_correction
        self.model.d_y_disp.v = dut.last.dispcorr
        self.model.d_y_disp.u = dut.last.unc_of_dispcorr
        self.model.d_y_drift.v = 0 #dut.last.drift      
        self.model.d_y_drift.u = 0 #dut.last.unc_of_drift    
        
        
        # now model is filled up with all necessary data. Calculate result 
        self.result = Var(None, None, c_phy.V, "Difference between capacitance applied and measured with DUT")
        self.result.v = self.model.f()
        self.result.u = n_support_v01.calculate_unc(self.model)
        if self.standard is None:
            self.equipment_ids = env.get_equipment_ids()
        else:
            self.equipment_ids = [self.standard_id]


    def result_string(self):
        """Returns a formatted string with the calibration data."""

        zw="{:>14s} {:14.6g} {:8.1e} {:14.6g} {:14.6g} {:8.1e}".format(
                    "{0:14.6g}".format(self.testpoint[c_tst.range]) if c_tst.range in self.testpoint else c_rpt.no_range_specified,
                    self.result_x.v,
                    self.result_x.u * 2,
                    self.model.y.v,
                    self.result.v,
                    self.result.u * 2,
                    )
                
        return zw
    
    def header_string(self):
        """Delivers a header fitting to result_string."""
        zw="{:>14s} {:>14s} {:>8s} {:>14s} {:>14s} {:>8s}".format(
                    "Range","Applied", "Exp Unc","DUT actual", "Dev", "Exp Unc")
        return zw
        

    def result_list(self):
        zw = list()
        if c_tst.range in self.testpoint:
            zw.append(self.testpoint[c_tst.range])
        if c_tst.frequency in self.testpoint:
            zw.append(self.testpoint[c_tst.frequency])
        
        zw.extend(
         [
                    self.result_x,
                    self.model.y.v,
                    self.result,
                    ])
        return zw
        
    def header_list(self):
        zw = list()
        if c_tst.range in self.testpoint:
            zw.append((c_rpt.range,c_phy.F,c_rpt.dut))
        if c_tst.frequency in self.testpoint:
            zw.append((c_rpt.frequency_app,c_phy.Hz,c_rpt.environment))
        zw.append((c_rpt.capacitance_app,c_phy.F,c_rpt.environment,c_rpt.exp_unc))
        zw.append((c_rpt.capacitance_read,c_phy.F,c_rpt.dut))
        zw.append((c_rpt.deviation,c_phy.F,c_rpt.not_grouped,c_rpt.exp_unc))
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
    testpoint = {c_tst.range: 1e-9, 
                 c_fct.Function: c_fct.cap,
                 c_tst.frequency: 10000,
                 c_tst.capacitance: 2.9e-9}

    proc_instr = {c_standard: "151003_ASC_01"}
    proc_instr = {}
                 
    pro.execute(dut, env, testpoint , proc_instr)
