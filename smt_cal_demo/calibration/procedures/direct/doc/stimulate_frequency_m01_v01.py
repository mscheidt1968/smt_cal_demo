# -*- coding: utf-8 -*-
"""
Created on Sun Jan 06 19:43:43 2013

@author: Scheidt
"""

import numpy as np

import devices.fluke5500e_v01 as fluke5500e

import models.direct.direct_stimulate_frequency_m01_v01 as ns_model
import models.support_v01
import tokens.electrical_properties as c_el
import tokens.device_functions as c_fct
import tokens.physical_units as c_phy
import tokens.testpoint_keys as c_tst
import tokens.reporting as c_rpt
from models.support_v01 import Var

func = fluke5500e.Volt_AC(None)
model = ns_model.Model()  

stability_dut = 10e-6
for f in [0.1,10,100,1e3,10e3,100e3,500e3]:
    
    model.d_x_drift.u = 0.5 * func.uncertainty_f(f)
    model.x.v = f
    model.y.v = f
    model.d_y_drift.u = stability_dut * model.y.v
    
    unc = 2 * models.support_v01.calculate_unc(model)
    
    print(("{:12f} {:9.3f} {:6.2g}".format(f,unc/f*1e6,unc)))

f = 100e3
model.d_x_drift.u = 0.5 * func.uncertainty_f(f)
model.x.v = f
model.y.v = f
model.d_y_drift.u = stability_dut * model.y.v
print((models.support_v01.calculate_unc_and_print_model(model)))
print((model.f()))
