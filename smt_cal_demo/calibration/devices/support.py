# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 12:02:00 2012

@author: Scheidt
"""
import time
import unittest
import serial
import telnetlib
import logging
import datetime
import zmq

context = zmq.Context()

class InstrumentNotFound(Exception):
    pass

class OutOfRange(Exception):
    pass

class MeasuringError(Exception):
    pass

class UnspecifiedMeasurementError(Exception):
    pass

class OutputError(Exception):
    pass

class SettingsError(Exception):
    pass

class TimeOut(object):
    """
    Creates an object which will trigger to true if a certain time has elapsed
    
    """
    
    def __init__(self,timeout):
        self.startTime = datetime.datetime.now()
        self.durationOfTimeout = timeout

    def set_timed_out(self):
        self.durationOfTimeout = 0
    
    def is_timed_out(self):
        duration=datetime.datetime.now() - self.startTime
        if duration.total_seconds() > self.durationOfTimeout:
            return True
        else:
            return False


def find_range(value, ranges):
    return find_rangeAC(value, 0, ranges)

def find_rangeAC(value, frequency, ranges):

    range_key = None
    range_max = None    
    
    for key,item in list(ranges.items()):
        test_range_fits = True
        test_range_max = None
        test_range_min = None
        
        if not key == "_format":
            for key2,item2 in list(item.items()):
                if key2 == "min" :
                    if value < item2 :
                        test_range_fits = False
                    else:
                        test_range_min = item2
            
                elif key2 == ">min" :
                    if value <= item2 :
                        test_range_fits = False
                    else:
                        test_range_min = item2
    
                elif key2 == "max" :
                    if value > item2 :
                        test_range_fits = False
                    else:
                        test_range_max = item2
            
                elif key2 == "<max" :
                    if value >= item2 :
                        test_range_fits = False
                    else:
                        test_range_max = item2
    
                elif key2 == "fmin" :
                    if frequency < item2 :
                        test_range_fits = False
            
                elif key2 == ">fmin" :
                    if frequency <= item2 :
                        test_range_fits = False
    
                elif key2 == "fmax" :
                    if frequency > item2 :
                        test_range_fits = False
            
                elif key2 == "<fmax" :
                    if frequency >= item2 :
                        test_range_fits = False
                        
            if test_range_fits == True:
                if range_max is None:
                    range_key =key
                    range_max = test_range_max
                elif test_range_max < range_max:
                    range_key = key 
                    range_max = test_range_max
                    

    if range_key is None:
        raise OutOfRange()
            
    return range_key        




class Testfind_range(unittest.TestCase):

    def setUp(self):
        self.ranges={
                        "0.033" : {"min" : 0.001, "<max" : 0.033 , "fmin" : 10 , "fmax" : 500e3 },
                        "0.33" : {"min" : 0.033, "<max" : 0.33 , "fmin" : 10 , "fmax" : 500e3 },
                        "3.3" : {"min" : 0.33, "<max" : 3.3 , "fmin" : 10 , "fmax" : 500e3} , 
                        "33" : {"min" : 3.3, "<max" : 33 , "fmin" : 10 , "fmax" : 20e3 }, 
                        "330" : {"min" : 30, "<max" : 330 , "fmin" : 10 , "fmax" : 20e3 }, 
                        "1000" : {"min" : 330, "<max" : 1020 , "fmin" : 10 , "fmax" : 10e3 } 
                    }

    def test_findRange(self):
        res=find_rangeAC(0.33, 10e3, self.ranges)                
        self.assertEqual(res, "3.3")
        res=find_rangeAC(3, 10e3, self.ranges)                
        self.assertEqual(res, "3.3")
        res=find_rangeAC(3.3, 10e3, self.ranges)                
        self.assertEqual(res, "33")

        # should raise an exception for an immutable sequence
        self.assertRaises(OutOfRange, find_rangeAC, 30, 100e3, self.ranges)

def uncertainty_from_AC_spec(value, frequency, spec, range_val = None):
    """ spec contains multiple specs which a selected by frequency """
    spec_index = 0
    if "finterval" in spec:
        n1 = len(list([x for x in spec["finterval"] if frequency >= x]))
        n2 = len(list([x for x in spec["finterval"] if frequency <= x]))
        if n1 == 0 or n2 == 0:
            raise OutOfRange("Frequency " + frequency.__str__() + " value out of specification range")    
        if spec["finterval"].__len__() == n1:
            spec_index = n1-2
        else:
            spec_index = n1-1
        
    return uncertainty_from_spec(value, spec["specs"][spec_index], range_val)
    

def uncertainty_from_spec(value, spec, range_val):
    """ spec is a dict() with keys describing offset and proportional part of uncertatinty """
    unc_summed=0    
    avalue=abs(value)
    for key,item in list(spec.items()):
        if key == "p":
            unc_summed+=avalue*item
        if key == "p%":
            unc_summed+=avalue*item*1e-2
        if key == "ppm":
            unc_summed+=avalue*item*1e-6
        if key == "fixn":
            unc_summed+=item*1e-9            
        if key == "fixu":
            unc_summed+=item*1e-6            
        if key == "fixm":
            unc_summed+=item*1e-3            
        if key == "fix":
            unc_summed+=item
        if key == "fix%Range":
            unc_summed+=item*1e-2*range_val            
        if key == "fixppmRange":
            unc_summed+=item*1e-6*range_val            
            
    return unc_summed   
        
    
class Testfind_uncertainty_from_AC_spec(unittest.TestCase):

    def setUp(self):
        self.test_spec={
                        "finterval" : [10, 45, 10e3, 20e3, 
                                    50e3, 100e3, 500e3],
                        "specs": 
                            [
                                { "p%" : 0.35, "fixu" : 25},
                                { "p%" : 0.15, "fixu" : 24},
                                { "p%" : 0.2 , "fixu" : 23},
                                { "p%" : 0.25, "fixu" : 22},
                                { "p%" : 0.35, "fixu" : 21},
                                { "p%" : 1   , "fix%Range" : 0.1},
                            ]
                        }


    def test_uncertainty_from_AC_spec(self):
        res=uncertainty_from_AC_spec(0, 10, self.test_spec)                
        self.assertAlmostEqual(res, 25e-6 , places=6)

        res=uncertainty_from_AC_spec(0, 45, self.test_spec)                
        self.assertAlmostEqual(res, 24e-6 , places=6)

        res=uncertainty_from_AC_spec(0, 500e3, self.test_spec,1)                
        self.assertAlmostEqual(res, 0.1/100.*1 , places=6)

        res=uncertainty_from_AC_spec(0.1, 15e3 , self.test_spec)                
        self.assertAlmostEqual(res, 23e-6 + 0.2/100.*0.1 , places=6)

        res=uncertainty_from_AC_spec(-0.1, 15e3 , self.test_spec)                
        self.assertAlmostEqual(res, 23e-6 + 0.2/100.*0.1 , places=6)

        # should raise an exception for an immutable sequence
        self.assertRaises(OutOfRange, uncertainty_from_AC_spec, 10, 9, self.test_spec)
        self.assertRaises(OutOfRange, uncertainty_from_AC_spec, 10, 501e3, self.test_spec)
    

def Rs232PortMap(minport=0, count=32):
    """ checks count serial ports from minport if attached and trys to
    read identity of device. 9600 baud odd parity 7 bits """
    
    portmap = dict() 
    attached_ports = list()       
    for k1 in range(minport, count):
        try: 
            ser = serial.Serial(k1, 9600)
            attached_ports.append(k1)
            ser.timeout = 1
            ser.parity = serial.PARITY_ODD
            ser.bytesize = serial.SEVENBITS
            ser.writeTimeout =1
            ser.write("\n")
            discard_answer = ser.readline()
            print(discard_answer)
            ser.write("*IDN?\n")
            answer = ser.readline()
            if answer != "":
                # system could be identified
                idn = answer.rstrip().split(",")    
                portmap[k1] = {"Manufacturer":idn[0] ,
                                "Model" : idn[1],
                                "SN" : idn[2],
                                "Firmware" : idn[3]
                                }

            ser.close()
        except serial.SerialException:
            pass
    return [portmap,attached_ports]
    
    
class Connection(object):
    
    """Object enabling communication

    """
    simulation = False
    
    def __init__(self,simulation=False):
        self.simulation=simulation
        
    def open(self,connectionInfo):
        pass
    
    def close(self):
        pass

    def writeln(self,data):
        if self.simulation:
            print(("Sending data:"+data+" new line"))
        pass
    
    def write(self,data):
        if self.simulation:
            print(("Sending data:"+data))
        pass
    
    def readln(self, writelnFirst="", simresult=""):
        """reads data until a terminator is recognized
        
        """
        pass

class SerialPortConnection(Connection):
    """Gives Access to a device conneted by RS232
    
    """
    
    port = "COM6"
    ser = None
    baudrate=9600
    
    def __init__(self,simulation=False):
        super(SerialPortConnection,self).__init__(simulation)
        
    def open(self):
        if self.simulation:
            logging.info("opening serial connection to:"+self.port)
        else:
            print("jetzt")
            self.ser = serial.Serial(self.port,self.baudrate,timeout=1)
            self.ser.parity = serial.PARITY_ODD
            self.ser.bytesize = serial.SEVENBITS

    def readln(self, writelnFirst="", simresult=""):
        if writelnFirst != "":
            self.writeln(writelnFirst)
        if self.simulation:
            return simresult
        else:
            return self.ser.readline().rstrip()
        
    def write(self,data):
        if self.simulation:
            logging.info("Sending data:"+data)
        else:
            self.ser.write(data)

    def writeln(self,data):
        if self.simulation:
            logging.info("Sending data:"+data+" with line end")
        else:
            self.ser.write(data+"\n")

    def close(self):
        self.ser.close()
        self.ser=None        


class SerialDeviceConnection(Connection):
    """Gives Access to a device managed by serial_devices_manager
    
    """
    
    def __init__(self,simulation=False):
        self.target = ""
        self.socket = context.socket(zmq.REQ)
        self.socket.connect("tcp://127.0.0.1:5001")
        super(SerialDeviceConnection,self).__init__(simulation)

    def readln(self, writelnFirst=""):
        self.socket.send_json(dict(target=self.target, cmd="readln", data=writelnFirst))
        answer = self.socket.recv_json()
        return answer["data"]
        
    def write(self,data):
        self.socket.send_json(dict(target=self.target, cmd="write", data=data))
        answer = self.socket.recv_json()
        return

    def writeln(self,data):
        self.socket.send_json(dict(target=self.target, cmd="writeln", data=data))
        answer = self.socket.recv_json()
        return 


class GPIBConnection(Connection):
    """Gives Access to a GPIB device conneted by Prologix over serial device manager
    """
    
    def __init__(self, simulation=False):
        self.target = ""
        self.socket = context.socket(zmq.REQ)
        self.socket.connect("tcp://127.0.0.1:5001")
        super(GPIBConnection,self).__init__(simulation)

    def _readbinary(self, byte_count=1):
        self.socket.send_json(dict(target=self.target, cmd="readbinary", byte_count=byte_count))
        answer = self.socket.recv_json()
        return answer["data"]

    def _readln(self, writelnFirst=""):
        self.socket.send_json(dict(target=self.target, cmd="readln", data=writelnFirst))
        answer = self.socket.recv_json()
        return answer["data"]
        
    def _write(self,data):
        self.socket.send_json(dict(target=self.target, cmd="write", data=data))
        answer = self.socket.recv_json()
        return

    def _writeln(self,data):
        self.socket.send_json(dict(target=self.target, cmd="writeln", data=data))
        answer = self.socket.recv_json()
        return 
        
    def open(self):
        logging.info("Opening {:s}".format(self.target))
        self._write("++read_tmo_ms 100\n")
        self._write("++mode 1\n")
        self._write("++auto 0\n")
        self._write("++eoi 0\n")

    def set_auto(self,on = True):
        if on:
            self._write("++auto 1\n")
        else:
            self._write("++auto 0\n")
            
    def flush_input(self):
        finished = False
        while not finished:
            answer = self._readbinary(byte_count=128)
            if answer == "":
                finished = True

    def set_device_address(self, address = 22, sub_address = None):
        """Set GPIB address of device to which we like to talk to"""
        self._write(("++addr " + str(address)))
        if not sub_address is None:
            self._write((" " + str(sub_address)))
        self._write("\n")
        
    def local(self):
        """Enables front panel operation of device"""
        self._write("++loc\n")
        
    def escape_special_characters(self, data):
        """Precedes special characters with ESC ad needed by Prologix IF"""
        # tested on command line
        zw = data
        zw = zw.replace("\x1B","\x1B\x1B")
        zw = zw.replace("+","\x1B+")
        zw = zw.replace("\n","\x1B\n")
        zw = zw.replace("\r","\x1B\r")
        return zw
    
    def send_clr(self):        
        self._write("++clr\n")

    def write(self,data):
        self._write(self.escape_special_characters(data))

    def writeln(self,data):
        self._write(self.escape_special_characters(data)+"\n")

    def readln(self, writelnFirst="", simresult="", time_out=20):
        self._write("++auto 0\n")
        if writelnFirst != "":
            self.writeln(writelnFirst)
        
        self._write("++read_tmo_ms 100\n")
        self._write("++read 10\n")
        fertig = False
        answer = ""
        t_start = datetime.datetime.now()
        while not fertig:
            partial = self._readbinary(1)
            answer += partial
            if len(answer) > 0:
                if answer[-1] == "\n":
                    fertig = True
            elif answer != "":
                pass
            else:
                # reenable reading from GPIB
                self._write("++read 10\n")
                
            dt_now = datetime.datetime.now() - t_start
            if dt_now.total_seconds() > time_out:
                raise Exception("Timeout when reading from GPIB:{:.0f}, answer up to now: {:s}".
                                    format(time_out, answer))
            
        return answer.rstrip()

        

    def read_bin_data(self, count=100):
        self._write("++read_tmo_ms 100\n")
        self._write("++auto 1\n")
        return self._readbinary(byte_count=count)

    def read_further_data(self, count=100):
        return self._readbinary(byte_count=count)

    def close(self):
        pass


class GPIBConnection_direct(Connection):
    """Gives Access to a GPIB device conneted by Prologix
    """
       
    def __init__(self):
        self.port = 19
        self.ser = None
        self.baudrate=921600
        super(GPIBConnection,self).__init__()
        
    def open(self):
        logging.info("Com port " + str(self.port+1) + " used to initialize Prologix GPIB IF")
        self.ser = serial.Serial(self.port,self.baudrate,timeout=0.1) 
        self.ser.write("++read_tmo_ms 100\n".encode("latin_1"))
        self.ser.write("++mode 1\n".encode("latin_1"))
        self.ser.write("++auto 0\n".encode("latin_1"))
        self.ser.write("++eoi 0\n".encode("latin_1"))

    def set_auto(self,on = True):
        if on:
            self.ser.write("++auto 1\n".encode("latin_1"))
        else:
            self.ser.write("++auto 0\n".encode("latin_1"))
            
    def flush_input(self):
        self.ser.flushInput()

    def set_device_address(self, address = 22, sub_address = None):
        """Set GPIB address of device to which we like to talk to"""
        self.ser.write(("++addr " + str(address)).encode("latin_1"))
        if not sub_address is None:
            self.ser.write((" " + str(sub_address)).encode("latin_1"))
        self.ser.write("\n".encode("latin_1"))
        
    def local(self):
        """Enables front panel operation of device"""
        self.ser.write("++loc\n".encode("latin_1"))
        
    def escape_special_characters(self, data):
        """Precedes special characters with ESC ad needed by Prologix IF"""
        # tested on command line
        zw = data
        zw = zw.replace("\x1B","\x1B\x1B")
        zw = zw.replace("+","\x1B+")
        zw = zw.replace("\n","\x1B\n")
        zw = zw.replace("\r","\x1B\r")
        return zw
    
    def send_clr(self):        
        self.ser.write("++clr\n".encode("latin_1"))

    def write(self,data):
        self.ser.write(self.escape_special_characters(data).encode("latin_1"))

    def writeln(self,data):
        self.ser.write((self.escape_special_characters(data)+"\n").encode("latin_1"))

    def readln(self, writelnFirst="", simresult="", time_out=20):
        self.ser.write("++auto 0\n".encode("latin_1"))
        if writelnFirst != "":
            self.writeln(writelnFirst)
        
        self.ser.write("++read_tmo_ms 100\n".encode("latin_1"))
        self.ser.write("++read 10\n".encode("latin_1"))
        fertig = False
        answer = b""
        t_start = datetime.datetime.now()
        while not fertig:
            partial = self.ser.read()
            answer += partial
            if len(answer) > 0:
                if answer[-1] == 10:
                    fertig = True
            else:
                # reenable reading from GPIB
                self.ser.write("++read 10\n".encode("latin_1"))
            dt_now = datetime.datetime.now() - t_start
            if dt_now.total_seconds() > time_out:
                raise Exception("Timeout when reading from GPIB:{:.0f}".
                                    format(time_out))
            
        return answer.rstrip().decode("latin_1")

        

    def read_bin_data(self, count=100):
        self.ser.write("++read_tmo_ms 100\n".encode("latin_1"))
        self.ser.write("++auto 1\n".encode("latin_1"))
        return self.ser.read(size =count).decode("latin_1")

    def read_further_data(self, count=100):
        return self.ser.read(size =count).decode("latin_1")

    def close(self):
        self.ser.close()


class TestGPIBConnection_class(unittest.TestCase):
    gpib = None

    def setUp(self):
        self.gpib = GPIBConnection()
        self.gpib.port = 19

    def test_read_id_of_HP3458(self):
        """HPIB must be attached with address 22 by Prologix on com port 20"""
        self.gpib.open()
        self.gpib.set_device_address(22)
        res=self.gpib.readln("id?")
        self.assertEqual(res,"HP3458A","ID was not read. received:" + res)

        
        res = self.gpib.escape_special_characters("\x1B+\r\n")
        self.assertEqual(res ,
                         "\x1b\x1b\x1b+\x1b\r\x1b\n")

    
    def tearDown(self):
        self.gpib.close()
    
class TelnetConnection(Connection):
    """Gives Access to a device conneted to Lan by telnet
    
    """
    
    ip = "192.168.2.30"
    port = "3490"
    tel = None
    
    def __init__(self,sim=False):
        super(TelnetConnection,self).__init__(sim)
        
    def open(self):
        if self.simulation:
            logging.info("opening telnet connection to:"+self.ip+":"+self.port)
        else:
            print("jetzt")
            self.tel = telnetlib.Telnet(self.ip,self.port)

    def readln(self, writelnFirst="", simresult=""):
        if writelnFirst != "":
            self.writeln(writelnFirst)
        if self.simulation:
            return simresult
        else:
            return self.tel.read_until("\n",1).rstrip()
        
    def write(self,data):
        if self.simulation:
            logging.info("Sending data:"+data)
        else:
            self.tel.write(data)

    def writeln(self,data):
        if self.simulation:
            logging.info("Sending data:"+data+" with line end")
        else:
            self.tel.write(data+"\n")

    def close(self):
        self.tel.close()
        self.tel=None        


if __name__ == '__main__':
#    unittest.main(exit=False)
#    raise Exception("Test ended")
    import smt_cal_demo.calibration.tokens.devices as c_dev
    con = GPIBConnection()
    con.target = c_dev.agilent_3458A_01
    con.open()
    con.set_device_address(22)
    con.set_auto(True)
    print((con.readln("CALL ID")))
    con.writeln("NRDGS 10")
    t0 = time.time()
    for k1 in range(2):
        con.writeln("TRIG SGL")
        print((time.time()-t0))
    
    pass