# -*- coding: utf-8 -*-
"""
Created on Wed Jan 02 09:03:05 2013

@author: Scheidt
"""
import numpy as np

import unittest
from smt_cal_demo.calibration.models.support_v01 import Var
import smt_cal_demo.calibration.tokens.physical_units as c_phy

class Direct_Base_Model(object):

    def __init__(self):
        unit = c_phy.V
        self.x = Var(0., 0., unit, "Set value on calibrator")
        self.d_x_disp = Var(0., 0., unit, "correction due to display resolution")        
        self.d_x_corr = Var(0., 0., unit, "correction based on calibration")        
        self.d_x_drift = Var(0., 0, unit, "time dependent correction. Stability of instrument")
        self.y = Var(0., 0., unit, "Indication of device under test")
        self.d_y_disp = Var(0., 0., unit, "correction due to display resolution")        
        self.d_y_corr = Var(0., 0., unit, "correction based on calibration")        
        self.d_y_drift = Var(0., 0., unit, "time dependent correction. Stability of instrument")
   
    
class Model(Direct_Base_Model):
    
    def __init__(self):
        super(Model,self).__init__()
        self.c_p_dut = Var(0., 0., c_phy.F, "parallel capacity of dut input")
        self.r_p_dut = Var(0., 0., c_phy.Ohm, "parallel resistivity of DUT")
        self.c_leads = Var(0., 0., c_phy.F, "additional parallel capacity by wiring")
        self.l_leads = Var(0., 0., c_phy.H, "inductivity of wires")
        self.r_s_cal = Var(0., 0., c_phy.Ohm, "internal resistance of voltage source")
        self.frequency = Var(0., 0., c_phy.Hz, "frequency of applied voltage")

    def f(self):
        xc = (self.x.v
                + self.d_x_disp.v
                + self.d_x_corr.v
                + self.d_x_drift.v 
                )
        yc = (self.y.v
                + self.d_y_disp.v
                + self.d_y_corr.v
                + self.d_y_drift.v)

        j = np.complex(0,1)
        om = 2 * np.pi * self.frequency.v
        z = 1 / (1/self.r_p_dut.v + j * om * (self.c_p_dut.v + self.c_leads.v))

        s = z * xc/ (self.r_s_cal.v + j * om * self.l_leads.v + z)
        
        zw = np.abs(s) - yc
        
        return zw

class ModelTest(unittest.TestCase):
    
    def test(self):
        m=create_sample()
        self.assertAlmostEqual(m.f(),0.000427843721, places=4)
   
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
    m.l_leads.v = 1e-6
    m.l_leads.u = 0.1 * 1e-6
    m.r_s_cal.v = 50
    m.r_s_cal.u = 5
    m.c_p_dut.v = 140e-12
    m.c_p_dut.u = 0.1 * 140e-12
    m.frequency.v = 500e3
    m.frequency.u = 1e-3 * m.frequency.v
    m.r_p_dut.v = 10e6
    m.r_p_dut.u = 0.1 * m.r_p_dut.v 
    m.x.v = 0.3
    m.y.v = 0.3
    return m
        
if __name__ == '__main__':
    unittest.main(exit=False)

