# -*- coding: utf-8 -*-
"""
Created on Mon May 12 19:30:33 2014

@author: Scheidt
"""
import math

def format_number_unc(x, ux, size=14, no_prefix=False):
    """ format a number x with uncertainty according to GUM regulations
    """
    prefixes={-1:(1e-3,"m"),
            -2:(1e-6,"u"),
            -3:(1e-9,"n"),
            -4:(1e-12,"p"),
            -5:(1e-15,"f"),
            0:(1,""),
            1:(1e3,"k"),
            2:(1e6,"M"),
            3:(1e9,"G"),
            4:(1e12,"T")}

    # determine positions n_ auf decimal point
    if x == 0:
        n_x = 0
    else:
        n_x = math.floor(math.log10(abs(x)))

    if ux == 0:
        n_ux = n_x-8
    else:
        n_ux = math.floor(math.log10(ux))

    # round numbers. 
    potenz = 10**(n_ux-1)
    # speciality if first significant digit of uncertainty is larger than 5
    # than only one significant number will be uses according to METAS
    # Mr. Mortara Email 12.5.2014
    unc_over_5 = False
    if round(ux/potenz) >= 50:
        potenz = potenz / 10.
        unc_over_5 = True
    #regular round of x
    f_x = potenz*round(x/potenz)
    # rounding upwards uncertainty
    f_ux = potenz*math.ceil(ux/potenz)


    # select prefix if enabled        
    if no_prefix:
        pref_index = 0
    else:
        if abs(f_x)>abs(f_ux):
            pref_index = math.floor(n_x/3.0)
            if pref_index <-5 or pref_index>4:
                pref_index = 0
        else:
            pref_index = math.floor(n_ux/3.0)
            if pref_index <-5 or pref_index>4:
                pref_index = 0

    if abs(x) > 1e20:
        pref_index = 0
    
    pref_mul =  1/prefixes[pref_index][0]    
    pref_unit =  prefixes[pref_index][1]    
    
    # determine number of decimals to display
    kommastellen = 1- n_ux + pref_index * 3
    if unc_over_5:
        kommastellen -= 1
    if kommastellen<0:
        kommastellen = 0
    format_str = "{" + ":.{:.0f}".format(kommastellen) + "f}"

    
    
    f2_x = format_str.format(f_x * pref_mul)
    if ux == 0:
        if f2_x.find(".")>=0:
            while f2_x[-1]=="0":
                f2_x = f2_x[0:-1]
            if f2_x[-1]==".":
                f2_x = f2_x[0:-1]

    if f2_x == "0":
        pass
    elif f2_x == "-0":
        f2_x = "0"
    else:    
        f2_x += pref_unit
    
    f2_ux = format_str.format(f_ux * pref_mul)
    if ux == 0:
        if f2_ux.find(".")>=0:
            while f2_ux[-1]=="0":
                f2_ux = f2_ux[0:-1]
            if f2_x[-1]==".":
                f2_ux = f2_ux[0:-1]

    if f2_ux == "0":
        pass
    elif f2_ux == "-0":
        f2_ux = "0"
    else:    
        f2_ux += pref_unit


    
    #return (f_x*pref_mul,f_ux*pref_mul,pref_unit,n_ux,1-n_ux+pref_index*3)
    return ( f2_x.lstrip(), f2_ux.lstrip())



def format_number(number, digits=6, no_prefix=False):
    f = float(number)
    if f==0:
        index = 0
    else:
        index = math.floor(math.log10(abs(f))//3)
    prefixes={-1:(1e-3,"m"),
            -2:(1e-6,"u"),
            -3:(1e-9,"n"),
            -4:(1e-12,"p"),
            -5:(1e-15,"f"),
            0:(1,""),
            1:(1e3,"k"),
            2:(1e6,"M"),
            3:(1e9,"G"),
            4:(1e12,"T")
    }
    if no_prefix:
        index = 0
        
    if index<-5:
        f = 0
        prefix = 0
        f1 = 0
        suffix = " "
    else:
        f1 = f/prefixes[index][0]
        suffix = prefixes[index][1]

    if f1==0:
        sf2 = "0"
    else:
        sf2="{:f}".format(f1)
        if sf2.find(".")>=0:
            while sf2[-1]=="0":
                sf2 = sf2[0:-1]
            if sf2[-1]==".":
                sf2 = sf2[0:-1]
    
    if sf2 == "0":
        pass
    elif sf2 == "-0":
        sf2 = "0"
    else:
        sf2 += suffix       
        
    return sf2


if __name__=="__main__":
    print((format_number_unc(1.234567,0.02436)))
    print((format_number_unc(1.234499,0.02436)))
    print((format_number_unc(1.234499,0.05136)))
    print((format_number_unc(1.234499e2,0.02436e2)))
    print((format_number_unc(1.234499e3,0.02436e3)))
    print((format_number_unc(0,0.02436e3)))
    print((format_number_unc(-1.234499e3,0.02436e3)))
    pass
