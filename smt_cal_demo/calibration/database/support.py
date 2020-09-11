# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 16:30:37 2015

@author: Scheidt
"""

import datetime
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from smt_cal_demo.calibration.database.objects import Option, Calibration, Instrument, Measurement, TestGroup, Certificate, Customer
from sqlalchemy import event
import smt_cal_demo.utilities.easygui as eg
import smt_cal_demo.calibration.tokens.paths as c_paths

# old sqlite database
# engine = create_engine('sqlite:///C:\\Users\\Scheidt\\Documents\\Firma\\Datenbanken\\calibration_data.sqlite', echo=False)
# new local mysql database
engine = create_engine(
    "sqlite:///" + c_paths.local_calibration_database_2015,
    echo=False,
    connect_args={'check_same_thread':False},
    poolclass=StaticPool,
    )

Session = sessionmaker(bind = engine)
session = Session()
Session_keys = sessionmaker(bind = engine)
session_keys=Session_keys()

try:
    db_id_offset = session_keys.query(Option).filter(Option.name == "db_id_offset").one()
except:
    db_id_offset = Option("db_id_offset", str(eg.integerbox("Enter the base number of the database",lowerbound = 0, upperbound = 31)))
    session_keys.add(db_id_offset)
    session_keys.flush()

    
try:
    id_step = session_keys.query(Option).filter(Option.name == "id_step").one()
except:
    id_step = Option("id_step","32")
    session_keys.add(id_step)
    session_keys.flush()

try:
    next_id = session_keys.query(Option).filter(Option.name == "next_id").one()
except:
    next_id = Option("next_id",str(2**32+int(id_step.value)+int(db_id_offset.value)))
    session_keys.add(next_id)
    session_keys.flush()
    


def get_id():
    new_id = int(next_id.value)
    next_id.value = str( new_id+int(id_step.value))    
    session_keys.commit()
    return new_id


def my_after_attach(session,instance):
    if instance.id is None:
        instance.id = get_id()

event.listen(Session, "after_attach", my_after_attach)

if __name__=="__main__":
    
    #print get_id()
    #
    print(get_id())
    pass

