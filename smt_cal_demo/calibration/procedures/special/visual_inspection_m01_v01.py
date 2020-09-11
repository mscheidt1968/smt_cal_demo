# -*- coding: utf-8 -*-
"""
Created on Fri Apr 05 19:56:35 2013

@author: scheidt
"""

import smt_cal_demo.utilities.easygui as eg

import smt_cal_demo.calibration.procedures.base_classes_v01 as b_c
import smt_cal_demo.calibration.tokens.electrical_properties as c_el
import smt_cal_demo.calibration.tokens.device_functions as c_fct
import smt_cal_demo.calibration.tokens.physical_units as c_phy
import smt_cal_demo.calibration.tokens.testpoint_keys as c_tst
import smt_cal_demo.calibration.tokens.reporting as c_rpt


class ProcessingInstructionsError(Exception):
    pass

class Procedure(b_c.Procedure):
    """Asks user a question and get a good bad answer.""" 
    
    def __init__(self, environment = None):
        self.testpoint = dict()
        self.processing_instructions = dict()

    def method_info(self):
        return (
        """Visual inspection of a certain functionality by the operator.
        """)
    
    def execute(self, dut, env, testpoint = dict(), processing_instructions = dict()):
        self.testpoint = testpoint.copy()
        self.processing_instructions = processing_instructions.copy()

        if "message" not in processing_instructions:
            raise ProcessingInstructionsError("No message specified")

        self.answer = eg.ynbox(processing_instructions["message"])
        


    def result_string(self): 
        """ gives a nice string of the calibration """

        zw=("Question:" + self.processing_instructions["message"]+ 
            " Answer: " + ("Yes" if self.answer else "No")
            )
                
        return zw
    
    def header_string(self):
        """ delivers a header fitting to report result """
        zw="Visual inpection"
        return zw
        
    def result_list(self):
        return [
                    self.processing_instructions["message"],
                    ("Yes" if self.answer else "No")
                    ]
        
    def header_list(self):
        return(["Question","Answer"])
        
        
if __name__ == '__main__':
    proc=Procedure(environment= None)
    
    print((proc.header_string()))
    
    print("First time test")
    proc.execute(None,None,{"function":"Display"},{"message":"Is display working"})
    print((proc.result_string()))




