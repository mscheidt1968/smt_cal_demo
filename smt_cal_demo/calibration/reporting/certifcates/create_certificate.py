# -*- coding: utf-8 -*-
"""
Created on Wed Nov 07 18:37:02 2012

@author: Scheidt
"""

import smt_cal_demo.utilities.easygui as eg
import smt_cal_demo.calibration.calibration_data.cal_spec_reader_v2 as csr
from smt_cal_demo.calibration.database.support import session,Calibration,Instrument,Measurement
from smt_cal_demo.calibration.reporting.certifcates.acc_pdf import create_certificate

c_title = "Reporting"
calibration = None
#calibration = session.query(Calibration).filter(Calibration.id == 4295306530L ).one()

if calibration is None:
    loop=True
    while loop == True:
        fields=["Manufacturer","Model","SN"]
        values=eg.multenterbox("Enter data to initialize an instrument dataset.",
                                    "Calibration Database",
                                    fields=fields,values=["%","%","%"])
        
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
            choice=eg.choicebox(msg, "Certificate Creation", choices)
        
            for item in calibrations:
                if item.select_string()==choice:
                    calibration = item
    else:
        calibration=calibrations[0]
        
    print(calibration)



fn = None
#fn = u'C:\\Users\\Scheidt\\Documents\\Firma\\SW\\entwicklung\\kalibrieren\\calibration_data\\fluke\\fluke8846a_performance.py'

if fn is None:
    try:
        fn = eg.fileopenbox(msg = "Select specification",
                                 title = "Calibration", 
                                 default = "../../calibration_data/"+
                                 calibration.instrument.manufacturer.lower() + "/*.py")
    except:
        pass

if fn is None:
    fn = eg.fileopenbox(msg = "Select specification",
                             title = "Calibration", 
                             default = "../../calibration_data/*.py")
    
if fn is None:
    calData = ""
elif fn == ".":
    calData = ""
else:
    spec_file = open(fn,"r")
    data = spec_file.read()
    spec_file.close()
    exec(data)


[test_ids,tespoints,cur_proc_instrs,specs] = csr.process_cal_spec(calData)
 
option = dict()
option["acc"]=False
option["database"]=False
option["safety"]=False

option["acc_spec"] = False

create_certificate(calibration,test_ids,cur_proc_instrs,specs,options=option)