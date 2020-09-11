# -*- coding: utf-8 -*-
"""
Created on Thu Jan 02 13:08:17 2014

@author: Scheidt
"""

import sys

from PyQt5.QtWidgets import QDialog,QPushButton,QApplication,QDialogButtonBox
from smt_cal_demo.calibration.guis.main_ui.select_calibration_ui_v01 import Ui_Dialog

from smt_cal_demo.calibration.database.support import session,Calibration,Instrument,Measurement,Customer

class Dialog(QDialog):

    @property
    def instrument(self):
        return self._instrument
    
    @instrument.setter
    def instrument(self, value):
        self._instrument = value
        self.data_changed = True
        return

    
    def __init__(self):
        QDialog.__init__(self)

        # Set up the user interface from Designer.
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.btn_new = QPushButton("New")
        self.ui.btnBox.addButton(self.btn_new, QDialogButtonBox.ActionRole)
        
        self.btn_new.clicked.connect(self.new_calibration)
        self.ui.listOfCalibrations.currentItemChanged.connect(self.current_index_changed)
        self.ui.listOfCalibrations.doubleClicked.connect(self.selected)
        
        #self._instrument = session.query(Instrument).all()[3]
        
        self.data_changed = True

    def selected(self, *args):
        self.done(1)
    
    def new_calibration(self, *args):
        self.done(2)

    def current_index_changed(self, *args):
        self.selected_calibration = self.calibrations_index[self.ui.listOfCalibrations.currentRow()]
        
        
    def showEvent(self,event):
        if self.data_changed:
            self.data_changed = False
            self.updata_data()
            
        super(Dialog,self).showEvent(event)  
        
        
    def updata_data(self):

        self.ui.listOfCalibrations.clear()
        self.calibrations_index = list()                     
        for k1 in range(len(self._instrument.calibration)):
            item = self._instrument.calibration[len(self._instrument.calibration)-k1-1]
#            textual_rep = "SN: {:20s} Marking: {:20s} Customer: {:20s}".format(item.serial_number, item.marked_id, customer)
            textual_rep = str(item)           
            self.ui.listOfCalibrations.addItem(textual_rep)
            self.calibrations_index.append(item)
        
        if len(self._instrument.calibration) > 0:
            self.ui.listOfCalibrations.setCurrentRow(0)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog=Dialog()

    print(dialog.exec_())
    
    