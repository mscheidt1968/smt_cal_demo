# -*- coding: utf-8 -*-
"""
Created on Wed Jan 09 15:24:21 2013

@author: Scheidt
"""


import datetime as dt
from dateutil.relativedelta import relativedelta
import smt_cal_demo.utilities.easygui as eg
from smt_cal_demo.calibration.database.objects import Instrument,Customer
from smt_cal_demo.calibration.database.support import session 

c_ui_title = "Database"
t1 = dt.datetime.now()
t1_s = t1.strftime("%d.%m.%y")
t2 = t1 + relativedelta(years = 1)
t2_s = t1.strftime("%d.%m.%y")

fields=["Manufacturer","Model","SN","Marked ID","Object description","Last calibration","Next calibration","Traceable","Cal_expiration_d","in_use"]
field_values = ["","","","","",t1_s,t2_s,"","",""]
values=eg.multenterbox("Enter data to initialize an instrument dataset.","Calibration Database",fields,field_values )

instrument=Instrument()
instrument.manufacturer=values[0]
instrument.model=values[1]
instrument.serial_number=values[2]
instrument.marked_id=values[3]
instrument.object_description=values[4]
instrument.last_calibration = dt.datetime.strptime(values[5],"%d.%m.%y")
instrument.next_calibration = dt.datetime.strptime(values[6],"%d.%m.%y")
instrument.traceable = None if values[7]=="" else int(values[7])
instrument.cal_expiration_d = None if values[8]=="" else int(values[8])
instrument.in_use = None if values[9]=="" else int(values[9])


customers = session.query(Customer).all()

msg = "Select ownwer of the instrument from list:"
choices = list()
for item in customers:
    choices.append(item.select_string())

choice=eg.choicebox(msg, c_ui_title, choices)

customer = None    
for item in customers:
    if item.select_string()==choice:
        customer = item

instrument.customer = customer
instrument.modified = dt.datetime.now()

session.add(instrument)
session.commit()
