# -*- coding: utf-8 -*-
"""
Created on Wed Jan 02 09:32:54 2013

@author: Scheidt
"""

import numpy as np

import devices.fluke5500e_v01 as fluke5500e

import models.direct.direct_stimulate_ac_voltage_m01_v01 as ns_model
import models.support_v01
import tokens.electrical_properties as c_el
import tokens.device_functions as c_fct
import tokens.physical_units as c_phy
import tokens.testpoint_keys as c_tst
import tokens.reporting as c_rpt
from models.support_v01 import Var

func = fluke5500e.Volt_AC(None)

range_names = [x for x in list(func.ranges.keys()) if x!="_format"]
range_names.sort(cmp=lambda x,y:0 if float(x)==float(y) else -1 if float(x)<float(y) else 1)

model = ns_model.Model()  

low_value = None

for range_name in range_names:
    range_data = func.ranges[range_name]

    try:
        finterval = func.baseSpec1yr[range_name]["finterval"]    
    except:
        pass
    
    try:
        finterval = func.basespec1yr_ana[range_name]["finterval"]    
    except:
        pass   

    high_value = range_data["<max"] * 0.99
    if low_value is None:
        low_value = 0.05* high_value
    else:
        low_value = 0.1 * high_value

    print(("Range:{:s} {:.3e} {:.3e}".format(range_name,low_value,high_value)))     
        
    for k in range(len(finterval)-1):

        low_f = finterval[k]
        high_f = finterval[k+1]
        frequency = low_f + 0.99 * ( high_f - low_f)
        
        
        el_properties = func.get_el_properties(high_value,func.settings)

        model.frequency.v = frequency
        model.frequency.u = 1e-3 * model.frequency.v        
        model.c_p_dut.v = 100e-12
        model.c_p_dut.u = 2*0.289*50e-12
        model.r_p_dut.v = 1e6
        model.r_p_dut.u = 2 * 0.289 * 0.5e6
        model.r_s_cal = el_properties[c_el.R_s]
        model.c_leads.v = 50e-12
        model.c_leads.u = 0.289 * 2 * 0.5 * model.c_leads.v       
        model.l_leads.v = 1e-6
        model.l_leads.u = 0.289 * 2 * 0.5 * model.l_leads.v       

        model.d_x_drift.u = 0.5 * func.uncertainty(low_value, frequency, high_value, func.settings)
        model.x.v = low_value
        model.y.v = low_value
        model.d_y_drift.u = 10e-6 * model.y.v
        
        unc_low = 2 * models.support_v01.calculate_unc(model)
                
        el_properties = func.get_el_properties(high_value,func.settings)

        model.d_x_drift.u = 0.5 * func.uncertainty(high_value, frequency, high_value, func.settings)
        model.x.v = high_value
        model.y.v = high_value
        model.d_y_drift.u = 10e-6 * model.y.v
                
        unc_high = 2 * models.support_v01.calculate_unc(model)
        
        stg = (unc_high - unc_low)/(high_value - low_value)
        
        offset = unc_high - stg *  high_value       
    
        print(("{:12.2f} - {:12.2f}  : {:9.1e} + {:9.1e} [{:6.2g},{:6.2g}]".format(low_f,high_f,stg,offset,unc_low,unc_high)))
    
    
frequency = 500e3
sample_value = 0.3

el_properties = func.get_el_properties(sample_value,func.settings)

model.frequency.v = frequency
model.frequency.u = 1e-3 * model.frequency.v        
model.c_p_dut.v = 100e-12
model.c_p_dut.u = 2*0.289*50e-12
model.r_p_dut.v = 1e6
model.r_p_dut.u = 2 * 0.289 * 0.1e6
model.r_s_cal = el_properties[c_el.R_s]
model.c_leads.v = 50e-12
model.c_leads.u = 0.289 * 2 * 0.5 * model.c_leads.v       
model.l_leads.v = 1e-6
model.l_leads.u = 0.289 * 2 * 0.5 * model.l_leads.v       

model.d_x_drift.u = 0.5 * func.uncertainty(sample_value, frequency, sample_value, func.settings)
model.x.v = sample_value
model.y.v = sample_value
model.d_y_drift.u = 10e-6 * model.y.v
print() 
print((models.support_v01.calculate_unc_and_print_model(model)))
print((model.f()))
