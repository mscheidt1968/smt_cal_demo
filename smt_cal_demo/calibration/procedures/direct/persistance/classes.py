# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 10:34:32 2015

@author: scheidt
"""

class PreMeasuredValue(object):

    def __init__(self):
        self.value = None
        self.unc_of_value = None
        self.correction = 0
        self.unc_of_correction= 0
        self.dispcorr = 0
        self.unc_of_dispcorr = 0
        self.drift = 0
        self.unc_of_drift = 0

if __name__=="__main__":
    pass
