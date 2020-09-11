# -*- coding: utf-8 -*-
"""
Created on Sat Feb 16 19:01:19 2013

@author: Scheidt
"""


import datetime as dt
from dateutil.relativedelta import relativedelta
import smt_cal_demo.utilities.easygui as eg
from smt_cal_demo.calibration.database.objects import Instrument, Customer
from smt_cal_demo.calibration.database.support import session 

c_ui_title = "Calibration database"

t1 = dt.datetime.now()
t1_s = t1.strftime("%d.%m.%y")
t2 = t1 + relativedelta(years = 1)
t2_s = t1.strftime("%d.%m.%y")

fields=["Name","Contacts","Adresses"]
field_values = ["","",""]
values=eg.multenterbox("Enter data to initialize a customer dataset.",c_ui_title,fields,field_values )

customer=Customer()
customer.name=values[0]
customer.contacts=values[1]
customer.addresses=values[2]

customer.modified = dt.datetime.now()

session.add(customer)
session.commit()
                    
