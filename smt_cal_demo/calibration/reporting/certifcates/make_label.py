# -*- coding: utf-8 -*-
"""
Created on Sun Apr 07 11:10:36 2013

@author: Scheidt
"""
def make_label(id_obj, instrument_sn, certificate_id, cal_date, acc_logo=True, safety=False):    
    pass    
    
if __name__== "__main__":  
    instrument_id = 4296148705
    cal_date = dt.datetime(2020,7,7)
    certifcate_id = "200707_C01_000"
    instrument_sn = "191022202"
    make_label(instrument_id, instrument_sn, certifcate_id, cal_date, acc_logo=False, safety=True)