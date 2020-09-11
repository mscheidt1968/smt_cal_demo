# -*- coding: utf-8 -*-
"""
Created on Sun Nov 04 15:55:24 2012

@author: Scheidt
"""
import smt_cal_demo.utilities.easygui as eg

class ProcessingInstructionError(Exception):
    pass

def manual_entry(test_point_data = dict(), processing_instructions = dict()):
    """A manual entry of an indication. Plausibility ist tested against expected value"""
    indications = list()
    indication_prefix = 1
    if "indication_prefix" in processing_instructions:
        if processing_instructions["indication_prefix"] == "f":
            indication_prefix=1e-12
        elif processing_instructions["indication_prefix"] == "n":
            indication_prefix=1e-9
        elif processing_instructions["indication_prefix"] == "u":
            indication_prefix=1e-6
        elif processing_instructions["indication_prefix"] == "m":
            indication_prefix=1e-3
        elif processing_instructions["indication_prefix"] == "k":
            indication_prefix=1e3
        elif processing_instructions["indication_prefix"] == "M":
            indication_prefix=1e6
        elif processing_instructions["indication_prefix"] == "G":
            indication_prefix=1e9

    cnt = 1
    if "count" in processing_instructions:
        try:
            cnt = int(processing_instructions["count"])
        except:
            raise ProcessingInstructionError("count is not an integer number")
        if cnt<1 or cnt>20:
            raise ProcessingInstructionError("count out of range 1-20")
            
    for k1 in range(cnt):    
    
        ready = False
    
        while ready == False:
            msg = "Enter indication of DUT"
            if cnt>1:
                msg += " " + str(k1+1) + ". reading."
            if "unit" in processing_instructions:
                msg += " in "
                if "indication_prefix" in processing_instructions:
                    msg+= processing_instructions["indication_prefix"]
                msg += processing_instructions["unit"]
            else:
                msg +="."

            if "function" in test_point_data:
                msg += "\n\nFunction under test is: " + test_point_data["function"]

            msg += "\n\nTesting: " + test_point_data.__str__() 
            entertxt = eg.enterbox(msg,"Calibration")
            try: 
                indications.append(float(entertxt)*indication_prefix)
                ready = True
            except:
                eg.msgbox("Please enter a float variable")
        
    return indications




if __name__ == '__main__':
    print(manual_entry(dict(voltage=100),dict(number_of_indications=4,unit="V",indication_prefix="u")))
