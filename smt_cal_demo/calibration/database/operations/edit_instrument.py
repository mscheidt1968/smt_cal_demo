# -*- coding: utf-8 -*-
"""
Created on Sat Feb 16 19:49:34 2013

@author: Scheidt
"""


import datetime as dt
import smt_cal_demo.utilities.easygui as eg
from smt_cal_demo.calibration.database.objects import Instrument, Customer
from smt_cal_demo.calibration.database.support import session 

c_ui_title = "Database"

loop=True
while loop == True:
    fields=["Manufacturer","Model","SN"]
    values=eg.multenterbox("Enter data to search instrument.",
                                "Calibration Database",
                                fields=fields,values=["Sch%","%","%"])
    
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
    choice=eg.choicebox(msg, c_ui_title, choices)

    for item in instruments:
        if item.__repr__()==choice:
            instrument = item
else:
    instrument=instruments[0]
    

fields=["Manufacturer","Model","SN","Marked ID","Object description","Last calibration","Next calibration"]
field_values = [instrument.manufacturer,
                instrument.model,
                instrument.serial_number,
                instrument.marked_id,
                instrument.object_description,
                instrument.last_calibration.strftime("%d.%m.%y") if not instrument.last_calibration is None else "01.01.01",
                instrument.next_calibration.strftime("%d.%m.%y") if not instrument.last_calibration is None else "01.01.01"
                ]

values=eg.multenterbox("Enter data to initialize an instrument dataset.","Calibration Database",fields,field_values )

instrument.manufacturer=values[0]
instrument.model=values[1]
instrument.serial_number=values[2]
instrument.marked_id=values[3]
instrument.object_description=values[4]
instrument.last_calibration = dt.datetime.strptime(values[5],"%d.%m.%y")
instrument.next_calibration = dt.datetime.strptime(values[6],"%d.%m.%y")

instrument.modified = dt.datetime.now()
4296234242

if eg.ynbox("Will modify customer field", c_ui_title)==1:
    customers = session.query(Customer).all()
    
    msg = "Select ownwer of the instrument from list:"
    choices = list()
    for item in customers:
        choices.append(item.select_string())
    
    choice=eg.choicebox(msg, c_ui_title, choices)
        
    for item in customers:
        if item.select_string()==choice:
            customer = item
    
    instrument.customer = customer

instrument.modified = dt.datetime.now()
session.add(instrument)
session.commit()