# -*- coding: utf-8 -*-
"""
Created on Wed Jan 02 11:17:01 2013

@author: Scheidt
"""

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
   
    
class Model(Direct_Base_Model):
    
    def __init__(self):
        super(Model,self).__init__()

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

        
        zw = xc - yc
        
        return zw

class ModelTest(unittest.TestCase):
    
    def test(self):
        m=create_sample()
        self.assertAlmostEqual(m.f(),0, places=4)
   
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
    m.x.v = 1
    m.y.v = 1
    return m
        
if __name__ == '__main__':
    unittest.main(exit=False)

