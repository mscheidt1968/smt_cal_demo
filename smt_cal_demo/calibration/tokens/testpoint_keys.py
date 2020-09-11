# -*- coding: utf-8 -*-
"""
Created on Sun Dec 30 10:29:46 2012

@author: Scheidt
"""

# testpoint constants
range = "range"
charge = "charge"
voltage = "voltage"
voltage_offset = "voltage_offset"
source_voltage = "source_voltage"
scale_voltage = "scale_voltage"
limit_voltage = "limit_voltage"
current = "current"
limit_current = "limit_current"
frequency = "frequency"
upper_frequency = "upper_frequency"
lower_frequency = "lower_frequency"
frequencies = "frequencies"
capacitance = "capacitance"
resistance = "resistance"
resistance1 = "resistance1"
resistance2 = "resistance2"
temperature = "temperature"
power = "power"
powers = "powers"
position = "position"
orientation = "orientation"
orientations = "orientations"
winding_count = "winding_count"
conversion_factor = "conversion_factor"
channel = "channel"
part = "part"
gate_time = "gate_time"
time_interval = "time_interval"
period = "period"
pulse_width = "pulse_width"
power_factor = "power_factor"
report_type = "report_type"
dut_stability_abs = "dut_stability_abs"
dut_stability_rel = "dut_stability_rel"
harmonic_number = "harmonic_number"
harmonic_content = "harmonic_content"
location = "location"

# processing instruction constants
count = "count" # defines number of readings for a measurment
delay = "delay" # number of seconds to wait after applying a stimulus before a reading should be done
skip = "skip" #number of measurements to be done in advance
sub_function = "sub_function" # enables different configuration 
scale_disp = "scale_disp" # avalue to be multiplied on indication entry
scaling = "scaling" # a factor which is applied after measurement e.g. conversion from Volts to Amps
fixed_res = "fixed_res" # use fixed resistances instead emulated
pre_measure_values = "pre_measure_values"
stimulus = "stimulus"
no_thermal_dut = "no_thermal_dut"
current_source = "current_source"

current_transducer = "current_transducer"
shunt = "shunt"
primary_side_shunt = "primary_side_shunt"
secondary_side_shunt = "secondary_side_shunt"
environment = "environment"
dut = "dut"

nominal_voltage_ratio = "nominal_voltage_ratio"
nominal_current_ratio = "nominal_current_ratio"

sample_count = "sample_count"

report_dut_indication = "report_dut_indication"

trigger_level = "trigger_level"
trigger_delay = "trigger_delay"
