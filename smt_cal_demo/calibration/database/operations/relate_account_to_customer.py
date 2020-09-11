# -*- coding: utf-8 -*-
"""
Created on Sun Mar 17 14:10:58 2013

@author: Scheidt
"""


import datetime as dt
import smt_cal_demo.utilities.easygui as eg
from smt_cal_demo.calibration.database.objects import Instrument, Customer, Account
from smt_cal_demo.calibration.database.support import session 

c_ui_title = "Calibration database"

t1 = dt.datetime.now()
t1_s = t1.strftime("%d.%m.%y")


accounts = session.query(Account).all()

msg = "Select account you will assign a customer"
choices = list()
for item in accounts:
    choices.append(item.select_string())

choice=eg.choicebox(msg, c_ui_title, choices)
    
for item in accounts:
    if item.select_string()==choice:
        account = item

customers = session.query(Customer).all()

msg = "Select customer you will assign this account to"
choices = list()
for item in customers:
    choices.append(item.select_string())

choice=eg.choicebox(msg, c_ui_title, choices)
    
for item in customers:
    if item.select_string()==choice:
        customer = item

account.customers.append(customer)


session.add(account)
session.commit()
                    
