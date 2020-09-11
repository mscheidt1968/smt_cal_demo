# -*- coding: utf-8 -*-
"""
Created on Sun Dec 23 16:30:37 2012

@author: Scheidt
"""

import os
import sqlite3 as n_sql
import datetime as n_dat
import zipfile as n_zip
import smt_cal_demo.calibration.tokens.paths as c_paths
import smt_cal_demo.calibration.database.support as n_sup


t1 = n_dat.datetime.now()
sql_path = os.path.join(
    c_paths.local_measurement_data_store)

if not os.path.isdir(sql_path):
    os.mkdir(sql_path)

measurements = n_sup.session.query(n_sup.Measurement).all()
x = 0
y = 0

data_store_file_list = dict()

for meas in measurements:
    id = meas.id
    start_date = meas.start_date
    if start_date is None:
        y += 1
    else:
        sql_file_name_level0 = os.path.join(
                sql_path,
                "y{:04d}m{:02d}".format(start_date.year,start_date.month),
            )   
        if not os.path.isdir(sql_file_name_level0):
            os.mkdir(sql_file_name_level0)
        sql_file_name_level1 = os.path.join(
                sql_file_name_level0,
                "d{:02d}.sqlite".format(start_date.day)
            )   

        if sql_file_name_level1 not in data_store_file_list:
            # create zip file
            new_conn = n_sql.connect(sql_file_name_level1)
            data_store_file_list[sql_file_name_level1] = new_conn
            new_conn.execute('''
                        CREATE TABLE data (
                        	id BIGINT NOT NULL, 
                        	modified_date DATETIME, 
                        	data2 BLOB, 
                        	data3 BLOB,
                        	PRIMARY KEY (id)
                        )
                        ''')            
            new_conn.commit()
        
        conn = data_store_file_list[sql_file_name_level1]
        
        data_file_name_old = os.path.join(
            c_paths.local_mid_data_store,
            "MID_{:d}".format(id),
            "procedure.pck2")
    
        if os.path.isfile(data_file_name_old):
            with open(data_file_name_old,"rb") as fp:
                conn.execute('''
                INSERT INTO data
                (id, modified_date, data2, data3)
                VALUES
                (?, ?, ?, NULL)
                ''', 
                (id,
                n_dat.datetime.now(),
                fp.read(),)
                )
        
        data_file_name_new = os.path.join(
            c_paths.local_mid_data_store,
            "MID_{:d}".format(id),
            "procedure.pck3")

        if os.path.isfile(data_file_name_new):
            with open(data_file_name_new,"rb") as fp:
                conn.execute('''
                INSERT INTO data
                (id, modified_date, data2, data3)
                VALUES
                (?, ?, NULL, ?)
                ''', 
                (id,
                n_dat.datetime.now(),
                fp.read(),)
                )
        
#        conn.commit()
    
        
    x += 1
    if x%1000 == 0:
        for name, conn in data_store_file_list.items():
            conn.commit()
            
        print(x)

for name, conn in data_store_file_list.items():
    conn.commit()
    conn.close()

print("Number of ids processed", x,
      "Number of ids without start_date", y)

t2 = n_dat.datetime.now()

print("Fertig", (t2-t1).total_seconds())
