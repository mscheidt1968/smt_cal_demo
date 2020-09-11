# -*- coding: utf-8 -*-
"""
Created on Sat Dec 19 13:27:05 2015

@author: Scheidt
"""

import pickle
import io


class Dummy(object):

    pass


class Py3Unpickler(pickle.Unpickler):
    """ Renames modules to accomodate package name changes from py3. to smt_cal_demo
    """
    def find_class(self, module, name):
        if module.find("py3.") >= 0:
            return super(Py3Unpickler, self).find_class(module.replace("py3.", "smt_cal_demo."), name)
        else:
            return super(Py3Unpickler, self).find_class(module, name)

        
if __name__== '__main__':    
    pass
