# -*- coding: utf-8 -*-
"""
Created on Sun Mar 17 14:00:59 2013

@author: Scheidt
"""

import numpy as np
import random

import datetime as dt
from dateutil.relativedelta import relativedelta
import smt_cal_demo.utilities.easygui as eg
from smt_cal_demo.calibration.database.objects import Instrument, Customer, Account
from smt_cal_demo.calibration.database.support import session 
import math 

c_password_chars = "234679ACDEFGHJKLMNPRTUWXYZ"

def create_password(n=8):
    password = ""
    for k1 in range(n):
        password += c_password_chars[random.randrange(0,len(c_password_chars)-1)]
    
    return password
        
    
    
c_ui_title = "Calibration database"

t1 = dt.datetime.now()
t1_s = t1.strftime("%d.%m.%y")
t2 = t1 + relativedelta(years = 1)
t2_s = t1.strftime("%d.%m.%y")

Account.customers
Account.group
Account.last_login_date
Account.login_name
Account.nice_name
Account.modified
Account.password
Account.validation_date
new_password = create_password(8)
fields=["Login name","Nice name","Group"]
field_values = ["","","normal"]
values=eg.multenterbox("Enter data to initialize an account with password:" + new_password,c_ui_title,fields,field_values )


account = Account()

account.group = values[2]
account.last_login_date = t1
account.login_name = values[0]
account.nice_name = values[1]
account.modified = t1
account.password = new_password
account.validation_date = t1

if eg.ynbox("Will you add a customer", c_ui_title)==1:
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

print("Passwort für den Account: \n" + account.login_name)
print(new_password)
