# -*- coding: utf-8 -*-
"""
Created on Thu Jan 02 10:12:42 2014

@author: Scheidt
"""

import numpy as np

import sys

from PyQt5.QtWidgets import QDialog,QPushButton,QApplication,QDialogButtonBox
from smt_cal_demo.calibration.guis.main_ui.select_instrument_ui_v01 import Ui_Dialog

from smt_cal_demo.calibration.database.support import session,Calibration,Instrument,Measurement,Customer

class Dialog(QDialog):

    @property
    def manufacturer(self):
        return self._manufacturer
    
    @manufacturer.setter
    def manufacturer(self, value):
        self._manufacturer = value
        self.data_changed = True
        return

    @property
    def model(self):
        return self._model
    
    @model.setter
    def model(self, value):
        self._model = value
        self.data_changed = True
        return
    
    def __init__(self):
        QDialog.__init__(self)

        # Set up the user interface from Designer.
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.btn_new = QPushButton("New")
        self.ui.btnBox.addButton(self.btn_new, QDialogButtonBox.ActionRole)
        
        self.btn_new.clicked.connect(self.new_instrument)
        self.ui.listInstruments.currentItemChanged.connect(self.current_index_changed)
        self.ui.listInstruments.doubleClicked.connect(self.selected)
        
        self.ui.cmbFilterCustomer.currentIndexChanged.connect(self.filter_changed)
        self._manufacturer = "Fluke"
        self._model = "175"
        
        self.data_changed = True

    def selected(self, *args):
        self.done(1)
    
    def new_instrument(self, *args):
        self.done(2)

    def current_index_changed(self, *args):
        self.selected_instrument = self.tree_instrument_index[self.ui.listInstruments.currentRow()]
        
        
    def showEvent(self,event):
        if self.data_changed:
            self.data_changed = False
            self.updata_data()
            
        super(Dialog,self).showEvent(event)  
        
        
    def updata_data(self):
        self.instruments_list=session.query(Instrument).filter(Instrument.manufacturer.like(self.manufacturer),
                                                    Instrument.model.like(self._model)).all()

        if len(self.instruments_list) == 0:
            dummy_instrument = Instrument()
            dummy_instrument.manufacturer = self.manufacturer
            dummy_instrument.model = self.model
            dummy_instrument.customer_id = None
            dummy_instrument.serial_number = "dummy"
            dummy_instrument.marked_id = "dummy"
            self.instruments_list.append(dummy_instrument)

        list_of_customers = ["no filter"]
        self.ui.cmbFilterCustomer.clear()

        for k1 in range(len(self.instruments_list)):
            item = self.instruments_list[k1]
            if item.customer is None:
                customer = str("unknown owner")
            else:
                customer = item.customer.name
            
            if not(customer in list_of_customers):
                list_of_customers.append(customer)
                
                
        for customer in list_of_customers:
            self.ui.cmbFilterCustomer.addItem(customer)

        self.update_treeView_data()
        

    def filter_changed(self, zw):
        self.update_treeView_data()        
        
    def update_treeView_data(self):    
        self.ui.listInstruments.clear()
        self.tree_instrument_index = list()                     
        for k1 in range(len(self.instruments_list)):
            item = self.instruments_list[k1]
            if item.customer is None:
                customer = str("unknown owner")
            else:
                customer = item.customer.name

            if (self.ui.cmbFilterCustomer.currentText() == "no filter" or
                self.ui.cmbFilterCustomer.currentText() == customer):
                textual_rep = "SN: {:20s} Marking: {:20s} Customer: {:20s}".format(item.serial_number, item.marked_id, customer)
                self.ui.listInstruments.addItem(textual_rep)
                self.tree_instrument_index.append(item)
        
        self.ui.listInstruments.setCurrentRow(0)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog=Dialog()

    print(dialog.exec_())
    print(dialog.selected_instrument)
    
    dialog.model = "45"

    print(dialog.exec_())
    print(dialog.selected_instrument)
    