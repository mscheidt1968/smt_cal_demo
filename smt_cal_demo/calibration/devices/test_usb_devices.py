# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 11:34:52 2015

@author: Scheidt
"""

import win32com.client
import winreg

print("List of USB devices")
wmi = win32com.client.GetObject ("winmgmts:")
for usb in wmi.InstancesOf ("Win32_USBHub"):
    print(("{{""usb_name"":{:s}, ""PNPDeviceID"":{:s}}}".format(usb.Name,usb.PNPDeviceID)))
    print(usb.Port)

key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r"SYSTEM\CurrentControlSet\Enum\FTDIBUS")
for index in range(winreg.QueryInfoKey(key)[0]):
    identification = winreg.EnumKey(key,index)
    key2 = winreg.OpenKey(key, identification + "\\0000\\Device Parameters")
    value = winreg.QueryValueEx(key2,"PortName")
    print((identification,value))    
    key2.Close()
    
key.Close()