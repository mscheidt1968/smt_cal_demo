# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 09:54:59 2012

@author: Scheidt
"""

import os
import pickle
import zipfile as n_zip
import sqlite3 as n_sql
import io
import time
import datetime as n_dat
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, PickleType, BigInteger, DateTime, Boolean, Text,Table, BLOB, Float
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
import smt_cal_demo.calibration.tokens.paths as c_paths
import smt_cal_demo.calibration.database.py2unpickle as n_py2unpickle
import smt_cal_demo.calibration.database.py3unpickle as n_py3unpickle


Base = declarative_base()
#engine will be created in support.py

account_customer_ass = Table('account_customer_ass', Base.metadata,
    Column('id', BigInteger, primary_key = True),
    Column('account_id', BigInteger, ForeignKey('accounts.id')),
    Column('customer_id', BigInteger, ForeignKey('customers.id')),
    Column('modified',DateTime)
)

class Account(Base):
    __tablename__ = 'accounts'

    id = Column(BigInteger, primary_key = True)
    validation_date = Column(DateTime)
    last_login_date = Column(DateTime)
    login_name = Column(String(80))
    nice_name = Column(String(80))
    password = Column(String(80))
    group = Column(String(80))
    customers = relationship("Customer",
                    secondary=account_customer_ass) 

    modified = Column(DateTime)

    def select_string(self):
        return "{:s} alias {:s} id:{:d})".format(self.login_name,self.nice_name,self.id)


class Option(Base):
    __tablename__ = 'opts'
    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    value = Column(String(80))
    
    def __init__(self, name, value):
        self.name = name
        self.value = value
    
    def __repr__(self):
        return "<Option({:s},{:s})>".format(self.name, self.value)


class Certificate(Base):
    __tablename__ = 'certficates'
    
    id = Column(BigInteger, primary_key = True)
    print_date = Column(DateTime)
    calibration_id = Column(BigInteger, ForeignKey('calibrations.id'))
    id_m = Column(String(80))
    comment = Column(Text)
    validity =Column(Boolean)
    unvalidity_comment = Column(Text)
    
    modified = Column(DateTime)

class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(BigInteger, primary_key = True)
    name = Column(String(80))
    contacts = Column(Text())
    addresses = Column(Text())
    instruments = relationship("Instrument",
                               order_by = "Instrument.id",
                               backref = "customer")
    
    modified = Column(DateTime)
    
    def select_string(self):
        return "{:s} Adress: {:s} id:{:d})".format(self.name,self.addresses,self.id)
    
    
class Instrument(Base):
    __tablename__ = 'instruments'
    
    id = Column(BigInteger, primary_key=True)
    manufacturer = Column(String(80))
    model = Column(String(80))
    customer_id = Column(BigInteger, ForeignKey('customers.id'))
    serial_number = Column(String(80))
    object_description = Column(String(80))
    calibration = relationship("Calibration",
                               order_by = "Calibration.start_date",
                               backref = "instrument")

    modified = Column(DateTime)
    marked_id = Column(String(80))
    last_calibration = Column(DateTime)
    next_calibration = Column(DateTime)
    traceable = Column(Integer)
    cal_expiration_d = Column(Integer)
    in_use = Column(Integer)
    
    def __repr__(self):
        return "<Instrument({:s},{:s},{:s})>".format(self.manufacturer, self.model, self.serial_number)
        
    

class Calibration(Base):
    __tablename__ = 'calibrations'
    __table_args__ = {'mysql_charset': 'utf8', 'mysql_engine': 'InnoDB'}    

    id = Column(BigInteger, primary_key=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    project_id_m = Column(String(80))
    instrument_id = Column(BigInteger, ForeignKey('instruments.id'))
    result = Column(Boolean)
    operator = Column(String(80))
    validity =Column(Boolean)
    unvalidity_comment = Column(Text)
    
    measurements = relationship("Measurement", backref = "calibration")        
    certificates = relationship("Certificate", backref = "calibration")        

    modified = Column(DateTime)

    def __repr__(self):
        return "Calibration from: {0:s} id:{1:d})".format(self.start_date.isoformat(),self.id)

    def select_string(self):
        return "Calibration from: {0:s} with id:{1:d})".format(self.start_date.strftime("%d %B %Y at %X"),self.id)


class TestGroup(Base):
    __tablename__ = 'testgroups'

    id = Column(BigInteger, primary_key=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    description = Column(String(80))

    measurement = relationship("Measurement", backref = "testgroup")        

    modified = Column(DateTime)

    def __repr__(self):
        return "<TestGroup({:d})>".format(self.id)

class Measurement(Base):
    __tablename__ = 'measurements'

    id = Column(BigInteger, primary_key=True)
    
    testgroup_id = Column(BigInteger, ForeignKey('testgroups.id'))
    calibration_id = Column(BigInteger, ForeignKey('calibrations.id'))
    
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    description = Column(String(80))
    validity =Column(Boolean)
    unvalidity_comment = Column(Text)
    
    # a list of dictionaries defining input parameters and 
    # list structe supports grouping and automatic processing
    parameter = Column(String(1024))
    
    # introduced during change from py2 to py3
    # This value is used to trigger different data procedure loading
    # behavior
    # 0: python 2.7 pickled values in procedure.pck2 file
    # 1: python 3.x pickled value in procedure.pck3 file
    procedure_data_type = Column(Integer)

    # the data contains all information produced during measurement as json
    data = Column(Text)

    modified = Column(DateTime)

    # the procedure contains all information produced during measurement
    # and also the final result
    # data is stored in the file system not in the database
    @hybrid_property
    def procedure(self):
        sql_file_name = os.path.join(
            c_paths.local_measurement_data_store,
            "y{:04d}m{:02d}".format(
                self.start_date.year,
                self.start_date.month),
            "d{:02d}.sqlite".format(self.start_date.day))
        
        obj = None
        if os.path.isfile(sql_file_name):
            conn = n_sql.connect(sql_file_name)
            data = conn.execute(
                "Select * FROM data WHERE id = ?",
                (self.id,)).fetchone()
            
            if data is not None:
                if self.procedure_data_type == 1:
                    if data[2] is not None:
                        zw_obj = data[2]
                        obj = n_py2unpickle.Py2Unpickler(
                            io.BytesIO(zw_obj), 
                            fix_imports=True,
                            encoding="latin_1",
                            errors="strict").load()
                elif data[3] is not None:
                    zw_obj = data[3]
                    obj = n_py3unpickle.Py3Unpickler(
                        io.BytesIO(zw_obj), 
                        fix_imports=True,
                        encoding="latin_1",
                        errors="strict").load()
#                    obj = pickle.loads(zw_obj)
                    
            conn.close()
            
        return obj


    @procedure.setter
    def procedure(self, value):
        self.procedure_data_type = 2
        sql_file_name_level0 = os.path.join(
                c_paths.local_measurement_data_store,
                "y{:04d}m{:02d}".format(
                    self.start_date.year,
                    self.start_date.month),
            )   
        if not os.path.isdir(sql_file_name_level0):
            os.mkdir(sql_file_name_level0)
        sql_file_name_level1 = os.path.join(
                sql_file_name_level0,
                "d{:02d}.sqlite".format(self.start_date.day)
            )   

        if os.path.isfile(sql_file_name_level1):
            conn = n_sql.connect(sql_file_name_level1)
        else:
            conn = n_sql.connect(sql_file_name_level1)
            try:
                with conn:
                    conn.execute('''
                                CREATE TABLE data (
                                	id BIGINT NOT NULL, 
                                	modified_date DATETIME, 
                                	data2 BLOB, 
                                	data3 BLOB,
                                	PRIMARY KEY (id)
                                )
                                ''')     
            except:
                raise Exception("Couldn't initialize database: {:s}".
                    format(sql_file_name_level1))

        update_necessary = False
        try:
            with conn:
                conn.execute('''
                    INSERT INTO data
                    (id, modified_date, data2, data3)
                    VALUES
                    (?, ?, NULL, ?)
                    ''', 
                    (self.id,
                    n_dat.datetime.now(),
                    pickle.dumps(value),)
                )

        except n_sql.IntegrityError:
            update_necessary = True
    
        if update_necessary:
            try:
                with conn:
                    conn.execute('''
                        UPDATE data 
                        SET modified_date=?,data3=? 
                        WHERE id=?
                    ''',
                    (n_dat.datetime.now(),
                     pickle.dumps(value),
                        self.id,)
                    )
    
            except:
                raise Exception("Couldn't write data")

        try:
            conn.commit()
            conn.close()
        except Exception as exc:
            raise Exception("Problem during data storage in sql db {:s}. Err:{:s}".
                format(sql_file_name_level1, exc.args[0]))
            
        return

    
    def __repr__(self):
        return "<Measurement({:d})>".format(self.id)

    def select_string(self):
        return "Measurement from: {0:s} with id:{1:d} and test: {2:s})".format(self.start_date.strftime("%d %B %Y at %X"),self.id,self.parameter)


#Shouldn't be used anymore because database is versioned now
#Base.metadata.create_all(engine) 

def create_database_on_central():
    sync_engine = create_engine(
        "sqlite:///" +
        c_paths.central_calibration_database_2015)
    
    Base.metadata.create_all(sync_engine) 
    
def create_database_on_local():
    sync_engine = create_engine(
        "sqlite:///" +
        c_paths.local_calibration_database_2015)
    
    Base.metadata.create_all(sync_engine) 


if __name__== '__main__':
    
    # no test code, because id control is 
    # available in module support
    create_database_on_local()
