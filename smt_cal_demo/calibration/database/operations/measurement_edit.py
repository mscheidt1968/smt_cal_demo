# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 18:56:19 2013

@author: Scheidt
"""


import os
import time
import datetime
import pickle
import sqlite3 as n_sql
import datetime as n_dat
import io

import smt_cal_demo.utilities.easygui as eg
from smt_cal_demo.calibration.database.support import session,Calibration,Instrument,Measurement
import smt_cal_demo.calibration.tokens.paths as c_paths
import smt_cal_demo.calibration.database.py2unpickle as n_py2unpickle


def get_procedure_object(measurement):
    sql_file_name = os.path.join(
        c_paths.local_measurement_data_store,
        "y{:04d}m{:02d}".format(
            measurement.start_date.year,
            measurement.start_date.month),
        "d{:02d}.sqlite".format(measurement.start_date.day))
    
    obj = None
    if os.path.isfile(sql_file_name):
        conn = n_sql.connect(sql_file_name)
        data = conn.execute(
            "Select * FROM data WHERE id = ?",
            (measurement.id,)).fetchone()
        
        if data is not None:
            if measurement.procedure_data_type == 1:
                if data[2] is not None:
                    zw_obj = data[2]
                    obj = n_py2unpickle.Py2Unpickler(
                        io.BytesIO(zw_obj), 
                        fix_imports=True,
                        encoding="latin_1",
                        errors="strict").load()
            elif data[3] is not None:
                zw_obj = data[3]
                obj = pickle.loads(zw_obj)
                
        conn.close()
        
    return obj


def store_procedure_object(measurement, value):
    measurement.procedure_data_type = 2
    sql_file_name_level0 = os.path.join(
            c_paths.local_measurement_data_store,
            "y{:04d}m{:02d}".format(
                measurement.start_date.year,
                measurement.start_date.month),
        )   
    if not os.path.isdir(sql_file_name_level0):
        raise Exception("Directory must exist, if already done meausrement is modified")
        
    sql_file_name_level1 = os.path.join(
            sql_file_name_level0,
            "d{:02d}.sqlite".format(measurement.start_date.day)
        )   

    if os.path.isfile(sql_file_name_level1):
        conn = n_sql.connect(sql_file_name_level1)
    else:
        raise Exception("Sqlite DB must exist, if already done meausrement is modified")

    try:
        with conn:
            conn.execute('''
                UPDATE data 
                SET modified_date=?,data3=? 
                WHERE id=?
            ''',
            (n_dat.datetime.now(),
             pickle.dumps(value),
                measurement.id,)
            )

    except:
        raise Exception("Couldn't write data")

    try:
        conn.commit()
        conn.close()
    except Exception as exc:
        raise Exception("Problem during data storage in sql db {:s}. Err:{:s}".
            format(sql_file_name_level1, exc.args[0]))
        
    return

c_title = "Reporting"
calibration = None
#calibration = session.query(Calibration).filter(Calibration.id == 4294996385L ).one()
measurement_selected = False
values = None
while measurement_selected == False:
    if calibration is None:
        loop=True
        while loop == True:
            fields=["Manufacturer","Model","SN"]
            values=eg.multenterbox("Enter data to initialize an instrument dataset.",
                                        "Calibration Database",
                                        fields=fields,values=["%","%","%"] if values is None else values)
            
            instruments=session.query(Instrument).filter(Instrument.manufacturer.like(values[0]),
                                                        Instrument.model.like(values[1]),
                                                        Instrument.serial_number.like(values[2])).all()
                                                        
            if instruments.__len__()==0:
                eg.msgbox("Change your data. No instrument found.")
            else:
                loop = False
        
        if instruments.__len__()>1:
            msg = "Multiple instruments found, please select the intended from the list:"
            choices = list()
            for item in instruments:
                choices.append(item)
            choice=eg.choicebox(msg, "Certifcate Creation", choices)
        
            for item in instruments:
                if item.__repr__()==choice:
                    instrument = item
        else:
            instrument=instruments[0]
            
        print(instrument)           
        
        
        calibrations = instrument.calibration
    
        if calibrations.__len__()>1:
            date_of_latest = None
            latest_cal = None        
            for item in calibrations:
                if date_of_latest is None:
                    date_of_latest = item.start_date
                    latest_cal = item
                if item.start_date >= date_of_latest:
                    date_of_latest = item.start_date
                    latest_cal = item
    
            msg = "Should latest calibration from {0:s} be used?".format(latest_cal.start_date.strftime("%d %B %Y at %X"))
            if eg.ynbox(msg,"Create certificate")==1:
                calibration =latest_cal
            else:                
                msg = "Multiple calibrations found, please select the intended from the list:"
                choices = list()
                for item in calibrations:
                    choices.append(item.select_string())
                choice=eg.choicebox(msg, c_title, choices)
            
                for item in calibrations:
                    if item.select_string()==choice:
                        calibration = item
        else:
            calibration=calibrations[0]
            
        print(calibration)           
    
    
    choices = list()
    for item in calibration.measurements:
        choices.append(item.select_string())

    if len(choices) == 0:
        eg.msgbox("No measurement available")
        calibration = None
    else:
        msg = "Select measurement"
        choice=eg.choicebox(msg, c_title, choices)
        if choice is None:
            calibration = None
        else:            
            for item in calibration.measurements:
                if item.select_string()==choice:
                    measurement = item
        
            measurement_selected = True
        
answer = eg.ynbox("Should measurement be marked as invalid?",c_title)
if answer == 0:
    measurement.validity = True
else:
    measurement.validity = False
 
answer = eg.ynbox("Should changes be saved to database?",c_title)
if answer == 0:
    pass    
else:
    answer = eg.enterbox("Please enter text for unvalidity comment",
                     c_title,default=measurement.unvalidity_comment)   
    measurement.unvalidity_comment = answer
    measurement.modified = datetime.datetime.now()
    session.add(measurement)
    session.commit()

print("Measurement dataset is now available as var measurement")
print("To get procedure data for modifications, call get_procedure_object(measurement).")
print("To store modified data, call store_procedure_object(measurement).")

    