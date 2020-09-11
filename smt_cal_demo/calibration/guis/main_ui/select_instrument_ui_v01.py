# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'select_instrument_v01.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(799, 419)
        self.btnBox = QtWidgets.QDialogButtonBox(Dialog)
        self.btnBox.setGeometry(QtCore.QRect(20, 370, 771, 32))
        self.btnBox.setOrientation(QtCore.Qt.Horizontal)
        self.btnBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.btnBox.setObjectName("btnBox")
        self.listInstruments = QtWidgets.QListWidget(Dialog)
        self.listInstruments.setGeometry(QtCore.QRect(10, 10, 781, 311))
        self.listInstruments.setObjectName("listInstruments")
        self.cmbFilterCustomer = QtWidgets.QComboBox(Dialog)
        self.cmbFilterCustomer.setGeometry(QtCore.QRect(10, 340, 781, 22))
        self.cmbFilterCustomer.setObjectName("cmbFilterCustomer")

        self.retranslateUi(Dialog)
        self.btnBox.rejected.connect(Dialog.reject)
        self.btnBox.accepted.connect(Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
