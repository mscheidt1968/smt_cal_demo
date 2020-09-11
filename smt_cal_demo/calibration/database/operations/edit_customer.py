# -*- coding: utf-8 -*-
"""
Created on Sun Apr 07 09:24:34 2013

@author: Scheidt
"""


import datetime as dt
import smt_cal_demo.utilities.easygui as eg
from smt_cal_demo.calibration.database.objects import Instrument, Customer
from smt_cal_demo.calibration.database.support import session 

c_ui_title = "Database"

loop=True
while loop == True:
    fields=["Name","Contacts","Adresses"]
    values=eg.multenterbox("Enter data to search customer.",
                                "Calibration Database",
                                fields=fields,values=["%","%","%"])
    
    customers=session.query(Customer).filter(Customer.name.like(values[0]),
                                                Customer.contacts.like(values[1]),
                                                Customer.addresses.like(values[2])).all()
                                                
    if customers.__len__()==0:
        eg.msgbox("Change your data. No customer found.")
    else:
        loop = False

if customers.__len__()>1:
    msg = "Multiple customers found, please select the intended from the list:"
    choices = list()
    for item in customers:
        choices.append(item)
    choice=eg.choicebox(msg, c_ui_title, choices)

    for item in customers:
        if item.__repr__()==choice:
            customer = item
else:
    customer=customers[0]
    

fields=["Name","Contacts","Addresses"]
field_values = [customer.name,
                customer.contacts,
                customer.addresses,
                ]

values=eg.multenterbox("Enter new data.","Calibration Database",fields,values=field_values )

customer.name=values[0]
customer.contacts=values[1]
customer.addresses=values[2]

customer.modified = dt.datetime.now()

session.add(customer)
session.commit()