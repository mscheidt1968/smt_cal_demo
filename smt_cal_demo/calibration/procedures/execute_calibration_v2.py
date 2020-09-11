# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 14:55:46 2012

@author: Scheidt
"""

import datetime
import importlib as n_imp
import smt_cal_demo.utilities.easygui as eg
import smt_cal_demo.calibration.calibration_data.cal_spec_reader_v2 as csr
from smt_cal_demo.calibration.database.support import session,Calibration,Instrument,Measurement
from smt_cal_demo.calibration.models.support_v01 import Var

c_ui_title = "Calibration execution"
c_pass_text = 'passed'
c_cond_conf_text = 'cond. passed'
c_cond_failed_text = 'cond. failed'
c_failed_text = 'failed'
c_marginal_text = 'marginal'
c_no_result = 'no_result'
marginal_limit = 0.8

class InstrumentNotFoundError(Exception):
    pass

class ProcessingInstructionsError(Exception):
    pass


def verify_spec(proc, spec):
    test_result = c_no_result
    per_of_tol = 0.0
    if "testvar" in spec:
        test_var = spec["testvar"]
        if test_var == "delta":
            proc.delta = proc.result_list()[-2]
        if "abs" in spec:
            test_var_value = eval("proc." + test_var)
            if type(test_var_value) is Var:
                tol_max = spec["abs"]
                if (abs(test_var_value.v)<tol_max - test_var_value.u*2 and
                    tol_max > test_var_value.u*2):
                    test_result = c_pass_text
                    per_of_tol = abs(test_var_value.v/tol_max)
                elif abs(test_var_value.v)<tol_max + test_var_value.u*2:
                    if abs(test_var_value.v)<tol_max:
                        test_result = c_cond_conf_text
                        per_of_tol = abs(test_var_value.v/tol_max)
                    else:
                        test_result = c_cond_failed_text
                        per_of_tol = abs(test_var_value.v/tol_max)
                else:
                    test_result = c_failed_text
                    per_of_tol = abs(test_var_value.v/tol_max)
            else:
                print("Achtung type surprize", test_var_value, type(test_var_value))
                tol_max = spec["abs"]
                if abs(test_var_value)<marginal_limit*tol_max:
                    test_result = c_pass_text
                elif abs(test_var_value)<tol_max:
                    test_result = c_marginal_text
#                            raise Exception("Marginal not compatible to 17025:2018.")
                else:
                    test_result = c_failed_text
                per_of_tol = abs(test_var_value/tol_max)
        elif "rel" in spec:
            test_var_value = eval("proc." + test_var)
            tol_max = abs(spec["rel"] * proc.model.y.v)
            if abs(test_var_value)<marginal_limit*tol_max:
                test_result = c_pass_text
            elif abs(test_var_value)<tol_max:
                test_result = c_marginal_text
#                        raise Exception("Marginal not compatible to 17025:2018.")
            else:
                test_result = c_failed_text
            per_of_tol = abs(test_var_value/tol_max)
# this is buggy and shoul not be used any more
#                if spec.has_key("abs_y_max"):
#                    test_var_value = eval("proc." + test_var)
#                    tol_max = spec["abs_y_max"]
#                    tol_min = 2 * proc.model.y.v - spec["abs_y_max"]
#                    if test_var_value>tol_max or test_var_value<tol_min:
#                        test_result = c_failed_text
#                    else:
#                        test_result = c_pass_text
#                    per_of_tol = abs(((tol_max+tol_min)/2-test_var_value)/(tol_max-tol_min))
        if "between" in spec:
            test_var_value = eval("proc." + test_var)
            tol_min = float( spec["between"].split(" ")[0])
            tol_max = float( spec["between"].split(" ")[1])
            if type(test_var_value) is Var:
                per_of_tol = 2*abs(((tol_max+tol_min)/2-test_var_value.v)/(tol_max-tol_min))
                if (test_var_value.v < tol_max - test_var_value.u) and (test_var_value.v > tol_min + test_var_value.u):
                    test_result = c_pass_text
                elif (test_var_value.v < tol_max) and (test_var_value.v > tol_min):
                    test_result = c_cond_conf_text
                elif (test_var_value.v < tol_max + test_var_value.u) and (test_var_value.v > tol_min - test_var_value.u):
                    test_result = c_cond_failed_text
                else:
                    test_result = c_failed_text
            else:
                tol_min_marg = tol_min + (tol_max - tol_min) * (1-marginal_limit)/2
                tol_max_marg = tol_max - (tol_max - tol_min) * (1-marginal_limit)/2
                per_of_tol = 2*abs(((tol_max+tol_min)/2-test_var_value)/(tol_max-tol_min))
                if test_var_value>tol_max or test_var_value<tol_min:
                    test_result = c_failed_text
                elif test_var_value>tol_max_marg or test_var_value<tol_min_marg:
                    test_result = c_marginal_text
                    raise Exception("Marginal not compatible to 17025:2018.")
                else:
                    test_result = c_pass_text
        if "between_no_marg" in spec:
            test_var_value = eval("proc." + test_var)
            tol_min = float( spec["between_no_marg"].split(" ")[0])
            tol_max = float( spec["between_no_marg"].split(" ")[1])
            per_of_tol = None
            if hasattr(test_var_value,"v"):
                if test_var_value.v>tol_max or test_var_value.v<tol_min:
                    test_result = c_failed_text
                else:
                    test_result = c_pass_text
            else:
                if test_var_value>tol_max or test_var_value<tol_min:
                    test_result = c_failed_text
                else:
                    test_result = c_pass_text
                
    else:
        if "abs" in spec:
            test_result = "multiline"
            
    return (test_result,per_of_tol)


def execute_calData(calData, dut, environment, calibration = None, keep_open = False):
    """Executes a calibration as described in calData
    
    dut: Device object on which calibration is done
    environment: calibration environment
    calibration: if set this calibration will be extended"""
    
    [test_ids,test_points,proc_insts,sepcs] = csr.process_cal_spec(calData) 
    manufacturer = test_points[test_ids[0]]["manufacturer"]
    device_model = test_points[test_ids[0]]["model"]
    start_test_id = None
    
    if calibration is None:
        
        success = False
        while success == False:
            try:
                instruments=session.query(Instrument).filter(Instrument.manufacturer==manufacturer,
                                    Instrument.model==device_model).all()

                if len(instruments) == 0:
                    raise InstrumentNotFoundError("Not such instrument type in database yet")
                else:
                    choices = list()
                    for item in instruments:
                        choice = "SN: " +item.serial_number + " marked also:" + item.marked_id
                        choices.append( choice )
                        
                    answer = eg.choicebox("Enter serial number of that device","Calibration",choices=choices)

                    for item in instruments:
                        choice = "SN: " +item.serial_number + " marked also:" + item.marked_id
                        if choice == answer:
                            serial_number = item.serial_number

                    instrument = None
                    instruments=session.query(Instrument).filter(Instrument.manufacturer==manufacturer,
                                        Instrument.model==device_model,
                                        Instrument.serial_number==serial_number).all()
                                    
                    if instruments.__len__() == 0:
                        raise InstrumentNotFoundError("No instrument with this serial number found")
                    
                
                if instruments.__len__() > 1:
                    raise InstrumentNotFoundError("Database inconsistent. More than one instrument with this serial number found")
                
                success = True
            except Exception as exc:
                eg.msgbox("Error:" + exc.args[0] + "\nTry again")
            
            
        instrument=instruments[0]
        
        #check if last calibration was finished successfull
        last_calibration = session.query(Calibration).filter(Calibration.instrument_id == instrument.id).order_by(Calibration.start_date.desc()).first()
        if not last_calibration is None:
            if last_calibration.end_date is None:
                answer = eg.ynbox("Should last calibration be continued?")
                if answer == 1 and len(last_calibration.measurements) > 0:
                    answer_invalidate = eg.ynbox("Should last measurement be marked as invalid?")
                    if answer_invalidate == 1:
                        # fetch last measurement
                        last_measurement = last_calibration.measurements[-1]
                        last_measurement.validity = False
                        comment = eg.enterbox("What unvalidity comment should be made?", default = "mistype")
                        last_measurement.unvalidity_comment = comment
                        session.add(last_measurement)
                        session.commit()
                        
                    calibration = last_calibration
                    start_test_id = eg.choicebox("Select test to start",choices = test_ids)
                    
        if calibration is None:
            calibration = Calibration()
            calibration.start_date = datetime.datetime.now()
            calibration.instrument=instrument
            calibration.result = True
            answer = eg.enterbox("Please enter porject IDm, if available", c_ui_title)
            if answer != "":
                calibration.project_id_m = answer                
            calibration.operator = eg.choicebox("Select current operator",c_ui_title, choices = ["Operator #1", "Operator #2"])
            session.add(calibration)
            session.commit()
    else:
        instrument = calibration.instrument
    

    last_message = None
    last_test = None
    current_procedure = ""
    for test_id in test_ids:
        if not start_test_id is None:
            if test_id == start_test_id:
                start_test_id = None
        if start_test_id is None:
            if "procedure" in proc_insts[test_id]:
                if current_procedure != proc_insts[test_id]["procedure"]:
                    current_procedure = proc_insts[test_id]["procedure"]
                    prc_lib = n_imp.import_module(
                        "smt_cal_demo.calibration.procedures." +
                        proc_insts[test_id]["procedure"])
                    proc = prc_lib.Procedure()
                    print(proc.header_string())
            else:
                raise ProcessingInstructionsError("No procedure defined for calibration point:"+ test_id)
            
            repeat_measurement_outer = True
            while repeat_measurement_outer:
                repeat_measurement_outer = False
                try:
                    measurement = Measurement()
                    measurement.calibration = calibration
                    measurement.start_date =datetime.datetime.now()
                    measurement.parameter = test_id
                    if last_test is None:
                        try:
                            print("Test: " + test_points[test_id]["test"])
                            eg.msgbox(test_points[test_id]["test"],"New test")
                            last_test = test_points[test_id]["test"]
                            last_message = None
                        except:
                            print("No test attribute defined")
                    else:
                        try:
                            if last_test != test_points[test_id]["test"]:
                                print("Test: " + test_points[test_id]["test"])
                                last_message = None
                            last_test = test_points[test_id]["test"]
                        except:
                            print("No test attribute defined")
    
                    if "message" in proc_insts[test_id]:
                        if (last_message is None) or (last_message!=proc_insts[test_id]["message"]):
                            environment.switch_to_safe_state()
                            eg.msgbox(proc_insts[test_id]["message"],"Message")
                            last_message = proc_insts[test_id]["message"]                        
                    else:
                        last_message = None                        
                            
                    repeat_measurement = True
                    while repeat_measurement:
                        repeat_measurement = False
                        proc.execute(dut, environment, test_points[test_id], proc_insts[test_id])
                        print(proc.result_string())
                        test_result, per_of_tol = verify_spec(proc, sepcs[test_id])
                        if per_of_tol is None:
                            print("Test result: {:s}".format(test_result))
                        else:
                            print("Test result: {:s} using {:.1f}% of tolerance.".format(test_result, per_of_tol*100))
                            
                        print()
                        
                        if test_result not in [c_no_result, c_pass_text]:
                            msg = "Specification not met. Current result is {:s} using {:.1f}% of tolerance.".format(test_result, per_of_tol)
                            msg += "\nShould the measurement be repeated? (Repeat = Yes)"
                            answer = eg.ynbox(msg, "Spec issue")
                            if answer == True:
                                repeat_measurement = True
    
                    measurement.end_date=datetime.datetime.now()
                    measurement.validity = True
                except Exception as a:
                    print("Fehler: ", a)        
                    measurement.end_date=datetime.datetime.now()
                    measurement.validity = False
                    measurement.unvalidity_comment = "Fehler: " + str(a)

                    msg = "An error has occured. Message {:s}".format(str(a))
                    msg += "\nShould the measurement be repeated? (Repeat = Yes)"
                    answer = eg.ynbox(msg, "Spec issue")
                    if answer == True:
                        repeat_measurement_outer = True

            
            
            measurement.procedure = proc
            session.add(measurement)
            session.commit()    
    
    if keep_open == False:
        calibration.end_date = datetime.datetime.now()
    session.commit()

    if keep_open == False:
        dut.test_finished()
    environment.switch_to_safe_state()

    if keep_open == False:
        eg.msgbox("Measurement finished")
        instrument.last_calibration = datetime.datetime.now()
        answer = eg.indexbox("When should instrument be recalibrated",c_ui_title,("1 year","2 years","1 month","2 month","Don't mind"))
        delta_t = datetime.timedelta(days = 365)
        if answer == 0:
            delta_t = datetime.timedelta(days = 365)
        elif answer == 1:
            delta_t = datetime.timedelta(days = 2*365)
        elif answer == 2:
            delta_t = datetime.timedelta(days = 30)
        elif answer == 3:
            delta_t = datetime.timedelta(days = 60)
        if answer != 4:
            instrument.next_calibration = instrument.last_calibration + delta_t
            instrument.modified = datetime.datetime.now()
            session.add(instrument)
            session.commit()
    
    return calibration
        