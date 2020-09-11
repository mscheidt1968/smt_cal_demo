# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 09:45:33 2013

@author: Scheidt
"""

import numpy as np

import sys
import time
import datetime
import logging
import imp
import importlib
import subprocess
import winsound

from PyQt5 import QtGui, QtCore, QtWidgets


import smt_cal_demo.utilities.easygui as eg

from smt_cal_demo.calibration.guis.main_ui import select_calibration_dialog_v01
from smt_cal_demo.calibration.guis.main_ui import select_instrument_dialog_v01
from smt_cal_demo.calibration.guis.main_ui import calibration_information_ui_v01
from smt_cal_demo.calibration.guis.main_ui.main_calibration_ui_v01 import Ui_MainWindow
import smt_cal_demo.calibration.calibration_data.cal_spec_reader_v2 as n_cal_data
from smt_cal_demo.calibration.database.support import session, Calibration, Instrument, Measurement
import smt_cal_demo.calibration.tokens.reporting as c_rpt
import smt_cal_demo.calibration.tokens.testpoint_keys as c_tst
from smt_cal_demo.calibration.models.support_v01 import Var
import smt_cal_demo.calibration.calibration_data
import threading
import smt_cal_demo.calibration.tokens.execution_modes as c_exm

#c_exm.execution_mode = set([c_exm.no_io])

c_st_not_init = "Not initialized"
c_st_rdy_execute_next = "Ready to execute next"
c_st_executing = "Executing"
c_st_ready_to_store = "Ready to store"
c_st_last_executed = "Last executed"
c_st_error = "Error"

c_cmd_nothing = "Nothing"
c_cmd_do_not_block = "Do not block"
c_cmd_execute_next = "Execute Next"
c_cmd_restart = "Restart"
c_cmd_store_measurement = "Store Measurement"
c_cmd_dont_store_measurement = "Dont Store Measurement"
c_cmd_close_calibration = "Close Calibration"

c_ui_title = "Calibration execution"


class MeasurementControlThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.command_event = threading.Event()
        self.ui_command = None
        self.ui_command_done = True
        self.error_msg = "Ok"
        self.calDataHandler = None
        self.current_state = c_st_not_init
        self.current_test_index = None
        self.instrument = None
        self.calibration = None

    def run(self):
        self.stop = False
        while self.stop is False:
            if self.command_event.wait(5):
                self.command_event.clear()
                self.ui_command_done = False
                if self.ui_command == c_cmd_restart:
                    # setup DUT setup environment
                    self.process_Restart()
                elif self.ui_command == c_cmd_execute_next:
                    self.process_Execute_Next()
                elif self.ui_command == c_cmd_store_measurement:
                    self.process_Store_Measurement()
                elif self.ui_command == c_cmd_dont_store_measurement:
                    self.process_DONT_Store_Measurement()
                elif self.ui_command == c_cmd_close_calibration:
                    self.process_Close_Calibration()
                elif self.ui_command == c_cmd_do_not_block:
                    while self.ui_command == c_cmd_do_not_block:
                        print("no block")
                        time.sleep(0.1)
                else:
                    self.ui_command_done = True
            else:
                print("UI died")
                self.stop = True
        print("Measurement Thread ended")
        self.stop = False

    def process_Close_Calibration(self):
        no_err = True
        print("Closing calibration")
        last_state = self.current_state
        self.current_state = c_st_executing

        self.calibration.end_date = datetime.datetime.now()
        session.commit()

        self.environment.switch_to_safe_state()
        self.dut.switch_to_safe_state()

        self.instrument.last_calibration = datetime.datetime.now()
        answer = eg.indexbox(
            "When should instrument be recalibrated",
            c_ui_title,
            ("1 year", "2 years", "1 month", "2 month", "Don't mind"))

        delta_t = datetime.timedelta(days=365)
        if answer == 0:
            delta_t = datetime.timedelta(days=365)
        elif answer == 1:
            delta_t = datetime.timedelta(days=2 * 365)
        elif answer == 2:
            delta_t = datetime.timedelta(days=30)
        elif answer == 3:
            delta_t = datetime.timedelta(days=60)
        if answer != 4:
            self.instrument.next_calibration = self.instrument.last_calibration + delta_t
            self.instrument.modified = datetime.datetime.now()
            session.add(self.instrument)
            session.commit()

        self.current_state = last_state
        self.ui_command = None
        self.ui_command_done = True

    def find_next_test(self, no_err):
        cdh = self.calDataHandler
        if self.current_test_index == -1:
            restart = True
        else:
            restart = False

        if no_err:
            next_test_found = False
            while next_test_found is False:
                if self.current_test_index + 1 < len(cdh.test_ids):
                    self.current_test_index += 1
                    self.current_state = c_st_rdy_execute_next
                    test_id = cdh.test_ids[self.current_test_index]
                    if cdh.executable_nodes[test_id].execute:
                        next_test_found = True
                else:
                    next_test_found = True
                    if restart:
                        self.current_state = c_st_error
                        self.error_msg = "No test enabled"
                    else:
                        self.current_state = c_st_last_executed
                        self.environment.release()
                        self.dut.release()
        else:
            self.current_state = c_st_error

    def process_Store_Measurement(self):
        no_err = True
        print("Storing measurement")
        self.current_state = c_st_executing
        session.add(self.measurement)
        session.commit()

        self.find_next_test(no_err)

        self.ui_command = None
        self.ui_command_done = True

    def process_DONT_Store_Measurement(self):
        no_err = True
        print("Not Storing measurement")
        print(self.measurement)
        self.current_state = c_st_executing

        self.find_next_test(no_err)

        self.ui_command = None
        self.ui_command_done = True

    def process_Restart(self):
        # setup DUT setup environment
        print("Restart started")
        cdh = self.calDataHandler
        no_err = True
        if "environment" not in cdh.proc_instrs[cdh.test_ids[0]]:
            self.error_msg = "No enviroment specified"
            no_err = False
        elif "dut" not in cdh.proc_instrs[cdh.test_ids[0]]:
            self.error_msg = "No dut specified"
            no_err = False

        if no_err:
            try:
                imported_module = importlib.import_module(
                    "smt_cal_demo.calibration." +
                    str(cdh.proc_instrs[cdh.test_ids[0]]["environment"]))

            except Exception as ex:
                self.error_msg = "Could not load environment " + ex.message
                print(ex.message)
                no_err = False

        if no_err:
            try:
                if not(self.environment is None):
                    self.environment.release()
            except:
                pass
            self.environment = None

        if no_err:
            try:
                self.environment = imported_module.Environment()
            except Exception as exc:
                self.error_msg = "Could not assign environment"
                print(exc)
                no_err = False

        if no_err:
            try:
                imported_module = importlib.import_module(
                    "smt_cal_demo.calibration." +
                    str(cdh.proc_instrs[cdh.test_ids[0]]["dut"]))
            except Exception as ex:
                self.error_msg = "Could not load dut"
                no_err = False

        if no_err:
            try:
                if not(self.dut is None):
                    self.dut.release()
            except:
                pass

            self.dut = None

        if no_err:
            try:
                self.dut = imported_module.DUT()
            except:
                self.error_msg = "Could not assign dut"
                no_err = False

        if no_err:
            try:
                print(cdh.test_points[cdh.test_ids[0]])
                self.manufacturer = cdh.test_points[cdh.test_ids[0]]["manufacturer"]
            except:
                self.error_msg = "No manufacturer specified"
                no_err = False

        if no_err:
            try:
                self.device_model = cdh.test_points[cdh.test_ids[0]]["model"]
            except:
                self.error_msg = "No device model specified"
                no_err = False

        self.current_test_index = -1
        self.last_message = None
        self.last_test = None
        self.current_procedure = ""

        self.find_next_test(no_err)

        self.ui_command = None
        self.ui_command_done = True

    def process_Execute_Next(self):
        print("Excute Next started")
        cdh = self.calDataHandler
        no_err = True
        calibration = self.calibration
        if (self.current_state != c_st_rdy_execute_next and
                self.current_state != c_st_ready_to_store):
            self.error_msg = "Wrong state whenn trying to excute next"
            no_err = False

        if no_err:
            self.current_state = c_st_executing
            test_id = cdh.test_ids[self.current_test_index]

            if "procedure" in cdh.proc_instrs[test_id]:
                if self.current_procedure != cdh.proc_instrs[test_id]["procedure"]:
                    self.current_procedure = cdh.proc_instrs[test_id]["procedure"]
                    prc_lib = importlib.import_module(
                        "smt_cal_demo.calibration." +
                        "procedures." +
                        cdh.proc_instrs[test_id]["procedure"])

                    self.proc = prc_lib.Procedure()
                    if c_tst.report_type in cdh.proc_instrs[test_id]:
                        self.proc.report_type = cdh.proc_instrs[test_id][c_tst.report_type]
                    print(self.proc.header_string())
            else:
                raise Exception("No procedure defined for calibration point:" + test_id)
            try:
                self.measurement = Measurement()
                self.measurement.calibration = calibration
                self.measurement.start_date = datetime.datetime.now()
                self.measurement.parameter = test_id
                if self.last_test is None:
                    try:
                        print("Test: " + cdh.test_points[test_id]["test"])
                        eg.msgbox(cdh.test_points[test_id]["test"], "New test")
                        self.last_test = cdh.test_points[test_id]["test"]
                        self.last_message = None
                    except:
                        print("No test attribute defined")
                else:
                    try:
                        if self.last_test != cdh.test_points[test_id]["test"]:
                            print("Test: " + cdh.test_points[test_id]["test"])
                            self.last_message = None
                        self.last_test = cdh.test_points[test_id]["test"]
                    except:
                        print("No test attribute defined")

                if "message" in cdh.proc_instrs[test_id]:
                    if (self.last_message is None) or (self.last_message != cdh.proc_instrs[test_id]["message"]):
                        self.environment.switch_to_safe_state()
                        eg.msgbox(cdh.proc_instrs[test_id]["message"], "Message")
                        self.last_message = cdh.proc_instrs[test_id]["message"]
                else:
                    self.last_message = None

                self.proc.execute(self.dut, self.environment, cdh.test_points[test_id], cdh.proc_instrs[test_id])
                print(self.proc.result_string())
                self.measurement.end_date = datetime.datetime.now()
                self.measurement.validity = True
            except Exception as a:
                print("Fehler: " + a.args[0])
                self.measurement.end_date = datetime.datetime.now()
                self.measurement.validity = False
                self.measurement.unvalidity_comment = "Fehler: " + a.args[0]

            self.measurement.procedure = self.proc

        if no_err:
            self.current_state = c_st_ready_to_store
        else:
            self.current_state = c_st_error

        print("Ended Execute")
        self.ui_command = None
        self.ui_command_done = True
        if True:
            Freq = 2500  # Set Frequency To 2500 Hertz
            Dur = 1000  # Set Duration To 1000 ms == 1 second
            winsound.Beep(Freq, Dur)
#            sound_thread = threading.Thread(target = self.remember_me)
#            sound_thread.start()

    def remember_me():
        Freq = 2500  # Set Frequency To 2500 Hertz
        Dur = 1000  # Set Duration To 1000 ms == 1 second
        winsound.Beep(Freq, Dur)


class CalDataHandler(object):
    """This class handels access to information
    related to the calibration definition data.
    It opens new files
    It hold data
    It creates a tree structure for the testpoint data
    """

    def __init__(self):
        self.test_ids = list()

    def open_file(self, sequence_file):
        if sequence_file == "":
            logging.info("No file selected for import ")
            return False
        try:
            imported_module = imp.load_source("dynamic_loaded_source", str(sequence_file))
        except Exception as ex:
            print("Could not import module {:s}, error: {:s}".format(sequence_file, str(ex)))
            logging.info("Could not import module {:s}, error: {:s}".format(sequence_file, str(ex.args[0])))
            return False

        print("ok1")
        try:
            cal_data = imported_module.calData
        except:
            logging.info("No calibration data in module {:s}".format(sequence_file))
            return False

        print("ok2")
        self.process_cal_data(cal_data)
        print("ok3")
        return True

    def process_cal_data(self, cal_data):
        self.executable_nodes = dict()
        (self.test_ids, self.test_points, self.proc_instrs, self.specs) = n_cal_data.process_cal_spec(cal_data)
        test_ids = list(self.test_ids)
        test_points = dict()
        for key, item in self.test_points.items():
            test_points[key] = dict(item)
        # each test_id must create a single node without childs

        max_common_test_point = dict(test_points[test_ids[0]])

        for test_id in self.test_ids:
            current_test_point = test_points[test_id]
            for key in list(current_test_point.keys()):
                if key in max_common_test_point:
                    if max_common_test_point[key] != current_test_point[key]:
                        max_common_test_point.pop(key)

        if len(max_common_test_point) == 0:
            raise Exception("No common testpoint data")

        self.rootNode = Testpoint_Node(None, max_common_test_point)

        testpoints_start = test_points
        for test_id in test_ids:
            current_test_point = testpoints_start[test_id]
            for key in list(max_common_test_point.keys()):
                if key in current_test_point:
                    current_test_point.pop(key)
            testpoints_start[test_id] = current_test_point

        self.divide(self.rootNode, test_ids, testpoints_start)

    def divide(self, node, test_ids, testpoints):
        finished = False
        current_start_index = 0
        while not finished:
            max_common_test_point_of_group = dict(testpoints[test_ids[current_start_index]])
            group_finished = False
            current_end_index = current_start_index

            while not group_finished:
                im_max_common_test_point = dict(max_common_test_point_of_group)
                current_test_point = testpoints[test_ids[current_end_index]]
                for key in list(max_common_test_point_of_group.keys()):
                    if (key in current_test_point) is False:
                        im_max_common_test_point.pop(key)
                    elif current_test_point[key] != max_common_test_point_of_group[key]:
                        im_max_common_test_point.pop(key)

                if len(im_max_common_test_point) == 0:
                    group_finished = True
                    current_end_index -= 1
                elif current_end_index == len(test_ids) - 1:
                    group_finished = True
                    max_common_test_point_of_group = dict(im_max_common_test_point)
                else:
                    current_end_index += 1
                    max_common_test_point_of_group = dict(im_max_common_test_point)

            if current_end_index > current_start_index:
                # further divide is necessary
                testpoints_iter = dict()
                for k1 in range(current_start_index, current_end_index + 1):
                    current_test_point = testpoints[test_ids[k1]]
                    for key in list(max_common_test_point_of_group.keys()):
                        if key in current_test_point:
                            current_test_point.pop(key)
                    testpoints_iter[test_ids[k1]] = current_test_point
                new_node = Testpoint_Node(parent=node,
                                          testpoint_data=max_common_test_point_of_group,
                                          calDataHandler=self)
                self.divide(new_node, test_ids[current_start_index:current_end_index + 1], testpoints_iter)
            else:
                new_node = Testpoint_Node(parent=node,
                                          testpoint_data=max_common_test_point_of_group,
                                          calDataHandler=self)
                new_node.test_id = test_ids[current_start_index]
                self.executable_nodes[test_ids[current_start_index]] = new_node
                #print str(new_node.testpoint_data_all())
            if current_end_index >= len(test_ids) - 1:
                finished = True
            else:
                current_start_index = current_end_index + 1

    def correlate_measurements(self, calibration):

        self.calibration = calibration

        for node in list(self.executable_nodes.values()):
            node.measurements = list()

        if calibration is not None:
            for measurement in calibration.measurements:
                test_id = measurement.parameter
                for key, node in list(self.executable_nodes.items()):
                    if key == test_id:
                        node.measurements.append(measurement)


class Testpoint_Node(object):

    def __init__(self, parent=None, testpoint_data={}, calDataHandler=None):
        self.testpoint_data = testpoint_data
        self.calDataHandler = calDataHandler
        self.test_id = None
        self.execute = True
        self.measurements = list()
        self.is_current_node = False
        self.childs = list()
        self.parent = parent
        if not (parent is None):
            self.parent.append_child(self)

    def test_all_child_nodes_same_execute_state(self, node, test_value=None):
        if test_value is None:
            test_value = node.childs[0].execute

        all_the_same = True
        for child in node.childs:
            if len(child.childs) == 0:
                if child.execute != test_value:
                    all_the_same = False
            else:
                if not self.test_all_child_nodes_same_execute_state(child, test_value):
                    all_the_same = False

        return all_the_same

    def set_node_execute_flags(self, node, new_value):
        node.execute = new_value
        for k1 in range(len(node.childs)):
            child_node = node.childs[k1]
            self.set_node_execute_flags(child_node, new_value)

    def update_execute_of_parent(self, node):
        if self.test_all_child_nodes_same_execute_state(node):
            node.execute = node.childs[0].execute

        if not (node.parent is None):
            self.update_execute_of_parent(node.parent)

    def toggle_execute(self):
        if len(self.childs) == 0:
            self.execute = not self.execute
            if not (self.parent is None):
                self.update_execute_of_parent(self.parent)
        else:
            new_value = not self.execute
            self.set_node_execute_flags(self, new_value)
            if not (self.parent is None):
                self.update_execute_of_parent(self.parent)

    def testpoint_data_all(self):
        if self.parent is None:
            zw = dict()
        else:
            zw = self.parent.testpoint_data_all()
        zw.update(self.testpoint_data)
        return zw

    def append_child(self, child):
        self.childs.append(child)
        return

    def testpoint_to_text(self, data=dict()):
        zw = ""
        for key in data:
            if zw != "":
                zw += "\n"
            zw += "{:20s} : {:20s}".format(key, str(data[key]))
        return zw


class Testpoint_ItemModel(QtCore.QAbstractItemModel):

    def __init__(self, rootNode=None):
        super(Testpoint_ItemModel, self).__init__()
        self.rootNode = rootNode

    def index_node(self, node):
        return self.createIndex(0, 0, node)

    def parent(self, index):
        node = index.internalPointer()
        parent = node.parent
        if parent is None:
            return QtCore.QModelIndex()

        row = None
        k1 = 0
        for child in parent.childs:
            if child is node:
                row = k1
            k1 += 1

        if row is None:
            raise Exception("fehler im Baum")

        return self.createIndex(0, 0, parent)

    def index(self, row, col, parent):
        if parent.internalPointer() is None:
            if row == 0 and col <= 1:
                return self.createIndex(row, col, self.rootNode)
            else:
                return QtCore.QModelIndex()
        node = parent.internalPointer()
        if col > 1:
            return QtCore.QModelIndex()
        else:
            zw = self.createIndex(row, col, node.childs[row])
            return zw

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 2

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.internalPointer() is None:
            return 1
        node = parent.internalPointer()
        return len(node.childs)

    def test_all_nodes_same_execute_state(self, node, test_value=None):
        if test_value is None:
            test_value = node.childs[0].execute

        all_the_same = True
        for child in node.childs:
            if len(child.childs) == 0:
                if child.execute != test_value:
                    all_the_same = False
            else:
                if not self.test_all_nodes_same_execute_state(child, test_value):
                    all_the_same = False

        return all_the_same

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                return node.testpoint_to_text(node.testpoint_data)
            elif index.column() == 1:
                if len(node.childs) == 0:
                    if node.execute:
                        return "Yes"
                    else:
                        return "Don't"
                else:
                    if self.test_all_nodes_same_execute_state(node):
                        if node.execute:
                            return "Yes"
                        else:
                            return "Don't"
                    else:
                        return "partial"
        elif role == QtCore.Qt.BackgroundRole and index.column() == 0:
            if len(node.childs) == 0:
                if node.is_current_node:
                    return QtGui.QBrush(QtGui.QColor("green"))
                else:
                    return QtGui.QBrush(QtGui.QColor("grey"))

            else:
                return QtGui.QBrush(QtGui.QColor("white"))
        return None

    def headerData(self, section, orientation, role):
        if (
                orientation == QtCore.Qt.Horizontal and
                role == QtCore.Qt.DisplayRole and
                section == 0):
            return 'Name'
        if (
                orientation == QtCore.Qt.Horizontal and
                role == QtCore.Qt.DisplayRole and
                section == 1):
            return 'Execute'
        return None


class ExecuteSynchronize(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        path = imp.find_module("guis")[1]
        path_sync = path.replace("kalibrieren\\guis", "data_management\\synchrotest2.py")
        return_code = subprocess.call("python.exe " + path_sync, shell=True)
        print("Synchronize ended with return code:")
        print(return_code)


class CalApp(QtWidgets.QMainWindow):

    def __init__(self):
        super(CalApp, self).__init__()
        self.initUI()

    def initUI(self):
        self.localMeasurementStatus = "Not initialized"
        self.instrument = None

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.cal_handler = CalDataHandler()

        self.ui.actionLoad_Test_Sequence_Data.triggered.connect(self.load_test_sequence_data)
        self.ui.actionSelect_Calibration.triggered.connect(self.select_calibration)
        self.ui.actionSelect_Instrument.triggered.connect(self.select_instrument)
        self.ui.actionPause_before_Save.triggered.connect(self.pause_state_changed)
        self.ui.actionContinue_with_Save.triggered.connect(self.save_and_continue_measurements)
        self.ui.actionContinue_with_Save.setEnabled(False)
        self.ui.actionNext_without_Save.triggered.connect(self.dont_save_and_continue_measurements)
        self.ui.actionNext_without_Save.setEnabled(False)
        self.ui.actionRepeat.triggered.connect(self.repeat_measurement)
        self.ui.actionRepeat.setEnabled(False)

        self.ui.actionSynchronize.triggered.connect(self.call_synchronize)

        self.ui.treeVwTestpoints.clicked.connect(self.item_clicked)

        self.ui.actionStart_Measurements.triggered.connect(self.start_measurements)

        self.next_measurement_index = -1
        self.current_test_id = None
        self.measurement_ctl = MeasurementControlThread()

        self.communication_timer = QtCore.QTimer()
        self.communication_timer.setInterval(200)
        self.communication_timer.timeout.connect(self.communication_timer_event)

        self.measurement_ctl.start()
        self.communication_timer.start()

        self.lblStatusMeasurement = QtWidgets.QLabel()
        self.ui.statusbar.addPermanentWidget(self.lblStatusMeasurement)

#       test_file = "C:\\Users\\Scheidt\\Documents\\Firma\\SW\\entwicklung\\kalibrieren\\calibration_data\\Scheidt_mt\\140105_MSC_10_Zener_Reference_V3_v01.py"
#       self.load_test_sequence_data_from_file(test_file)
        self.update_setting_dependend_ui()

    def closeEvent(self, event):
        # Your desired functionality here
        print('Close button pressed')
        self.measurement_ctl.stop = True
        while self.measurement_ctl.stop:
            time.sleep(0.1)
        print("Stopped now")
        self.communication_timer.stop()

    def pause_state_changed(self, *args):
        print(args)
        print(self.ui.actionPause_before_Save.isChecked())

    def print_current_test_data(self):
        test_index = self.measurement_ctl.current_test_index
        test_id = self.cal_handler.test_ids[test_index]

        info = ""
        for key, item in list(self.cal_handler.test_points[test_id].items()):
            if info != "":
                info += "\n"

            info += "{:20s} : {:20s}".format(str(key), str(item))

        self.ui.lblCurrTestTestpointInfo.setText(info)

        info = ""
        for key, item in list(self.cal_handler.proc_instrs[test_id].items()):
            if info != "":
                info += "\n"
            info += "{:20s} : {:20s}".format(str(key), str(item))

        self.ui.lblCurrTestProcessingInstr.setText(info)

        info = ""
        for key, item in list(self.cal_handler.specs[test_id].items()):
            if info != "":
                info += "\n"
            info += "{:20s} : {:20s}".format(str(key), str(item))

        self.ui.lblCurrTestSpecs.setText(info)

    def printLatestResult(self):
        measurement = self.measurement_ctl.measurement
        info = self.createResultStringFromMeasurement(measurement)
        self.ui.lblLastMeasurmentResult.setText(info)

    def createResultStringFromMeasurement(self, measurement):
        if not hasattr(measurement, "procedure"):
            return "-"
        if not hasattr(measurement.procedure, "header_list"):
            return "-"

        hl = measurement.procedure.header_list()
        rl = measurement.procedure.result_list()

        info = ""
        if type(hl[0]) is str:
            for k1 in range(len(hl)):
                info += "{:16s}".format(hl[k1])

            info += "\n"
            for k1 in range(len(hl)):
                if type(rl[k1]) is str:
                    info += "{:16s}".format(rl[k1])
                else:
                    info += "{:16g}".format(rl[k1])

        else:
            for k1 in range(len(hl)):
                if len(hl[k1]) == 3:
                    info += "{:>16s}".format(hl[k1][0])
                elif hl[k1][3] != c_rpt.exp_unc:
                    info += "{:>16s}".format(hl[k1][0])
                else:
                    info += "{:>16s} {:>16s}".format(hl[k1][0], "Unc.")

            info += "\n"
            for k1 in range(len(hl)):
                if len(hl[k1]) == 3:
                    if (type(rl[k1]) is str) or (type(rl[k1]) is str):
                        info += "{:>16s}".format(rl[k1])
                    elif (type(rl[k1]) is Var):
                        info += "{:16f}".format(rl[k1].v)
                    else:
                        info += "{:16f}".format(rl[k1])
                elif hl[k1][3] != c_rpt.exp_unc:
                    if (type(rl[k1]) is str) or (type(rl[k1]) is str):
                        info += "{:>16s}".format(rl[k1])
                    elif (type(rl[k1]) is Var):
                        info += "{:16f}".format(rl[k1].v)
                    else:
                        info += "{:16f}".format(rl[k1])
                else:
                    info += "{:16f} {:16f}".format(rl[k1].v, rl[k1].u)

        return info

    def communication_timer_event(self, *args):
        # update information about current or following measurement
        update_measurement_info_necessary = False

        if (
                self.next_measurement_index is None and
                self.measurement_ctl.current_test_index is not None):
            update_measurement_info_necessary = True

        elif (
                not (self.next_measurement_index is None) and
                self.measurement_ctl.current_test_index is None):
            update_measurement_info_necessary = True

        elif (self.next_measurement_index != self.measurement_ctl.current_test_index):
            update_measurement_info_necessary = True

        if update_measurement_info_necessary:
            if self.measurement_ctl.current_test_index is None:
                self.ui.lblCurrTestTestpointInfo.setText("next Test not defined")
                self.ui.lblCurrTestSpecs.setText("next Test not defined")
                self.ui.lblCurrTestProcessingInstr.setText("next Test not defined")
            else:
                self.print_current_test_data()

        if self.measurement_ctl.ui_command_done is True:
            self.ui.statusbar.showMessage(self.measurement_ctl.error_msg)
            ch = self.cal_handler
            model = self.ui.treeVwTestpoints.model
            mctl = self.measurement_ctl
            if self.current_test_id is None:
                if not (mctl.current_test_index is None):
                    self.current_test_id = mctl.current_test_index
                    self.cal_handler.executable_nodes[ch.test_ids[self.current_test_id]].is_current_node = True
                    self.ui.treeVwTestpoints.update(model().index_node(ch.executable_nodes[ch.test_ids[self.current_test_id]]))
            else:
                if (mctl.current_test_index is None):
                    zw = self.current_test_id
                    self.cal_handler.executable_nodes[ch.test_ids[zw]].is_current_node = False
                    self.current_test_id = None
                    self.ui.treeVwTestpoints.update(model().index_node(ch.executable_nodes[ch.test_ids[zw]]))
                elif mctl.current_test_index != self.current_test_id:
                    zw = self.current_test_id
                    self.cal_handler.executable_nodes[ch.test_ids[zw]].is_current_node = False
                    self.current_test_id = mctl.current_test_index
                    self.cal_handler.executable_nodes[ch.test_ids[self.current_test_id]].is_current_node = True
                    self.ui.treeVwTestpoints.update(model().index_node(ch.executable_nodes[ch.test_ids[zw]]))
                    self.ui.treeVwTestpoints.update(model().index_node(ch.executable_nodes[ch.test_ids[self.current_test_id]]))

            if self.localMeasurementStatus == "Request to start":
                if (
                        self.measurement_ctl.current_state == c_st_not_init or
                        self.measurement_ctl.current_state == c_st_error or
                        self.measurement_ctl.current_state == c_st_ready_to_store or
                        self.measurement_ctl.current_state == c_st_last_executed or
                        self.measurement_ctl.current_state == c_st_rdy_execute_next):
                    self.measurement_ctl.ui_command = c_cmd_restart
                    self.localMeasurementStatus = "Waiting for start to complete"
            elif self.localMeasurementStatus == "Waiting for start to complete":
                if (self.measurement_ctl.current_state == c_st_rdy_execute_next):
                    self.measurement_ctl.ui_command = c_cmd_execute_next
                    self.localMeasurementStatus = "Waiting for end of measurement"
                elif (self.measurement_ctl.current_state == c_st_last_executed):
                    self.localMeasurementStatus == "All measurements done"
            elif self.localMeasurementStatus == "Waiting for end of measurement":
                if (self.measurement_ctl.current_state == c_st_ready_to_store):
                    self.localMeasurementStatus = "Measurement available"
                    try:
                        self.printLatestResult()
                    except Exception as exc:
                        print("Problem to print the result:", exc.args[0])

            elif self.localMeasurementStatus == "Measurement available":
                if not self.ui.actionPause_before_Save.isChecked():
                    self.measurement_ctl.ui_command = c_cmd_store_measurement
                    self.localMeasurementStatus = "Data handling"
                else:
                    self.ui.actionContinue_with_Save.setEnabled(True)
                    self.ui.actionNext_without_Save.setEnabled(True)
                    self.ui.actionRepeat.setEnabled(True)
            elif self.localMeasurementStatus == "Repeat":
                if (self.measurement_ctl.current_state == c_st_ready_to_store):
                    self.ui.actionContinue_with_Save.setEnabled(False)
                    self.ui.actionNext_without_Save.setEnabled(False)
                    self.ui.actionRepeat.setEnabled(False)
                    self.measurement_ctl.ui_command = c_cmd_execute_next
                    self.localMeasurementStatus = "Waiting for end of measurement"
            elif self.localMeasurementStatus == "Save Measurement":
                self.ui.actionContinue_with_Save.setEnabled(False)
                self.ui.actionNext_without_Save.setEnabled(False)
                self.ui.actionRepeat.setEnabled(False)
                self.measurement_ctl.ui_command = c_cmd_store_measurement
                self.localMeasurementStatus = "Data handling"
            elif self.localMeasurementStatus == "Dont Save Measurement":
                self.ui.actionContinue_with_Save.setEnabled(False)
                self.ui.actionNext_without_Save.setEnabled(False)
                self.ui.actionRepeat.setEnabled(False)
                self.ui.actionContinue_with_Save.setEnabled(False)
                self.measurement_ctl.ui_command = c_cmd_dont_store_measurement
                self.localMeasurementStatus = "Data handling"
            elif self.localMeasurementStatus == "Data handling":
                if (self.measurement_ctl.current_state == c_st_rdy_execute_next):
                    self.measurement_ctl.ui_command = c_cmd_execute_next
                    self.localMeasurementStatus = "Waiting for end of measurement"
                elif (self.measurement_ctl.current_state == c_st_last_executed):
                    # here code to close calibration
                    self.measurement_ctl.calibration = self.calibration
                    self.measurement_ctl.instrument = self.instrument
                    self.measurement_ctl.ui_command = c_cmd_close_calibration
                    self.localMeasurementStatus = "Wait for closing calibration"
            elif self.localMeasurementStatus == "Wait for closing calibration":
                self.localMeasurementStatus = "All measurements done"

            self.measurement_ctl.command_event.set()
            self.lblStatusMeasurement.setText(self.localMeasurementStatus)

    def testpoint_dataChanged(self, *args):
        print(args)

    def update_parent_nodes(self, index):
        model = self.ui.treeVwTestpoints.model()
        index_parent = model.parent(index)
        if not (index_parent.isValid()):
            return
        else:
            index_to_update = model.createIndex(index_parent.row(), 1, index_parent.internalPointer())
            self.ui.treeVwTestpoints.update(index_to_update)
            self.update_parent_nodes(index_to_update)

    def update_child_nodes(self, index):
        model = self.ui.treeVwTestpoints.model()
        node = index.internalPointer()
        self.ui.treeVwTestpoints.update(index)
        for k1 in range(len(node.childs)):
            child_node = node.childs[k1]
            index_to_update = model.createIndex(k1, 1, child_node)
            self.ui.treeVwTestpoints.update(index_to_update)
            self.update_child_nodes(index_to_update)

    def item_clicked(self, index):
        node = index.internalPointer()
        self.ui.lblSelectedTestTestpointInfo.setText(node.testpoint_to_text(node.testpoint_data_all()))

        if node.measurements is None:
            txt = ""
        else:
            self.cal_handler.correlate_measurements(self.calibration)
            txt = ""
            for measurement in node.measurements:
                if txt != "":
                    txt += "\n"
                txt += str(measurement)
                info = self.createResultStringFromMeasurement(measurement)
                txt += "\n" + info
            self.update_parent_nodes(index)
        if index.column() == 1:
            node.toggle_execute()
            self.update_parent_nodes(index)
            self.update_child_nodes(index)

        self.ui.lblSelectedTestMeasurementsDone.setText(txt)

    def load_test_sequence_data(self, *args):
        sequence_file = QtWidgets.QFileDialog.getOpenFileName(
            self, caption=self.tr("Select sequence"),
            filter="Sequences (*.py)",
            directory=smt_cal_demo.calibration.calibration_data.__path__[0])[0]

        if sequence_file == "":
            logging.info("No file selected for import ")
            return
        else:
            self.load_test_sequence_data_from_file(sequence_file)

    def load_test_sequence_data_from_file(self, sequence_file):
        self.measurement_ctl.ui_command = c_cmd_do_not_block
        self.measurement_ctl.command_event.set()
        if self.cal_handler.open_file(str(sequence_file)) is False:
            self.measurement_ctl.ui_command = c_cmd_nothing
            self.measurement_ctl.command_event.set()
            return

        root_node = self.cal_handler.rootNode
        if (
                "model" in root_node.testpoint_data and
                "manufacturer" in root_node.testpoint_data):
            self.ui.actionSelect_Calibration.setEnabled(True)
        else:
            self.ui.actionSelect_Calibration.setEnabled(False)

        self.ui.treeVwTestpoints.setModel(Testpoint_ItemModel(self.cal_handler.rootNode))
        self.ui.treeVwTestpoints.setColumnWidth(0, 300)

        self.ui.actionSelect_Calibration.setEnabled(True)
        self.ui.treeVwTestpoints.expandAll()
        self.measurement_ctl.calDataHandler = self.cal_handler

        self.update_setting_dependend_ui()

        self.measurement_ctl.ui_command = c_cmd_nothing
        self.measurement_ctl.command_event.set()

    def start_measurements(self, *args):
        self.localMeasurementStatus = "Request to start"

    def save_and_continue_measurements(self, *args):
        if self.localMeasurementStatus == "Measurement available":
            self.localMeasurementStatus = "Save Measurement"

    def dont_save_and_continue_measurements(self, *args):
        if self.localMeasurementStatus == "Measurement available":
            self.localMeasurementStatus = "Dont Save Measurement"

    def repeat_measurement(self, *args):
        if self.localMeasurementStatus == "Measurement available":
            self.localMeasurementStatus = "Repeat"

    def select_calibration(self, *args):
        if "manufacturer" not in self.cal_handler.rootNode.testpoint_data:
            self.ui.statusbar.showMessage("No manufacturer set")
            return

        if "model" not in self.cal_handler.rootNode.testpoint_data:
            self.ui.statusbar.showMessage("No model set")
            return

        if self.instrument is None:
            self.select_instrument()
            if self.instrument is None:
                self.ui.statusbar.showMessage("Instrument must be selected")
                return

        dialog = select_calibration_dialog_v01.Dialog()
        dialog.instrument = self.instrument
        answer = dialog.exec_()
        if answer == 1:
            self.calibration = dialog.selected_calibration
            self.cal_handler.correlate_measurements(self.calibration)
        elif answer == 2:
            # create calibration
            self.calibration = Calibration()

            self.calibration.start_date = datetime.datetime.now()
            self.calibration.instrument = self.instrument
            self.calibration.result = True

            dialog = QtWidgets.QDialog()
            ui = calibration_information_ui_v01.Ui_Dialog()
            ui.setupUi(dialog)
            dialog.exec_()

            self.calibration.project_id_m = ui.txtProjectId.text()
            self.calibration.operator = ui.cmbOperator.currentText()
            session.add(self.calibration)
            session.commit()
            self.cal_handler.correlate_measurements(self.calibration)

        self.update_setting_dependend_ui()

    def select_instrument(self, *args):
        if "manufacturer" not in self.cal_handler.rootNode.testpoint_data:
            self.ui.statusbar.showMessage("No manufacturer set")
            return

        if "model" not in self.cal_handler.rootNode.testpoint_data:
            self.ui.statusbar.showMessage("No model set")
            return

        dialog = select_instrument_dialog_v01.Dialog()
        dialog.manufacturer = self.cal_handler.rootNode.testpoint_data["manufacturer"]
        dialog.model = self.cal_handler.rootNode.testpoint_data["model"]
        print("excute dialog")
        if dialog.exec_() == 1:
            print("Dialog success")
            self.instrument = dialog.selected_instrument
            self.measurement_ctl.instrument = self.instrument
            self.calibration = None
            print(self.instrument)

        self.update_setting_dependend_ui()

    def update_setting_dependend_ui(self):
        # does instrument fit to testsequence
        if not hasattr(self.cal_handler, "test_ids"):
            ui_state = "no valid test sequence"
        elif not hasattr(self.cal_handler, "rootNode"):
            ui_state = "no valid test sequence"
        elif (
                "manufacturer" not in self.cal_handler.rootNode.testpoint_data or
                "model" not in self.cal_handler.rootNode.testpoint_data):
            ui_state = "no valid test sequence"
        elif self.instrument is None:
            ui_state = "no valid instrument"
        elif (
                self.cal_handler.rootNode.testpoint_data["manufacturer"] != self.instrument.manufacturer or
                str(self.cal_handler.rootNode.testpoint_data["model"]) != self.instrument.model):
            ui_state = "no valid instrument"
        elif self.calibration is None:
            ui_state = "no valid calibration"
        else:
            ui_state = "valid settings"

        if ui_state == "no valid test sequence":
            # no valid test sequence
            self.instrument = None
            self.measurement_ctl.instrument = self.instrument
            self.measurement_ctl.current_test_index = None
            self.calibration = None
            self.measurement_ctl.calibration = self.calibration
            self.ui.actionSelect_Calibration.setEnabled(False)
            self.ui.actionSelect_Instrument.setEnabled(False)
            self.ui.actionStart_Measurements.setEnabled(False)
            self.ui.actionContinue_with_Save.setEnabled(False)
            self.ui.actionContinue_with_Save.setEnabled(False)
            self.ui.actionNext_without_Save.setEnabled(False)
            self.ui.actionRepeat.setEnabled(False)

            self.ui.lblCurrentCalibration.setText("no calibration selected")
            self.ui.lblCurrentInstrument.setText("no instrument selected")
            self.ui.lblCurrTestProcessingInstr.setText("-")
            self.ui.lblCurrTestSpecs.setText("-")
            self.ui.lblCurrTestTestpointInfo.setText("-")
            self.ui.lblLastMeasurmentResult.setText("-")
            self.ui.lblSelectedTestMeasurementsDone.setText("-")
            self.ui.lblSelectedTestTestpointInfo.setText("-")

        elif ui_state == "no valid instrument":
            self.instrument = None
            self.measurement_ctl.instrument = self.instrument
            self.calibration = None
            self.measurement_ctl.calibration = self.calibration
            self.ui.actionSelect_Calibration.setEnabled(True)
            self.ui.actionSelect_Instrument.setEnabled(True)
            self.ui.actionStart_Measurements.setEnabled(False)
            self.ui.actionContinue_with_Save.setEnabled(False)
            self.ui.actionContinue_with_Save.setEnabled(False)
            self.ui.actionNext_without_Save.setEnabled(False)
            self.ui.actionRepeat.setEnabled(False)

            self.ui.lblCurrentCalibration.setText("no calibration selected")
            self.ui.lblCurrentInstrument.setText("no instrument selected")
            self.ui.lblCurrTestProcessingInstr.setText("-")
            self.ui.lblCurrTestSpecs.setText("-")
            self.ui.lblCurrTestTestpointInfo.setText("-")
            self.ui.lblLastMeasurmentResult.setText("-")
            self.ui.lblSelectedTestMeasurementsDone.setText("-")
            self.ui.lblSelectedTestTestpointInfo.setText("-")

        elif ui_state == "no valid calibration":
            self.measurement_ctl.instrument = self.instrument
            self.calibration = None
            self.measurement_ctl.calibration = self.calibration

            self.ui.actionSelect_Calibration.setEnabled(True)
            self.ui.actionSelect_Instrument.setEnabled(True)
            self.ui.actionStart_Measurements.setEnabled(False)
            self.ui.actionContinue_with_Save.setEnabled(False)
            self.ui.actionContinue_with_Save.setEnabled(False)
            self.ui.actionNext_without_Save.setEnabled(False)
            self.ui.actionRepeat.setEnabled(False)

            self.ui.lblCurrentCalibration.setText("no calibration selected")
            self.ui.lblCurrentInstrument.setText(str(self.instrument))
            self.ui.lblCurrTestProcessingInstr.setText("-")
            self.ui.lblCurrTestSpecs.setText("-")
            self.ui.lblCurrTestTestpointInfo.setText("-")
            self.ui.lblLastMeasurmentResult.setText("-")
            self.ui.lblSelectedTestMeasurementsDone.setText("-")
            self.ui.lblSelectedTestTestpointInfo.setText("-")

        elif ui_state == "valid settings":
            self.measurement_ctl.instrument = self.instrument
            self.measurement_ctl.calibration = self.calibration

            self.ui.actionSelect_Calibration.setEnabled(True)
            self.ui.actionSelect_Instrument.setEnabled(True)
            self.ui.actionStart_Measurements.setEnabled(True)

            self.ui.lblCurrentCalibration.setText(str(self.calibration))
            self.ui.lblCurrentInstrument.setText(str(self.instrument))

    def call_synchronize(self, *args):
        proc = ExecuteSynchronize()
        proc.start()
        print("finished")

def main():
    app_reused = True
    app = QtCore.QCoreApplication.instance()
    if app is None:
        print("App will be created")
        app = QtWidgets.QApplication(sys.argv)
        app_reused = False

    window = CalApp()
    window.show()
#    app.aboutToQuit.connect(window.closeEvent)
    if app_reused is False:
        print("Call app.exec()")
        sys.exit(app.exec_())
    print("Fertig")

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)
    main()