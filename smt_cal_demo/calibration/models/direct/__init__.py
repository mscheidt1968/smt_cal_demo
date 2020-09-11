#
import math


class CapDirect(object):
    
    cap = None
    unc_cap = 0
    corr_cap = 0
    unc_corr_cap = 0
    
    dut_cap = None
    dut_std_dev_cap = 0
    dut_corr_cap = 0
    dut_unc_corr_cap = 0
    dut_range = 0

    output_delta_cap = None

    output_exp_unc = None
    
    def calculate(self):
        """ call when all input data are set """
        # make correction to input values
        zw_delta_cap = (self.dut_cap +
                                    self.dut_corr_cap -
                                    self.cap -
                                    self.corr_cap) 
        zw_sqr_unc = ( self.unc_cap**2 +
                                self.unc_corr_cap**2 +
                                self.dut_std_dev_cap**2 +
                                self.dut_unc_corr_cap**2 + 
                                2e-12**2)
        self.output_delta_cap = zw_delta_cap
        self.output_exp_unc = 2*math.sqrt( zw_sqr_unc)                        
        pass



class ResDirect(object):
    
    resistance = None
    unc_resistance = 0
    corr_resistance = 0
    unc_corr_resistance = 0
    
  
    dut_resistance = None
    dut_std_dev_resistance = 0
    dut_corr_resistance = 0
    dut_unc_corr_resistance = 0
    dut_range = 0

    output_delta_voltage = None

    output_exp_unc = None
    
    def calculate(self):
        """ call when all input data are set """
        # make correction to input values
        zw_delta_resistance = (self.dut_resistance +
                                    self.dut_corr_resistance -
                                    self.resistance -
                                    self.corr_resistance) 
        zw_sqr_unc = ( self.unc_resistance**2 +
                                self.unc_corr_resistance**2 +
                                self.dut_std_dev_resistance**2 +
                                self.dut_unc_corr_resistance**2)
        self.output_delta_resistance = zw_delta_resistance
        self.output_exp_unc = 2*math.sqrt( zw_sqr_unc)                        
        pass



class DCVoltDirect(object):
    
    voltage = None
    unc_voltage = 0
    corr_voltage = 0
    unc_corr_voltage = 0
    
    dut_voltage = None
    dut_std_dev_voltage = 0
    dut_corr_voltage = 0
    dut_unc_corr_voltage = 0
    dut_range = 0

    output_delta_voltage = None

    output_exp_unc = None
    
    def calculate(self):
        """ call when all input data are set """
        # make correction to input values
        zw_delta_voltage = (self.dut_voltage +
                                    self.dut_corr_voltage -
                                    self.voltage -
                                    self.corr_voltage) 
        zw_sqr_unc = ( self.unc_voltage**2 +
                                self.unc_corr_voltage**2 +
                                self.dut_std_dev_voltage**2 +
                                self.dut_unc_corr_voltage**2 + 
                                1e-6**2)
        self.output_delta_voltage = zw_delta_voltage
        self.output_exp_unc = 2*math.sqrt( zw_sqr_unc)                        
        pass


class ACVoltDirect(object):
    
    voltage = None
    unc_voltage = 0
    corr_voltage = 0
    unc_corr_voltage = 0
    frequency = 0
    
    dut_voltage = None
    dut_std_dev_voltage = 0
    dut_corr_voltage = 0
    dut_unc_corr_voltage = 0
    dut_range = 0
    dut_impedance = 1e6

    output_delta_voltage = None

    output_exp_unc = None
    
    def calculate(self):
        """ call when all input data are set """
        # calculate voltage drop due to inductivity of wires 2uH
        z_wires = 2 * math.pi * self.frequency * 2e-6
        voltage_drop = z_wires * self.voltage/self.dut_impedance
        
        zw_delta_voltage = (self.dut_voltage +
                                    self.dut_corr_voltage -
                                    self.voltage -
                                    self.corr_voltage)
        zw_sqr_unc = ( self.unc_voltage**2 +
                                self.unc_corr_voltage**2 +
                                self.dut_std_dev_voltage**2 +
                                self.dut_unc_corr_voltage**2 +
                                voltage_drop**2)
        self.output_delta_voltage = zw_delta_voltage
        self.output_exp_unc = 2*math.sqrt( zw_sqr_unc)                        
        pass
    
    
class ACCurDirect(object):
    
    current = None
    unc_current = 0
    corr_current = 0
    unc_corr_current = 0
    frequency = 0
    
    dut_current = None
    dut_std_dev_current = 0
    dut_corr_current = 0
    dut_unc_corr_current = 0
    dut_range = 0

    output_delta_current = None

    output_exp_unc = None
    
    def calculate(self):
        """ call when all input data are set """
        # make correction to input values
        zw_delta_current = (self.dut_current +
                                    self.dut_corr_current -
                                    self.current -
                                    self.corr_current)
        zw_sqr_unc = ( self.unc_current**2 +
                                self.unc_corr_current**2 +
                                self.dut_std_dev_current**2 +
                                self.dut_unc_corr_current**2)
        self.output_delta_current = zw_delta_current
        self.output_exp_unc = 2*math.sqrt( zw_sqr_unc)                        
        pass
    
    
class DCCurDirect(object):
    
    current = None
    unc_current = 0
    corr_current = 0
    unc_corr_current = 0
    
    dut_current = None
    dut_std_dev_current = 0
    dut_corr_current = 0
    dut_unc_corr_current = 0
    dut_range = 0

    output_delta_current = None

    output_exp_unc = None
    
    def calculate(self):
        """ call when all input data are set """
        # make correction to input values
        zw_delta_current = (self.dut_current +
                                    self.dut_corr_current -
                                    self.current -
                                    self.corr_current) 
        zw_sqr_unc = ( self.unc_current**2 +
                                self.unc_corr_current**2 +
                                self.dut_std_dev_current**2 +
                                self.dut_unc_corr_current**2
                                )
        self.output_delta_current = zw_delta_current
        self.output_exp_unc = 2*math.sqrt( zw_sqr_unc)                        
        pass


class CapMeasure(object):
    
    cap = None
    unc_cap = 0
    corr_cap = 0
    unc_corr_cap = 0
    
    dut_cap = None
    dut_std_dev_cap = 0
    dut_corr_cap = 0
    dut_unc_corr_cap = 0
    dut_range = 0

    output_delta_cap = None

    output_exp_unc = None
    
    def calculate(self):
        """ call when all input data are set """
        # make correction to input values
        zw_delta_cap = (self.dut_cap +
                                    self.dut_corr_cap -
                                    self.cap -
                                    self.corr_cap) 
        zw_sqr_unc = ( self.unc_cap**2 +
                                self.unc_corr_cap**2 +
                                self.dut_std_dev_cap**2 +
                                self.dut_unc_corr_cap**2 + 
                                10e-12**2)
        self.output_delta_cap = zw_delta_cap
        self.output_exp_unc = 2*math.sqrt( zw_sqr_unc)                        
        pass


class ResMeasure(object):
    
    resistance = None
    unc_resistance = 0
    corr_resistance = 0
    unc_corr_resistance = 0
    
    dut_resistance = None
    dut_std_dev_resistance = 0
    dut_corr_resistance = 0
    dut_unc_corr_resistance = 0
    dut_range = 0

    output_delta_voltage = None

    output_exp_unc = None
    
    def calculate(self):
        """ call when all input data are set """
        # make correction to input values
        zw_delta_resistance = (self.dut_resistance +
                                    self.dut_corr_resistance -
                                    self.resistance -
                                    self.corr_resistance) 
        zw_sqr_unc = ( self.unc_resistance**2 +
                                self.unc_corr_resistance**2 +
                                self.dut_std_dev_resistance**2 +
                                self.dut_unc_corr_resistance**2 + 
                                1e-6**2)
        self.output_delta_resistance = zw_delta_resistance
        self.output_exp_unc = 2*math.sqrt( zw_sqr_unc)                        
        pass


class DCVoltMeasure(object):
    
    voltage = None
    unc_voltage = 0
    corr_voltage = 0
    unc_corr_voltage = 0
    
    dut_voltage = None
    dut_std_dev_voltage = 0
    dut_corr_voltage = 0
    dut_unc_corr_voltage = 0
    dut_range = 0

    output_delta_voltage = None

    output_exp_unc = None
    
    def calculate(self):
        """ call when all input data are set """
        # make correction to input values
        zw_delta_voltage = (self.dut_voltage +
                                    self.dut_corr_voltage -
                                    self.voltage -
                                    self.corr_voltage) 
        zw_sqr_unc = ( self.unc_voltage**2 +
                                self.unc_corr_voltage**2 +
                                self.dut_std_dev_voltage**2 +
                                self.dut_unc_corr_voltage**2 + 
                                1e-6**2)
        self.output_delta_voltage = zw_delta_voltage
        self.output_exp_unc = 2*math.sqrt( zw_sqr_unc)                        
        pass


class ACVoltMeasure(object):
    
    voltage = None
    unc_voltage = 0
    corr_voltage = 0
    unc_corr_voltage = 0
    frequency = 0
    
    dut_voltage = None
    dut_std_dev_voltage = 0
    dut_corr_voltage = 0
    dut_unc_corr_voltage = 0
    dut_range = 0

    output_delta_voltage = None

    output_exp_unc = None
    
    def calculate(self):
        """ call when all input data are set """
        # make correction to input values
        zw_delta_voltage = (self.dut_voltage +
                                    self.dut_corr_voltage -
                                    self.voltage -
                                    self.corr_voltage)
        zw_sqr_unc = ( self.unc_voltage**2 +
                                self.unc_corr_voltage**2 +
                                self.dut_std_dev_voltage**2 +
                                self.dut_unc_corr_voltage**2)
        self.output_delta_voltage = zw_delta_voltage
        self.output_exp_unc = 2*math.sqrt( zw_sqr_unc)                        
        pass
    
    
class ACCurMeasure(object):
    
    current = None
    unc_current = 0
    corr_current = 0
    unc_corr_current = 0
    frequency = 0
    
    dut_current = None
    dut_std_dev_current = 0
    dut_corr_current = 0
    dut_unc_corr_current = 0
    dut_range = 0

    output_delta_current = None

    output_exp_unc = None
    
    def calculate(self):
        """ call when all input data are set """
        # make correction to input values
        zw_delta_current = (self.dut_current +
                                    self.dut_corr_current -
                                    self.current -
                                    self.corr_current)
        zw_sqr_unc = ( self.unc_current**2 +
                                self.unc_corr_current**2 +
                                self.dut_std_dev_current**2 +
                                self.dut_unc_corr_current**2)
        self.output_delta_current = zw_delta_current
        self.output_exp_unc = 2*math.sqrt( zw_sqr_unc)                        
        pass
    
    
class DCCurMeasure(object):
    
    current = None
    unc_current = 0
    corr_current = 0
    unc_corr_current = 0
    
    dut_current = None
    dut_std_dev_current = 0
    dut_corr_current = 0
    dut_unc_corr_current = 0
    dut_range = 0

    output_delta_current = None

    output_exp_unc = None
    
    def calculate(self):
        """ call when all input data are set """
        # make correction to input values
        zw_delta_current = (self.dut_current +
                                    self.dut_corr_current -
                                    self.current -
                                    self.corr_current) 
        zw_sqr_unc = ( self.unc_current**2 +
                                self.unc_corr_current**2 +
                                self.dut_std_dev_current**2 +
                                self.dut_unc_corr_current**2
                                )
        self.output_delta_current = zw_delta_current
        self.output_exp_unc = 2*math.sqrt( zw_sqr_unc)                        
        pass

