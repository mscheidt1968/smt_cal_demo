# -*- coding: utf-8 -*-
"""
Created on Wed Nov 07 19:53:04 2012

@author: Scheidt
"""

calData = str("""
0: manufacturer: Fluke, model:175
    +count:1  
    +environment: environments.fluke5500e_v01
    +dut: dut.generic_manual_v01
    +spec: Fluke 17X Calibration Manual PN 1600476 March 2001 Rev.5, 2/08

    1: test: Visual inspection
        +procedure: special.visual_inspection_m02_v01
        *parameter: none

    1: test: AC Voltage Verification, Function: volt_ac
        +procedure: direct.stimulate_voltage_ac_m01_v01
        +@C_p:140e-12 14e-12 F, +@R_p: 10e6 1e6 Ohm
            <testvar: result.v
            voltage: 300e-3,+scale_disp:1e-3
                *frequency: 45
                <abs: 3.3e-3
            voltage: 5,+scale_disp:1
                *frequency: 500
                <abs: 0.053
                *frequency: 1e3
                <abs: 0.103
            voltage: 50
                *frequency: 45
                <abs: 0.53
                *frequency: 1e3
                <abs: 1.03
            voltage: 300
                *frequency: 45
                <abs: 3.3
            voltage: 500
                *frequency: 500
                <abs: 5.3
                *frequency: 1e3
                <abs: 10.3
            voltage: 1e3
                *frequency: 45
                <abs: 0.013e3
        

    1: test: AC Volts Frequency, Function: frequ, sub_function: ACV
        +procedure: direct.stimulate_frequency_m01_v01
            <testvar: result.v
            *voltage: 1, frequency:45, +scale_disp:1
            <abs: 0.06
            *voltage: 1, frequency:50e3, +scale_disp:1e3
            <abs: 0.06e3

    1: test: DC Voltage Verification, Function: volt_dc, sub_function: V
        +procedure: direct.stimulate_voltage_dc_m01_v01
        +@R_p: 10e6 1e6 Ohm
            <testvar: result.v
            *voltage: 5
                <abs: 0.010
            *voltage: 300
                <abs: 0.7
            *voltage: 1000
                <abs: 4
            *voltage: -1000
                <abs: 4


    1: test: DC Volts Frequency, Function: frequ, sub_function: DCV
        +procedure: direct.stimulate_frequency_m01_v01
            <testvar: result.v
            *voltage: 3, frequency:45, +scale_disp:1
            <abs: 0.06
            *voltage: 30, frequency:50e3, +scale_disp:1e3
            <abs: 0.06e3

                
    1: test: DC Voltage Verification, Function: volt_dc, sub_function: mV
        +procedure: direct.stimulate_voltage_dc_m01_v01
        +scale_disp: 1e-3
        +@R_p: 10e6 1e6 Ohm
            <testvar: result.v
            *voltage: 3e-2
                <abs: 0.02e-2
            *voltage: -3e-1
                <abs: 0.007e-1
            *voltage: 6e-1
                <abs: 0.011e-1

    1: test: Capacitance Verification, Function: cap
        +procedure: direct.stimulate_capacitance_m01_v01
            <testvar: result.v
            *capacitance: 0.9e-6, +scale_disp: 1e-9
                <abs: 13e-9
    

    1: test: Resistance Verification, Function: res_2w
        +procedure: direct.stimulate_resistance_m01_v01
            <testvar: result.v
            *resistance: 500, +scale_disp: 1, +@I_meas: 1e-3 0.1e-3 A, +@R_p: 10e6 1e6 Ohm
                <abs: 4.7
            *resistance: 19e6, +scale_disp: 1e6, +@I_meas: 1e-6 0.1e-6 A, +@R_p: 10e6 1e6 Ohm
                <abs: 0.32e6

    1: test: Continuity, Function: continuity
        +procedure: special.test_beeper_m01_v01
            <testvar: answer
            *resistance: 25
            <equal: yes
            <testvar: answer
            *resistance: 250
            <equal: no

    1: test: Diode, Function: diode 
        +procedure: direct.stimulate_voltage_dc_m01_v01
            <testvar: result.v
            *voltage: 2, +scale_disp:1, +@R_p:10e6 1e6 Ohm
            <abs: 0.022

                
    1: test: AC Current Verification, Function: curr_ac, sub_function:mA
        +procedure: direct.stimulate_current_ac_m01_v01
        +@C_p:140e-12 14e-12 F, +@R_p: 1 1 Ohm
            <testvar: result.v
            current: 3e-3, +scale_disp:1e-3
                *frequency: 45
                <abs: 0.08e-3
            current: 50e-3,+scale_disp:1e-3
                *frequency: 1e3
                <abs: 0.78e-3
            current: 4e-1,+scale_disp:1e-3
                *frequency: 1e3
                <abs: 6.3e-3

    1: test: DC Current Verification, Function: curr_dc, sub_function:mA
        +procedure: direct.stimulate_current_dc_m01_v01
        +@R_p: 1 1 Ohm
            <testvar: result.v
            *current: 3e-3,+scale_disp:1e-3
                <abs: 0.06e-3
            *current: 5e-2,+scale_disp:1e-3
                <abs: 0.053e-2
            *current: -4e-1,+scale_disp:1e-3
                <abs: 6.3e-3
                

    1: test: AC Current Verification, Function: curr_ac, sub_function:A
        +procedure: direct.stimulate_current_ac_m01_v01
        +@C_p:140e-12 14e-12 F, +@R_p: 10e-3 1e-3 Ohm
            <testvar: result.v
            current: 4,+scale_disp:1
                *frequency: 45
                <abs: 0.063
            current: 9,+scale_disp:1
                *frequency: 1e3
                <abs: 0.17

    1: test: DC Current Verification, Function: curr_dc, sub_function:A
        +procedure: direct.stimulate_current_dc_m01_v01
        +@R_p: 10e-3 1e-3 Ohm
            <testvar: result.v
            *current: 4,+scale_disp:1
                <abs: 0.043
            *current: -9,+scale_disp:1
                <abs: 0.12
""")