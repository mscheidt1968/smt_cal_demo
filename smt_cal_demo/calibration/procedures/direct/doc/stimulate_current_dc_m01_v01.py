# -*- coding: utf-8 -*-
"""
Created on Wed Jan 02 11:28:01 2013

@author: Scheidt
"""

import numpy as np

import devices.fluke5500e_v01 as fluke5500e
import numpy as np

import models.direct.direct_stimulate_dc_current_m01_v01 as ns_model
import models.support_v01
import tokens.electrical_properties as c_el
import tokens.device_functions as c_fct
import tokens.physical_units as c_phy
import tokens.testpoint_keys as c_tst
import tokens.reporting as c_rpt
from models.support_v01 import Var

func = fluke5500e.Cur_DC(None)

range_names = [x for x in list(func.ranges.keys()) if x!="_format"]
range_names.sort(cmp=lambda x,y:0 if float(x)==float(y) else -1 if float(x)<float(y) else 1)

model = ns_model.Model()  



low_value = None
stability_dut = 10e-6
for range_name in range_names:
    range_data = func.ranges[range_name]


    high_value = range_data["<max"]*0.99
    if low_value is None:
        low_value = range_data["min"]
    else:
        low_value = 0.1 * high_value

        
    el_properties = func.get_el_properties(high_value,func.settings)
    
    model.d_x_drift.u = 0.5*func.uncertainty(low_value, high_value, func.settings)
    model.x.v = low_value
    model.y.v = low_value
    model.d_y_drift.u = stability_dut * model.y.v
    
    unc_low = 2*models.support_v01.calculate_unc(model)
            
    el_properties = func.get_el_properties(high_value,func.settings)

    model.d_x_drift.u = 0.5*func.uncertainty(high_value, high_value, func.settings)
    model.x.v = high_value
    model.y.v = high_value
    model.d_y_drift.u = stability_dut * model.y.v
            
    unc_high = 2*models.support_v01.calculate_unc(model)
    
    stg = (unc_high - unc_low)/(high_value - low_value)
    
    offset = unc_high - stg *  high_value       

    print(("Range:{:>8s} {:8.3e} {:8.3e}  : {:9.1e} + {:9.1e} [{:6.2g},{:6.2g}]".format(range_name,low_value,high_value,stg,offset,unc_low,unc_high)))
    
    

sample_value = 1e-3
el_properties = func.get_el_properties(sample_value,func.settings)

model.d_x_drift.u = 0.5*func.uncertainty(sample_value, sample_value, func.settings)
model.x.v = sample_value
model.y.v = sample_value
model.d_y_drift.u = stability_dut * model.y.v

print((models.support_v01.calculate_unc_and_print_model(model)))
print((model.f()))
