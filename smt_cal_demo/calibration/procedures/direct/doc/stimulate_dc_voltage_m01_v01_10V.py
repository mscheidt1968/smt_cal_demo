# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 20:12:32 2015

@author: Scheidt
"""

import scipy as sci
import reporting.uncertainty.uncertainty_report as unc
import models.direct.direct_stimulate_dc_voltage_m01_v02 as mod
import devices.agilent.hp3458a_v02 as ns_dev
import tokens.execution_modes as c_exm

from models.support_v01 import Var, calculate_unc_mv


c_exm.execution_mode.add(c_exm.no_io)
unc_rep = unc.UncertaintyReport("stimulate_voltage_dc_m01_v02_10V")
unc_rep.method_info = "Stimulation of DUT with a precise 10V DC voltage source"

for voltage in [10]:
        m = mod.Model()
        m.u_thermo.v = 0
        m.u_thermo.u = 0.289 * 2 * 0.2e-6
        m.x.v = voltage
        m.d_x_corr.v = 0.
        m.d_x_corr.u = 0.1e-6 * m.x.v / 2
        m.d_x_disp.v = 0.
        m.d_x_disp.u = 0.
        m.d_x_drift.v = 0.
        m.d_x_drift.u = 2 * 0.289 * 2e-6 * m.x.v
        m.y.v = voltage
        m.d_y_corr.v = 0.
        m.d_y_corr.v = 0.
        m.d_y_disp.v = 0.
        m.d_y_disp.v = 0.
        m.d_y_drift.v = 0.        
        m.d_y_drift.v = 0.        
        m.d_y_drift.u = 0.
        m.d_y_drift.u = 0.1e-6 * m.y.v
        m.r_leads.v = 0.050
        m.r_leads.u = 0.289 * 2 * 1e-3
        m.r_p_dut.v = 10e6
        m.r_p_dut.u = 1
        m.r_s_cal.v = 1
        m.r_s_cal.u = 0.1
                        
        
        detailed_spec = list()
        result = m.f()
        unc_1x = calculate_unc_mv(m, output=detailed_spec)[0]
        spec = ["U", "{:.3f}".format(m.x.v),
                "",
                "{:.1f} ppm".format(2 * unc_1x / m.x.v * 1e6 ),
                "",
                ""]
        last_line = ["d_U","Correction of U",result[0], unc_1x]
        unc_rep.add_specification(spec,detailed_spec[0],last_line)

unc_rep.create_pdf()        


if __name__=="__main__":
    pass
