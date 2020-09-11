# -*- coding: utf-8 -*-
"""
Created on Mon Jan 07 13:23:26 2013

@author: scheidt
"""
import unittest
from smt_cal_demo.calibration.models.support_v01 import Var
import smt_cal_demo.calibration.tokens.physical_units as c_phy

class Model(object):

    def __init__(self,unit):
        self.x = Var(None, 0., unit, "Indication of multimeter")
        self.d_x_disp = Var(0., 0., unit, "correction due to display resolution")        
        self.d_x_corr = Var(0., 0., unit, "correction based on calibration")        
        self.d_x_drift = Var(0, 0, unit, "time dependent correction. Stability of instrument")
                
    
    def f(self):
        zw = (self.x.v
                + self.d_x_disp.v
                + self.d_x_corr.v
                + self.d_x_drift.v 
                )
        return zw
    
        
class ModelTest(unittest.TestCase):
    
    def test(self):
        m=create_sample()
        self.assertAlmostEqual(m.f(), 1.1, places=4)
   
def create_sample():
    m = Model("A")
    m.d_x_corr.v = 0.1
    m.d_x_disp.v = 0.
    m.d_x_drift.v = 0.
    m.x.v = 1
    return m
        
if __name__ == '__main__':
    unittest.main(exit=False)

