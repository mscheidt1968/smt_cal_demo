# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 09:04:00 2012

@author: Scheidt
"""

import math
import numpy as np

class Var(object):
    """ Describes an input variable of a model 
    
    value: value of the quantity
    unit: physical unit
    description: english description of the input variable """    

    
    def __init__(self, value, uncertainty, unit, description=""):
        self.v = value
        self.u = uncertainty
        self.unit = unit
        self.description = description
        self.offset = None
        pass

    def data2dict(self, add_description = False):
        zw = dict()
        zw["v"] = self.v
        zw["u"] = self.u
        zw["unit"] = self.unit
        if add_description:        
            zw["description"] = self.description
        return zw

    def dict2data(self, data):
        self._v = data["v"]       
        self.u = data["u"]       
        self.unit = data["unit"]  
        if data.haskey("description"):
            self.description = data["description"]  
            
    def sim_mode(self,offset):
        self.offset = offset
            
    def expected_mode(self):
        self.offset = None


class VarList(object):
    """ Describes an input variable of a model 
    
    value: list of values of the quantity
    unit: physical unit
    description: english description of the input variable """    

    @property
    def v(self):
        """Current simulation value list"""
        if self.offset is None:
            return self._v
        else:
            return list(np.array(self._v) + np.array(self.offset))
    
    @v.setter
    def v(self, value):
        self._v = value

    
    def __init__(self, value, uncertainty, unit, description=""):
        self._v = value
        self.u = uncertainty
        self.unit = unit
        self.description = description
        self.offset = None
        pass

    def data2dict(self, add_description = False):
        zw = dict()
        zw["v"] = self.v
        zw["u"] = self.u
        zw["unit"] = self.unit
        if add_description:        
            zw["description"] = self.description
        return zw

    def dict2data(self, data):
        self._v = data["v"]       
        self.u = data["u"]       
        self.unit = data["unit"]  
        if data.haskey("description"):
            self.description = data["description"]  
            
    def sim_mode(self,offset):
        self.offset = offset
            
    def expected_mode(self):
        self.offset = None
    

class VarComplexUnknownPhase(object):
    """ Describes a complex input variable of a model with unknown phase 
    
    value: value of the quantity
    unit: physical unit
    description: english description of the input variable """    

    @property
    def v(self):
        """current simulation value"""
        if self.phi is None:
            return np.complex(0,0)
        else:
            zw = self.mod * np.exp(np.complex(0,1)* self.phi)
            return zw
    
    def __init__(self, modulus, uncertainty_modulus, unit, description=""):
        self._v = np.complex(0,0)
        self.phi = None
        self.mod = modulus
        self.u_m = uncertainty_modulus
        self.unit = unit
        self.description = description
        pass

    def data2dict(self, add_description = False):
        zw = dict()
        zw["mod"] = self.modulus
        zw["u_mod"] = self.u_m
        zw["unit"] = self.unit
        if add_description:        
            zw["description"] = self.description
        return zw

    def dict2data(self, data):
        self.mod = data["mod"]       
        self.u_m = data["u_mod"]       
        self.unit = data["unit"]  
        if data.haskey("description"):
            self.description = data["description"]  

    def sim_mode(self,phi):
        """Set's current value to a complex number of phase phi"""
        self.phi = phi
            
    def expected_mode(self):
        """Set's current value to expected value 0"""
        self.phi = None
            

def model2dict(model):
    res = dict()
    for item in dir(model):
        if type(getattr(model,item)) is Var:
            res[item] = getattr(model,item).data2dict()
    
    return res

def calculate_unc(model, verbose = False, f_options = dict(), output = None):
    # calculates uncertainty of model
    sum_unc_sq = 0
    for item in dir(model):
        if type(getattr(model,item)) is Var:
            f0 = model.f(**f_options)
            org_v = getattr(model,item).v
            
            unc_v = abs(getattr(model,item).u)
            if unc_v is None:
                raise Exception("No uncertainty for item:" + item)
                
            test_v = org_v - unc_v            
            df = 0
            dx = 1
            k_test = 0
            number_of_runs = 0
            # just step number of time to avoid rounding issues for small uncertaintes
            # while test_v < org_v + unc_v:
            while number_of_runs < 21:
                number_of_runs += 1
                getattr(model,item).v = test_v
                f1 = model.f(**f_options)
                df_test = abs(f1 - f0)
                if df_test > df:
                    df = df_test
                    dx = test_v - org_v 

                test_v = test_v + unc_v / 10.0
                k_test += 1
                if k_test > 21:
                    print(("test_v {:f}, unc_v{:f}".format(test_v,unc_v)))
                    
            getattr(model,item).v = org_v
            sum_unc_sq += df**2


            if type(output) is list:
                if getattr(model,item).u == 0:
                    output.append((item,getattr(model,item).description,getattr(model,item).v,getattr(model,item).u,None,None))
                else:
                    output.append((item,getattr(model,item).description,getattr(model,item).v,getattr(model,item).u,(df / dx),df / dx * getattr(model,item).u))
                
            if verbose:                
                if getattr(model,item).u == 0:
                    pass
                    print((item + "\t" +getattr(model,item).description + "\t" +str(getattr(model,item).v)+ "\t" +str(getattr(model,item).u) +"\t n.A. \t n.A."))
                else:
                    print((item + "\t" +getattr(model,item).description + "\t" +str(getattr(model,item).v)+ "\t" +str(getattr(model,item).u) +"\t" + str(df / dx) + "\t" + str(df / dx * getattr(model,item).u)))
            
    return math.sqrt(sum_unc_sq)

#def calculate_unc_deb(model):
#    # calculates uncertainty of model
#    sum_unc_sq = 0
#    for item in dir(model):
#        if type(getattr(model,item)) is Var:
#            print item
#            f0 = model.f()
#            org_v = getattr(model,item).v
#            
#            unc_v = getattr(model,item).u
#            test_v = org_v - unc_v            
#            df = 0
#            dx = 1
#            while test_v < org_v + unc_v:
#                getattr(model,item).v = test_v
#                f1 = model.f()
#                df_test = abs(f1 - f0)
#                if df_test > df:
#                    df = df_test
#                    print df
#                    dx = test_v - org_v 
#
#                test_v = test_v + unc_v / 10.0    
#
#                    
#            getattr(model,item).v = org_v
#            sum_unc_sq += df**2
#            
##            if getattr(model,item).u == 0:
##                print "c " + item + " n.a."
##            else:
##                print "c " + item + ": " + str(df / dx)
#                
#    return math.sqrt(sum_unc_sq)


def calculate_unc_and_print_model(model, verbose = False,  output = None):
    # calculates uncertainty of model
    sum_unc_sq = 0
    for item in dir(model):
        if type(getattr(model,item)) is Var:
            f0 = model.f()
            org_v = getattr(model,item).v
            
            unc_v = abs(getattr(model,item).u)
            test_v = org_v - unc_v            
            df = 0
            dx = 1
            while test_v < org_v + unc_v:
                getattr(model,item).v = test_v
                f1 = model.f()
                df_test = f1 - f0
                if abs(df_test) > abs(df):
                    df = df_test
                    dx = test_v - org_v 

                test_v = test_v + unc_v / 10.0    
                    
            getattr(model,item).v = org_v
            sum_unc_sq += df**2
            
            if type(output) is list:
                if getattr(model,item).u == 0:
                    output.append((item,getattr(model,item).description,getattr(model,item).v,getattr(model,item).u,None,None))
                else:
                    output.append((item,getattr(model,item).description,getattr(model,item).v,getattr(model,item).u,(df / dx),df / dx * getattr(model,item).u))
                
                
            if getattr(model,item).u == 0:
                pass
                print((item + "\t" +getattr(model,item).description + "\t" +str(getattr(model,item).v)+ "\t" +str(getattr(model,item).u) +"\t n.A. \t n.A."))
            else:
                print((item + "\t" +getattr(model,item).description + "\t" +str(getattr(model,item).v)+ "\t" +str(getattr(model,item).u) +"\t" + str(df / dx) + "\t" + str(df / dx * getattr(model,item).u)))
                
    return math.sqrt(sum_unc_sq)


def calculate_unc_mv(model, verbose = False, f_options = dict(), output = None):
    # calculates uncertainty of model
    number_of_outputs = len(model.f(**f_options))
    results = list()
    
    for res_index in range(number_of_outputs):
        if type(output) is list:
            current_output = list()
            output.append(current_output)
        if verbose:
            print(("Index \t {:d}\t f= \t{:9.3g}".format(res_index,model.f(**f_options)[res_index])))
            print()
        sum_unc_sq = 0
        zw_items = dir(model)
        for item in zw_items:
            if type(getattr(model,item)) is Var:
                f0 = model.f(**f_options)[res_index]
                df = 0
                org_v = getattr(model,item).v
                
                unc_v = abs(getattr(model,item).u)
                if unc_v is None:
                    raise Exception("No uncertaity for item:" + item)
                if unc_v > 0:              
                    test_v = org_v - unc_v            
                    df = 0
                    dx = 1
                    number_of_runs = 0
                    # just step number of time to avoid rounding issues for small uncertaintes
                    # while test_v < org_v + unc_v:
                    while number_of_runs < 21:
                        number_of_runs +=1
                        getattr(model,item).v = test_v
                        f1 = model.f(**f_options)[res_index]
                        df_test = f1 - f0
                        if abs(df_test) > abs(df):
                            df = df_test
                            dx = test_v - org_v 
        
                        test_v = test_v + unc_v / 10.0    
                            
                    getattr(model,item).v = org_v
                    sum_unc_sq += df**2
                
                if type(output) is list:
                    if getattr(model,item).u == 0:
                        current_output.append((item,
                            getattr(model,item).description,
                            getattr(model,item).v,
                            getattr(model,item).u,
                            None,
                            None
                            ))
                    else:
                        current_output.append((
                            item,
                            getattr(model,item).description,
                            getattr(model,item).v,
                            getattr(model,item).u,
                            (df / dx),df / dx * getattr(model,item).u
                            ))
    
                if verbose:
                    if getattr(model,item).u == 0:
                        pass
                        print((item + "\t" +getattr(model,item).description + "\t" +str(getattr(model,item).v)+ "\t" +str(getattr(model,item).u) +"\t n.A. \t n.A."))
                    else:
                        print((item + "\t" +getattr(model,item).description + "\t" +str(getattr(model,item).v)+ "\t" +str(getattr(model,item).u) +"\t" + str(df / dx) + "\t" + str(df / dx * getattr(model,item).u)))

        results.append(math.sqrt(sum_unc_sq))
        if verbose:
            print(("f\t target function\t \t{:9.4g} \t{:9.3g}".format(model.f(**f_options)[res_index], results[-1])))
            print()

    return results
