# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 11:16:03 2013

@author: Scheidt
"""

import datetime
import smt_cal_demo.utilities.easygui as eg
from smt_cal_demo.calibration.database.support import session,Calibration,Instrument,Measurement


c_title = "Database operation"
calibration = None
#calibration = session.query(Calibration).filter(Calibration.id == 4294996385L ).one()
calibration_selected = False
values = None
while calibration_selected == False:
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
                choice = eg.choicebox(msg, c_title, choices)
            
                for item in calibrations:
                    if item.select_string()==choice:
                        calibration = item
        else:
            calibration=calibrations[0]
            
        print(calibration)   
    else:
        calibration_selected = True

if calibration.end_date is None:
    # Calibration must be closed now
    print("Closing calibration")
    calibration.modified = datetime.datetime.now()
    calibration.end_date = datetime.datetime.now()   
    
    answer = eg.ynbox("Calibration is closed. Should changes be saved to database?",c_title)
    if answer == 0:
        pass    
    else:
        session.add(calibration)
        session.commit()
    
else:
    # Calibration must be closed now
    print("Calibration will be reopend")
    calibration.modified = datetime.datetime.now()
    calibration.end_date = None
    
    answer = eg.ynbox("Calibration is opened again. Should changes be saved to database?",c_title)
    if answer == 0:
        pass    
    else:
        session.add(calibration)
        session.commit()
    


