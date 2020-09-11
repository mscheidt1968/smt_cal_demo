# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 15:00:03 2012

@author: Scheidt
"""

class TestPointError(Exception):
    pass

def create_dict(a):
    """Creates from a string a dictionary"""
    # special casse messages with text and commas 27.3.2014
    if a.split(":")[0] == "+message":
        zw=dict()
        zw["+message"] = a.split(":")[1].lstrip().rstrip()
    elif a.split(":")[0] == "location":
        zw=dict()
        zw["location"] = a.split(":")[1].lstrip().rstrip()
    elif a.split(":")[0] == "+explanation":
        zw=dict()
        zw["+explanation"] = a.split(":")[1].lstrip().rstrip()
    elif a.split(":")[0] == "+spec":
        zw=dict()
        zw["+spec"] = a.split(":")[1].lstrip().rstrip()
    else:
        zw=dict()    
        l1=a.split(",")
        for item in l1:
            if item != "":
                l2=item.split(":",1)
                if l2.__len__()==2:
                    value = l2[1].lstrip().rstrip()
                    l2[0]=l2[0].rstrip().lstrip()
                    try:
                        zw[l2[0]]=value
                        zw[l2[0]]=float(value)
                        zw[l2[0]]=int(value)
                    except:
                        pass
                
    return zw
                
def combine_dicts_to_one(list_of_dicts):
    zw = dict()
    for dict_item in list_of_dicts:
        if dict_item.__len__()>0:
            for key, item in dict_item.items():
                zw[key]=item
    return zw


def process_cal_spec(cal_spec):
    calData=cal_spec.replace("\t","    ")
    cal_data = calData.split("\n")
    
    
    test_ids = list()
    test_points = dict()
    proc_instrs=dict()
    specs = dict()    
    
    current_test_point_parameters=[dict()]
    current_proc_inst_parameters=[dict()]
    current_spec_parameters=[dict()]
    last_test_point_id = None
    
    level=0
    
    for al in cal_data:
        alstripped=al.lstrip(" ")
        if alstripped.__len__()>2:
            if alstripped[0] in frozenset(["0","1","2","3","4","5","6","7","8","9"]):
                level = int(alstripped[0])
                current_test_point_parameters=current_test_point_parameters[0:level]
                current_test_point_parameters.append(dict())
                current_proc_inst_parameters=current_proc_inst_parameters[0:level]
                current_proc_inst_parameters.append(dict())
                if not last_test_point_id is None:
                    specs[last_test_point_id] = combine_dicts_to_one(current_spec_parameters)
                    last_test_point_id = None
                current_spec_parameters=current_spec_parameters[0:level]
                current_spec_parameters.append(dict())
                alstripped = alstripped[2:].lstrip(" ")
            
            create_testpoint = False
            if alstripped[0] == "*":
                create_testpoint = True
                alstripped = alstripped[1:].lstrip(" ")
    
            line_parameters = create_dict(alstripped)
    
            for key,item in line_parameters.items():
                if key[0] == "<":
                    token = key[1:]
                    current_spec_parameters[level][token] = item
                elif key[0] == "+":
                    current_proc_inst_parameters[level][key[1:]] = item
                else:
                    current_test_point_parameters[level][key] = item
            
            if create_testpoint == True:
                test_id = combine_dicts_to_one(current_test_point_parameters).__str__()
                if test_id in test_points:
                    raise TestPointError("Test point: " + test_id +" already defined") 
                test_points[test_id] = combine_dicts_to_one(current_test_point_parameters)
                proc_instrs[test_id] = combine_dicts_to_one(current_proc_inst_parameters)
                if not last_test_point_id is None:            
                    specs[last_test_point_id] = combine_dicts_to_one(current_spec_parameters)
                if "abs" in current_spec_parameters[level]:                    
                    del(current_spec_parameters[level]["abs"]) 
                if "rel" in current_spec_parameters[level]:
                    del(current_spec_parameters[level]["rel"]) 
                if "abs_y_max" in current_spec_parameters[level]:
                    del(current_spec_parameters[level]["abs_y_max"]) 
                if "between_no_marg" in current_spec_parameters[level]:
                    del(current_spec_parameters[level]["between_no_marg"]) 
                if "between" in current_spec_parameters[level]:
                    del(current_spec_parameters[level]["between"]) 
                last_test_point_id = test_id
                test_ids.append(test_id)
                
    if not last_test_point_id is None:            
        specs[last_test_point_id] = combine_dicts_to_one(current_spec_parameters)

        
    return [test_ids, test_points, proc_instrs,specs]
    
if __name__ == '__main__':
    calData = str("""
0: manufacturer: Agilent, model:3458A
    1: test: general
        *+procedure: hp3458_general_test_v1
    1: test: offset test, function: volt_dc
        +message: apply short, and wait for 5 minutes
        +explanation: this is a test @90degress, no error?
        +procedure: measure_offset_voltage_v1
        *range: 0.1
        <abs: 0.00106e-3
        *range: 1
        <abs: 0.00000106
        *range: 10
        <abs: 0.0000023
        *range: 100
        <abs: 0.000036
        *range: 1000
        <abs: 0.00010
    1: test: gain tests, function: volt_dc
        +procedure: calibrate_voltage_dc_direct_v1
            range: 0.1
                *voltage: 0.1
                <abs: 0.00212e-3
            range: 1
                *voltage: 1
                <abs: 0.00000998
            range: 10
                *voltage: 1
                <abs: 0.0000111
                *voltage: -1
                <abs: 0.0000111
                *voltage: -10
                <abs: 0.0000892
                *voltage: 10
                <abs: 0.0000892
            range: 100
                *voltage: 100
                <abs: 0.001114
            range: 1000
                *voltage: 1000
                <abs: 0.02396

""")

    calData = str("""
0: +environment: environments.agilent_hp3458a_v01
+dut: dut.agilent3458a
    
0:  manufacturer: Fluke, model:289
    +count:1  


    1: test: AC Verification V AC Function, Function: volt_ac
        +procedure: direct.stimulate_voltage_ac_m01_v01
        +@C_p:140e-12 14e-12 F, +@R_p: 10e6 1e6 Ohm
            +message: Switch to Volt AC Function
            +scale_disp: 1
            range: 5
            *voltage: 0.1, frequency: 60
                <testvar: result.v
                <abs: 0.0048
            *voltage: 0.5, frequency: 10e3
                <abs: 0.0055
                <testvar: result_x.v
            *voltage: 3, frequency: 100e3
                <testvar: result.v
                <abs: 0.184

            range: 50
            *voltage: 15, frequency: 100e3
                <abs: 0.565

            +message: Activate low pass function for following test
            *voltage: 50, frequency: 60
                <abs: 1.4
            *voltage: 50, frequency: 1600
                <between_no_marg: 42 50
            
            +message: Switch low pass function off
            range: 500
            *voltage: 500, frequency: 10e3
                <abs: 2.25
            
            range: 1000
            *voltage: 1000, frequency: 10e3
                <abs: 6.5
            
            range: 1000
            voltage: 1000, frequency: 5e3
            *location: dies ist ein, kommas test
                <abs: 6.5

""")

    [test_ids,test_points,processing_instructions,specs] = process_cal_spec(calData)            

    print(test_ids[0].__str__()) 
    print(processing_instructions[test_ids[0]].__str__())
    print(specs[test_ids[0]].__str__())    