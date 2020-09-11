# -*- coding: utf-8 -*-
"""
Created on Sun Aug 09 12:03:40 2015

@author: scheidt
"""

from __future__ import division
import socket
import os
import ctypes.wintypes
import datetime
from pathlib import Path

host_name = socket.gethostname()

if "__file__" in locals():
    _script_path = os.path.split(__file__)[0]
else:
    _script_path = os.getcwd()

# use host name to model device specific settings
firma_path = Path(__file__).parent.parent.as_posix()
computer_number = 0


def time_stamp_file_name_prefix(time_stamp = None):
    if time_stamp is None:
        time_now = datetime.datetime.now()
    else:
        time_now = time_stamp
        
    prefix = time_now.strftime("%y%m%d%S%f") + "_C{:02d}".format(computer_number)
    return prefix

def get_messgeraete_data_path(device_id):
    device_data_path = None
    for path in os.listdir(messgeraete_path):
        if os.path.split(path)[1].find(device_id)==0:
            device_data_path = os.path.join(messgeraete_path,path,"data")
            break
    
    if device_data_path is None:
        raise Exception("No data path for device_id",device_id,"found")
    
    if not os.path.exists(device_data_path):
        os.mkdir(device_data_path)
    
    return device_data_path
 
if __name__=="__main__":
    print("Time stamp prefix:", time_stamp_file_name_prefix())
    print(get_messgeraete_data_path("171115_MSC_10"))
    pass
