# -*- coding: utf-8 -*-
"""
Created on Wed Jan 02 14:15:42 2013

@author: Scheidt
"""

import unittest
from smt_cal_demo.calibration.models.support_v01 import Var
import smt_cal_demo.calibration.tokens.physical_units as c_phy

class Direct_Base_Model(object):

    def __init__(self):
        unit = c_phy.Ohm
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
        self.u_thermo = Var(0., 0., c_phy.V , "thermal voltage within circuit")
        self.i_meas = Var(0., 0., c_phy.A, "measuring curremt")
        self.r_leads = Var(0., 0., c_phy.Ohm, "resistance of wires and contacts")

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

        s = self.r_leads.v + self.u_thermo.v / self.i_meas.v 
        zw = xc + s - yc
        
        return zw

class ModelTest(unittest.TestCase):
    
    def test(self):
        m=create_sample()
        self.assertAlmostEqual(m.f(),0.01577999999, places=4)
   
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
    
    m.i_meas.v = 1e-3
    m.i_meas.v = 0.1 * 1e-3 * 2 * 0.289
    m.r_leads.v = 0.1
    m.r_leads.v = 0.1 * 0.1 * 2 * 0.289
    m.u_thermo.v = 0
    m.u_thermo.v = 2 * 0.289 * 1e-6
    m.x.v = 1
    m.y.v = 1
    return m
        
if __name__ == '__main__':
    unittest.main(exit=False)

