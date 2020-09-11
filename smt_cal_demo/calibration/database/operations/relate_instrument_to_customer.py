# -*- coding: utf-8 -*-
"""
Created on Sat Feb 16 19:18:04 2013

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
    choice=eg.choicebox(msg, c_ui_title, choices)

    for item in instruments:
        if item.__repr__()==choice:
            instrument = item
else:
    instrument=instruments[0]
    

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