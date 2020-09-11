# -*- coding: utf-8 -*-
"""
Created on Sun Jan 06 12:21:25 2013

@author: scheidt
"""

from smt_cal_demo.calibration.environments.fluke5500e_v01 import Environment
from smt_cal_demo.calibration.dut.generic_manual_v01 import DUT
from smt_cal_demo.calibration.procedures.execute_calibration_v2 import execute_calData
from smt_cal_demo.calibration.database.support import session,Calibration,Instrument,Measurement
from smt_cal_demo.calibration.calibration_data.fluke.fluke175 import calData

info = """
Measuring points and specification points according to performance test decribed in Fluke calibration manual
"""

def sequence():
    #cal_started = session.query(Calibration).filter(Calibration.id==4295022593).one()
    cal_started = None
    
    environment = Environment()
    dut = DUT()
        
    calibration = execute_calData(calData, dut, environment, calibration = cal_started)
    
    dut.test_finished()
    environment.switch_to_safe_state()


if __name__ == '__main__':
    sequence()