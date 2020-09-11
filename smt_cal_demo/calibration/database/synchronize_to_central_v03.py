# -*- coding: utf-8 -*-
"""
Created on Sun Dec 23 16:30:37 2012

@author: Scheidt
"""

import os
import shutil
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.sql import select, update, bindparam
import datetime as dt
import smt_cal_demo.calibration.tokens.paths as c_paths

class TableNotAvailableError(Exception):
    pass

class ColumnNotAvailableError(Exception):
    pass


init_modified = dt.datetime(2000,1,1)
meta = MetaData()
copy_files = False

# former sqlite db
# new also locally a mysql database. This was necessary to enable database migration easily
local_engine = create_engine(
    "sqlite:///" + c_paths.local_calibration_database_2015, echo=False)

# engine on network
central_engine = create_engine(
    "sqlite:///" + c_paths.central_calibration_database_2015, echo=False)



local_table_names_available = local_engine.table_names()
local_table_names = ['customers', 'accounts', 'instruments', 'calibrations','certficates', 'testgroups',  'measurements', 'account_customer_ass', 'opts', 'alembic_version']
for table_available in local_table_names_available:
    if len([x for x in local_table_names if x==table_available]) == 0:
        raise TableNotAvailableError("Table " + table_available + " is not in local_table_names list.")

central_table_names = central_engine.table_names()

mod_changes = 0
for table_name in local_table_names:
    print(("Processing table: " + table_name))
    if (table_name == "opts" or 
        table_name == 'account_customer_ass' or
        table_name == 'alembic_version'):
        # skip above tables
        print("no synchronisation")
        pass
    else:    
        if table_name not in central_table_names:
            raise TableNotAvailableError("Table " + table_name + " not available")
        
        local_table = Table(table_name, meta, autoload=True, autoload_with=local_engine)
        central_table = Table(table_name, meta, autoload=True, autoload_with=central_engine)
        
        # check fields are the same
        for col_name in local_table.columns.keys():
            pass
            if (col_name in central_table.columns) == False:
                raise ColumnNotAvailableError("Column " + col_name + "in table " + table_name + " not available")
    
        upd = local_table.update().where(local_table.c.modified == None).values(modified = init_modified)
        
        s_local = select([local_table.c.id,local_table.c.modified]).order_by(local_table.c.id)
#        local_data = [(data[0],data[1],) for data in local_engine.execute(s_local)]
        local_data = local_engine.execute(s_local).fetchall()
        local_data = sorted(local_data, key=lambda x: x[0])
        
        local_ids = [x[0] for x in local_data]
    
        s_central = select([central_table.c.id,central_table.c.modified]).order_by(central_table.c.id)
#        central_data = [(data[0],data[1],) for data in central_engine.execute(s_central)]
        central_data = central_engine.execute(s_central).fetchall()
        central_data = sorted(central_data, key=lambda x: x[0])
        
        central_ids = [x[0] for x in central_data]
    
        all_ids = set(local_ids).union(set(central_ids))

        x = 0
        local_update = list()
        central_update = list()
        local_insert = list()
        central_insert = list()
        
        index_local = 0
        index_central = 0
        
        while index_local < len(local_ids) or index_central < len(central_ids):
            x += 1
            if x%1000 == 0:
                print("{:d} rows processed".format(x))


            local_only = False
            central_only = False
            both = False
            
            if index_local == len(local_ids):
                # nur noch on central
                zw_id = central_ids[index_central]
                central_only = True
            elif index_central == len(central_ids):
                zw_id = local_ids[index_local]
                local_only = True
            elif local_ids[index_local] == central_ids[index_central]:
                zw_id = local_ids[index_local]
                both = True
            elif local_ids[index_local] < central_ids[index_central]:
                zw_id = local_ids[index_local]
                local_only = True
            else:
                zw_id = central_ids[index_central]
                central_only = True
                
                
            
            if both:
                #on local and central, therefor modified date has to be evaluated
                local_date = local_data[index_local][1]
                if local_date is None:
                    local_date = init_modified
                    
                central_date = central_data[index_central][1]
                if central_date is None:
                    central_date = init_modified
                    
                if local_date > central_date:
                    #local data is newer update central
                    cp_data = local_engine.execute(
                        local_table.select().where(local_table.c.id == zw_id)).fetchone()

                    storedata = dict()
                    for col_name in cp_data.keys():
                        storedata[col_name] = cp_data[col_name]

                    # _id is the parameter for the where part in the update command
                    storedata["_id"] = cp_data["id"]
                    
                    central_update.append(storedata)

                elif central_date > local_date:
                    #central data is newer copy to local
                    cp_data = central_engine.execute(
                        central_table.select().where(central_table.c.id == zw_id)).fetchone()

                    storedata = dict()
                    for col_name in cp_data.keys():
                        storedata[col_name] = cp_data[col_name]
                    
                    # _id is the parameter for the where part in the update command
                    storedata["_id"] = cp_data["id"]

                    local_update.append(storedata)
                
                index_local += 1
                index_central += 1

            elif local_only:
                #only on local copy data to central
                cp_data = local_engine.execute(
                    local_table.select().where(local_table.c.id == zw_id)).fetchone()

                storedata = dict()
                for col_name in cp_data.keys():
                    storedata[col_name] = cp_data[col_name]

                central_insert.append(storedata)                        
                index_local += 1
                
            elif central_only:
                #only on central
                cp_data = central_engine.execute(
                    central_table.select().where(central_table.c.id == zw_id)).fetchone()

                storedata = dict()
                for col_name in cp_data.keys():
                    storedata[col_name] = cp_data[col_name]
                    
                local_insert.append(storedata)

                index_central += 1
            else:
                raise Exception("Logic error?")
                
        
        #make now the necessary upates
        if len(local_update) > 0:
            id_list = [x["id"] for x in local_update]
            local_engine.execute(
                local_table.update().where(local_table.c.id==bindparam("_id")),
                local_update)
            
            print("Updated local {:d} datasets".format(len(local_update)))
        if len(local_insert) > 0:
            id_list = [x["id"] for x in local_insert]
            local_engine.execute(local_table.insert(), local_insert)
            print("Inserted local {:d} datasets".format(len(local_insert)))

        if len(central_update) > 0:
            id_list = [x["id"] for x in central_update]
            central_engine.execute(
                central_table.update().where(central_table.c.id==bindparam("_id")),
                central_update)
            
            print("Updated central {:d} datasets".format(len(central_update)))
        
        if len(central_insert) > 0:
            id_list = [x["id"] for x in central_insert]
            central_engine.execute(central_table.insert(), central_insert)
            print("Inserted central {:d} datasets".format(len(central_insert)))

