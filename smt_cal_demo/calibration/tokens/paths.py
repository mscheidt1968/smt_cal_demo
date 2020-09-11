# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 15:54:47 2015

@author: Scheidt
"""
import os
import socket
from pathlib import Path

hostname = socket.gethostname()

smt_cal_demo_path = Path(__file__).parent.parent

local_firma_path = smt_cal_demo_path.as_posix()

central_calibration_database_2015 = "Path to centralized database"
    
local_calibration_database_2015 = os.path.join(
    local_firma_path,
    "database", 
    "calibration_data_2015.sqlite")

central__measurement_data_store = "path to centralized data store"

local_measurement_data_store = os.path.join(
    local_firma_path,
    "measurement_data")

    
# if there is a need to modify this path on an individual computer
# do it as follows
if hostname == "???":
    #modifications for this computer
    pass


if __name__=="__main__":
    print(("calibration_database2015", local_calibration_database_2015))
    print(("local_measurement_data_store", local_measurement_data_store))
