# -*- coding: utf-8 -*-
"""
Created on Sat Dec 19 13:27:05 2015

@author: Scheidt
"""

import pickle
import io
from numpy.core.multiarray import scalar
from numpy import dtype



class Dummy(object):

    pass

class DateTimeDummy(object):
    
    def __init__(self,arg):
        self.arg = arg

#class Procedure(object):
#
##    def __init__(self):
##        # the following variables will contain maintained for serialization  
##        self.testpoint = dict()
##        self.processing_instructions = dict()
##        self.indications = list()  #list of recorded indications of DUT
#    pass
#
#class Var(object):
#    """ Describes an input variable of a model 
#    
#    value: value of the quantity
#    unit: physical unit
#    description: english description of the input variable """    
#
#    
#    def __init__(self, value, uncertainty, unit, description=""):
#        self.v = value
#        self.u = uncertainty
#        self.unit = unit
#        self.description = description
#        self.offset = None
#
#        
        
#class Model(object):
#    
#    pass

class Py2Unpickler(pickle.Unpickler):
    
    def find_class(self, module, name):
        if name == "Procedure":
            return super(Py2Unpickler, self).find_class("smt_cal_demo.calibration." + module, name)
        elif name == "Var":
            return super(Py2Unpickler, self).find_class("smt_cal_demo.calibration." + module, name)
        elif name == "scalar":
            return scalar
        elif name == "dtype":
            return dtype
        elif name == "Model":
            return super(Py2Unpickler, self).find_class("smt_cal_demo.calibration." + module, name)
        elif name == "Environment":
            return Dummy
        elif name == "device":
            return Dummy
        elif name == "Volt_AC":
            return Dummy
        elif name == "Volt_DC":
            return Dummy
        elif name == "Cur_AC":
            return Dummy
        elif name == "Cur_DC":
            return Dummy
        elif name == "Res":
            return Dummy
        elif name == "Res_2w":
            return Dummy
        elif name == "Res_4w":
            return Dummy
        elif name == "Cap":
            return Dummy
        elif name == "SerialPortConnection":
            return Dummy
        elif name == "StimulationDesc":
            return Dummy
        elif name == "MeasurementDesc":
            return Dummy
        elif name == "VarList":
            return super(Py2Unpickler, self).find_class("smt_cal_demo.calibration." + module, name)
        elif name == "A":
            return Dummy
        elif name == "Device":
            return Dummy
        elif name == "datetime":
            return DateTimeDummy
        else:
            return super(Py2Unpickler, self).find_class(module, name)

        
if __name__== '__main__':    
    counter = 0
    err_counter = 0
    empty_counter = 0
    for m in measurements:
        p1 = m.procedure
        if p1 == None:
            empty_counter += 1
        else:
            counter += 1
            try:
                obj = Py2Unpickler(io.BytesIO(p1),fix_imports=True, encoding="latin1", errors="strict").load()
            except Exception as exc:
                err_counter += 1
                print((counter,exc))
                if err_counter>1:
                    break
    
    print(("Empty:", empty_counter))        
    print(("Total:",counter))
    print(("Errors:",err_counter))