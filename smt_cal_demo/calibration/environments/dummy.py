# -*- coding: utf-8 -*-
"""
Created on Sun Oct 13 11:19:54 2013

@author: Scheidt
"""


import smt_cal_demo.calibration.procedures.base_classes_v01 as b_c 


c_title = "Environment"

class SetupError(Exception):
    pass


class Environment(b_c.Environment):
    """Contains functions needed to interact with the surrounding equipment"""

    def __init__(self):
        pass

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

    def release(self):
        """Releasses attached devices, so that a restart is possible"""
        pass