# -*- coding: utf-8 -*-
"""
Created on Sun Dec 23 16:30:37 2012

@author: Scheidt
"""

import os
import time
import datetime as n_dat
import sqlite3 as n_sql
import smt_cal_demo.calibration.tokens.paths as c_paths
import smt_cal_demo.calibration.database.support as n_sup
import smt_cal_demo.utilities.easygui as n_eg

t0 = time.clock()

def cnv_datetime(s):
    return n_dat.datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f" )

if n_eg.ynbox("Full update"):
    skip_dat = n_dat.datetime(10,1,1)
else:
    skip_dat = n_dat.datetime.now() - n_dat.timedelta(days = 90)


measurements = list(n_sup.session.query(
                    n_sup.Measurement.id,
                    n_sup.Measurement.start_date).
                    filter(n_sup.Measurement.start_date > skip_dat).all())

sql_files = (["y{:04d}m{:02d}\\d{:02}.sqlite".format(
            x[1].year, 
            x[1].month, 
            x[1].day) for x in measurements])


x = 0
for sql_file_name in set(sql_files):
    dir_name = sql_file_name.split("\\")[0]

    local_sql_path = os.path.join(
        c_paths.local_measurement_data_store,
        dir_name)
    
    if not os.path.isdir(local_sql_path):
        os.mkdir(local_sql_path)

    central_sql_path = os.path.join(
        c_paths.central__measurement_data_store,
        dir_name)

    if not os.path.isdir(central_sql_path):
        os.mkdir(central_sql_path)

    
    local_sql_file = os.path.join(
        c_paths.local_measurement_data_store,
        sql_file_name)

    central_sql_file = os.path.join(
        c_paths.central__measurement_data_store,
        sql_file_name)
    
    if not os.path.isfile(local_sql_file):
        local_conn = n_sql.connect(local_sql_file)
        try:
            with local_conn:
                local_conn.execute('''
                        CREATE TABLE data (
                        	id BIGINT NOT NULL, 
                        	modified_date DATETIME, 
                        	data2 BLOB, 
                        	data3 BLOB,
                        	PRIMARY KEY (id)
                        )
                        ''')
        except:
            print("Couldn't create database")
    else:
        local_conn = n_sql.connect(local_sql_file)
    
    
    if not os.path.isfile(central_sql_file):
        central_conn = n_sql.connect(central_sql_file)
        try:
            with central_conn:
                central_conn.execute('''
                        CREATE TABLE data (
                        	id BIGINT NOT NULL, 
                        	modified_date DATETIME, 
                        	data2 BLOB, 
                        	data3 BLOB,
                        	PRIMARY KEY (id)
                        )
                        ''')
        except:
            print("Couldn't create database")
    else:
        central_conn = n_sql.connect(central_sql_file)
        pass

    local_data = [zw for zw in local_conn.execute('''
            SELECT id, modified_date FROM data
        ''')]

    local_ids = [zw[0] for zw in local_data]
    
    central_data = [zw for zw in central_conn.execute('''
            SELECT id, modified_date FROM data
        ''')]

    central_ids = [zw[0] for zw in central_data]

    all_ids  = set(local_ids).union(set(central_ids))
    
    for zw_id in all_ids:
        if zw_id in local_ids:
            if zw_id in central_ids:
                # test which is newer
                local_date = cnv_datetime(local_data[local_ids.index(zw_id)][1])
                central_date = cnv_datetime(central_data[central_ids.index(zw_id)][1])
                if local_date > central_date:
                    #local is newer -> update central
                    cur_data = local_conn.execute('''
                            SELECT data2, data3 FROM data
                            WHERE id=?
                        ''',(zw_id,)).fetchone()
                    central_conn.execute('''
                            UPDATE data SET
                                modified_date=?, data2=?, data3=?
                            WHERE
                                id = ?
                            ''',
                            (local_date,
                             cur_data[0],
                             cur_data[1],
                             zw_id))
                elif central_date > local_date:
                    #central is newer -> update local
                    cur_data = central_conn.execute('''
                            SELECT data2, data3 FROM data
                            WHERE id=?
                        ''',(zw_id,)).fetchone()
                    local_conn.execute('''
                            UPDATE data SET
                                modified_date=?, data2=?, data3=?
                            WHERE
                                id = ?
                            ''',
                            (central_date,
                             cur_data[0],
                             cur_data[1],
                             zw_id))
                pass
            else:
                #copy from local to central
                local_date = cnv_datetime(local_data[local_ids.index(zw_id)][1])
                cur_data = local_conn.execute('''
                        SELECT data2, data3 FROM data
                        WHERE id=?
                    ''',(zw_id,)).fetchone()
                central_conn.execute('''
                        INSERT INTO data
                            (id, modified_date, data2, data3) VALUES 
                            (?, ?, ?, ?)
                        ''',
                        (zw_id,
                         local_date,
                         cur_data[0],
                         cur_data[1],
                         ))
        else:
            # must be in central, copy therefore to local
            central_date = cnv_datetime(central_data[central_ids.index(zw_id)][1])
            cur_data = central_conn.execute('''
                    SELECT data2, data3 FROM data
                    WHERE id=?
                ''',(zw_id,)).fetchone()
            local_conn.execute('''
                    INSERT INTO data 
                        (id, modified_date, data2, data3) VALUES 
                        (?, ?, ?, ?)
                    ''',
                    (zw_id,
                     central_date,
                     cur_data[0],
                     cur_data[1],
                     ))

    try:
        local_conn.commit()
        local_conn.close()
    except Exception as exc:
        raise Exception("Could not commit and close local_conn. SqlFile: {:s}Err:{:s}".
            format(sql_file_name, exc.args[0]))

    try:
        central_conn.commit()
        central_conn.close()
    except Exception as exc:
        raise Exception("Could not commit and close central_conn. SqlFile: {:s}Err:{:s}".
            format(sql_file_name, exc.args[0]))
        
    x += 1
    
    
    print(x)


t1 = time.clock()
print("This took {:.1f} seconds".format(t1 - t0))