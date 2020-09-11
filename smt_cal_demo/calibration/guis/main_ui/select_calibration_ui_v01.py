# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'select_calibration_v01.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.btnBox = QtWidgets.QDialogButtonBox(Dialog)
        self.btnBox.setGeometry(QtCore.QRect(10, 250, 381, 32))
        self.btnBox.setOrientation(QtCore.Qt.Horizontal)
        self.btnBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.btnBox.setObjectName("btnBox")
        self.listOfCalibrations = QtWidgets.QListWidget(Dialog)
        self.listOfCalibrations.setGeometry(QtCore.QRect(10, 10, 381, 231))
        self.listOfCalibrations.setObjectName("listOfCalibrations")

        self.retranslateUi(Dialog)
        self.btnBox.accepted.connect(Dialog.accept)
        self.btnBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Select Calibration"))




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
