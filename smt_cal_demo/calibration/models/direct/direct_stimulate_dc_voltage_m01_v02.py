# -*- coding: utf-8 -*-
"""
Created on Mon Dec 31 18:06:49 2012

@author: Scheidt
"""

import unittest
from smt_cal_demo.calibration.models.support_v01 import Var
import smt_cal_demo.calibration.tokens.physical_units as c_phy

class Model(object):
    
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

        self.u_thermo = Var(0., 0, c_phy.V , "thermal voltage within circuit")
        self.r_p_dut = Var(0., 0, c_phy.Ohm, "internal resistance of meter under test")
        self.r_leads = Var(0., 0., c_phy.Ohm, "resistance of wires")
        self.r_s_cal = Var(0., 0., c_phy.Ohm, "internal resistance of voltage source")
        super(Model,self).__init__()
    
    def f(self):
        x_c = ( self.x.v
                + self.d_x_disp.v
                + self.d_x_corr.v
                + self.d_x_drift.v 
                )
        y_c = ( self.y.v
                + self.d_y_disp.v
                + self.d_y_corr.v
                + self.d_y_drift.v)

        zw = x_c + self.u_thermo.v
        zw += (self.r_s_cal.v + self.r_leads.v) / (self.r_p_dut.v + self.r_s_cal.v + self.r_leads.v) * self.x.v
        return (zw - y_c, zw)
        

class ModelTest(unittest.TestCase):
    
    def test(self):
        m=create_sample()
        self.assertAlmostEqual(m.f()[0],1.0009999e-7, places=4)
   
def create_sample():
    m = Model()
    m.u_thermo.v = 0
    m.u_thermo.u = 0.289 * 2 * 1e-6
    m.d_x_corr.v = 0.
    m.d_x_disp.v = 0.
    m.d_x_drift.v = 0.
    m.d_x_drift.u = 0.
    m.d_y_corr.v = 0.
    m.d_y_disp.v = 0.
    m.d_y_drift.v = 0.        
    m.d_y_drift.u = 0.
    m.r_leads.v = 0.043
    m.r_leads.u = 0.289 * 2 * 10e-3
    m.r_p_dut.v = 10e6
    m.r_s_cal.v = 50
    m.x.v = 1
    m.y.v = 1
    return m
        
if __name__ == '__main__':
    m = create_sample()
    print((m.f()))
    unittest.main(exit=False)

