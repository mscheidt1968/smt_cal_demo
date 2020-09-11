# -*- coding: utf-8 -*-
"""
Created on Thu May 10 14:11:36 2018

@author: SCHEIDT-MT-10
"""

from pathlib import Path
import PyQt5.uic as uic
    
script_path = Path(__file__).parent
target = open(script_path / "calibration_information_ui_v01.py","w")
uic.compileUi(script_path / "calibration_information_v01.ui", target, execute=True)
target.close()


target = open(script_path / "main_calibration_ui_v01.py","w")
uic.compileUi(script_path / "main_calibration_v01.ui", target, execute=True)
target.close()

target = open(script_path / "select_calibration_ui_v01.py","w")
uic.compileUi(script_path / "select_calibration_v01.ui", target, execute=True)
target.close()

target = open(script_path / "select_instrument_ui_v01.py","w")
uic.compileUi(script_path / "select_instrument_v01.ui", target, execute=True)
target.close()
