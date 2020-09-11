# -*- coding: utf-8 -*-
"""
Created on Wed Jan 02 12:42:03 2013

@author: Scheidt
"""
import numpy as np

import unittest
from smt_cal_demo.calibration.models.support_v01 import Var
import smt_cal_demo.calibration.tokens.physical_units as c_phy

class Direct_Base_Model(object):

    def __init__(self):
        unit = c_phy.A
        self.x = Var(0., 0., unit, "Set value on calibrator")
        self.d_x_disp = Var(0., 0., unit, "correction due to display resolution")        
        self.d_x_corr = Var(0., 0., unit, "correction based on calibration")        
        self.d_x_drift = Var(0., 0, unit, "time dependent correction. Stability of instrument")
        self.y = Var(0., 0., unit, "Indication of device under test")
        self.d_y_disp = Var(0., 0., unit, "correction due to display resolution")        
        self.d_y_corr = Var(0., 0., unit, "correction based on calibration")        
        self.d_y_drift = Var(0., 0., unit, "time dependent correction. Stability of instrument")
        self.scaling = Var(1., 0., unit, "scaling factor applied to the indication of the DUT")
   
    
class Model(Direct_Base_Model):
    
    def __init__(self):
        super(Model,self).__init__()
        self.c_p_dut = Var(0., 0., c_phy.F, "parallel capacity of dut input")
        self.r_p_dut = Var(0., 0., c_phy.Ohm, "parallel resistivity of DUT")
        self.c_leads = Var(0., 0., c_phy.F, "additional parallel capacity by wiring")
        self.frequency = Var(0., 0., c_phy.Hz, "frequency of applied current")

    def f(self):
        xc = (self.x.v
                + self.d_x_disp.v
                + self.d_x_corr.v
                + self.d_x_drift.v 
                )
        yc = (self.y.v
                + self.d_y_disp.v
                + self.d_y_corr.v
                + self.d_y_drift.v)*self.scaling.v

        j = np.complex(0,1)
        om = 2 * np.pi * self.frequency.v
        z = 1 / (1/self.r_p_dut.v + j * om * (self.c_p_dut.v + self.c_leads.v))

        s = xc* z / self.r_p_dut.v
        
        zw = np.abs(s) - yc
        
        return zw

class ModelTest(unittest.TestCase):
    
    def test(self):
        m=create_sample()
        self.assertAlmostEqual(m.f(),-7.1258467604362608e-07, places=4)
   
def create_sample():
    m = Model()
    m.d_x_corr.v = 0.
    m.d_x_disp.v = 0.
    m.d_x_drift.v = 0.
    m.d_x_drift.u = 0.
    m.d_y_corr.v = 0.
    m.d_y_disp.v = 0.
    m.d_y_drift.v = 0.        
    m.d_y_drift.u = 0.
    m.c_leads.v = 50e-12
    m.c_leads.u = 0.1*50e-12
    m.c_p_dut.v = 140e-12
    m.c_p_dut.u = 0.1 * 140e-12
    m.frequency.v = 100e3
    m.frequency.u = 1e-3 * 100e3
    m.r_p_dut.v = 10
    m.r_p_dut.u = 0.1 * 10
    m.x.v = 1
    m.y.v = 1
    return m
        
if __name__ == '__main__':
    unittest.main(exit=False)

