#!/usr/bin/python
#### pep8_ignore: --ignore=C0103, W0311, C0301, W0401, N806
"""Turbidostat GUI."""

import wx
import _thread
import serial
import serial.tools.list_ports
import sys
from time import sleep
import re
import os
from glob import glob
# import configparser
import datetime
import string
# from pylab import *
from pylab import array, figure, imag, isnan, log, log10, matrix, inv, nan, r_, sqrt, plot, subplot, xlabel, ylabel, xlim, ylim, zeros, clip
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
# from scipy.stats import linregress

import wxturbidostat


home_folder = os.path.expanduser("~")
logs_folder = home_folder + '/Turbidostat/logs/'
data_folder = home_folder + '/Turbidostat/data/'
if not os.path.exists(logs_folder):
    os.makedirs(logs_folder)
if not os.path.exists(data_folder):
    os.makedirs(data_folder)
sys.stderr = open(logs_folder + 'stderr.log', 'w')
debug_log = open(logs_folder + 'debug.log', 'w+')

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def map_lin_log(x, maxin=255, maxout=255):
    x = clip(x, 0, maxin)
    return maxout * (log(1 + x) / log(1 + maxin))


def map_lin_log_inv(x, maxin=255, maxout=255):
    x = clip(x, 0, maxin)
    return (1 + maxout)**(x / maxin) - 1


def jaccsd(fun, x_in):
    """Jacobian through complex step differentiation."""
    x_out = fun(x_in)
    n = x_in.size
    m = x_out.size
    A = matrix(zeros([m, n]))
    eps = ((1 + 2e-16) - 1)
    h = n * eps
    for k in range(n):
        x1 = matrix(x_in, dtype=complex)
        x1[k, 0] = x1[k, 0] + h * 1j
        A[:, k] = imag(fun(x1)) / h
    return (x_out, A)


def ekf(fstate, x, P, hmeas, z, Q, R, I0=None):
    """Calculate extended Kalman Filter Step."""
    # (x1,A) = jaccsd(fstate,x);    #nonlinear update and linearization at current state
    x1 = fstate(x)
    A = matrix(r_[[[float(x[1]), float(x[0])], [0.0, 1.0]]])

    A = matrix(A)
    P = matrix(P)

    P = A * P * A.T + Q              # partial update
    # z1, H = jaccsd(hmeas, x1)    # nonlinear measurement and linearization
    z1 = hmeas(x1)
    H = matrix(r_[-(I0 * log(10)) / 10**float(x1[0]), 0])

    P12 = P * H.T                  # cross covariance

    K = P12 * inv(H * P12 + R)         # Kalman filter gain
    x = x1 + K * (z - z1)              # state estimate
    P = P - K * (P12.T)              # state covariance matrix

    return x, P, K


class TurbidostatGUI(wxturbidostat.TsFrame):
    def __init__(self, parent=None):
        # self.m_notebook.InvalidateBestSize()

        wxturbidostat.TsFrame.__init__(self, parent)

        # turbidostat device settings
        self.device_name = None
        self.device_id = None
        self.target_od = None
        self.targetI = None
        self.I0 = None
        self.stirrerTargetSpeed = None
        self.pumpDuration = None
        self.pumpInterval = None
        self.pumpMode = None
        self.pumpPower = None
        self.airpumpPower = None
        self.laserPower = None
        self.firmware_version = None

        self.gui_version = 0.404
        self.SetTitle('Turbidostat (gui: v' + str(self.gui_version) + ')')
        self.Show(True)


        self.threads = 0
        self.thread_lock = _thread.allocate_lock()
        self.connected = False
        self.connecting = False
        self.ser = None
        self.done = False

        self.m_widgetGroup = (
            self.m_txtDeviceName, self.m_tcDeviceName, self.m_btnReset,
            self.m_txtODText, self.m_txtOD, self.m_btnSetI0,
            self.m_txtOD1cmText, self.m_txtOD1cm,
            self.m_txtTargetODText, self.m_tcTargetOD, self.m_btnSetTargetOD,
            self.m_rbPumpMode, self.m_txtManualPump, self.m_tbManualPump,
            self.m_txtPumpInterval, self.m_tcPumpInterval, self.m_txtPumpIntervalUnit, self.m_btnSetPumpInterval,
            self.m_txtPumpDuration, self.m_tcPumpDuration, self.m_txtPumpDurationUnit, self.m_btnSetPumpDuration,
            self.m_txtPumpPower, self.m_sldPumpPower, self.m_txtPumpPowerPercentage, self.m_btnSetPumpPower,
            self.m_txtAirpumpPower, self.m_sldAirpumpPower, self.m_txtAirpumpPowerPercentage, self.m_btnSetAirpumpPower,
            self.m_txtStirrerSpeedText, self.m_txtStirrerSpeed, self.m_txtStirrerSpeedUnit,
            self.m_txtStirrerTargetSpeed, self.m_tcStirrerTargetSpeed, self.m_txtStirrerTargetSpeedUnit, self.m_btnSetStirrerTargetSpeed)
        self.m_widgetGroupAutomaticPump = (self.m_txtPumpInterval, self.m_tcPumpInterval, self.m_txtPumpIntervalUnit, self.m_btnSetPumpInterval,
                                           self.m_txtPumpDuration, self.m_tcPumpDuration, self.m_txtPumpDurationUnit, self.m_btnSetPumpDuration)
        self.m_widgetGroupManualPump = (self.m_txtManualPump, self.m_tbManualPump)

        for widget in self.m_widgetGroup:
            widget.Disable()

        self.data_source = None
        self.findSerialPorts()

        # import ipdb; ipdb.set_trace()

        # # check for product string
        # import usb
        # busses = usb.busses()
        # bus = busses.next()
        # for k in range(4): print(usb.util.get_string(bus.devices[1].dev, k, 0))

        # Set Icons
        icons = wx.IconBundle()
        favicon = wx.Icon('./res/turbidostat.ico', wx.BITMAP_TYPE_ICO, 16, 16)
        icons.AddIcon(favicon)
        favicon = wx.Icon('./res/turbidostat.ico', wx.BITMAP_TYPE_ICO, 32, 32)
        icons.AddIcon(favicon)
        self.SetIcons(icons)

        # load configuration from config file
        # configParser = configparser.RawConfigParser()
        # configFilePath = home_folder + '/Turbidostat/turbidostat.cfg'
        # configParser.read(configFilePath)
        # self.OD1cm_factor = configParser.getfloat('MEASUREMENT', 'OD_1cm_factor')
        # # configParser.set('MEASUREMENT', 'OD_1cm_factor', self.OD1cm_factor*2) # save some configuration
        # with open(configFilePath, 'wb') as configfile:
        #     configParser.write(configfile)
        self.logfile = None
        self.logfile_csv = None

        self.starttime = 0.0
        self.I0 = nan
        self.I = nan
        self.stirrer_speed = nan
        self.pump = False
        self.dummy_mode = False


        # ---- Kalman ----
        # Zustandsmodell exponentielles Wachstum
        self.f = lambda x: matrix([x[0, 0] * x[1, 0], x[1, 0]]).T

        # Measurement
        self.h = lambda x: matrix(self.I0 / (10**x[0, 0]))

        self.OnKalmanReset(None)

        # PLOT
        fig = figure()
        # fig.patch.set_facecolor((214/255, 214/255, 214/255))
        fig.patch.set_facecolor(array(self.m_pnlGraphs.GetBackgroundColour()[0:3]) / 255.0)

        self.canvas = FigureCanvas(self.m_pnlGraphs, -1, fig)
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()
        # self.toolbar.SetSize(wx.Size(-1, 10))
        # self.toolbar.DeleteToolByPos(1)
        # self.toolbar.DeleteToolByPos(1)
        # self.toolbar.DeleteToolByPos(5)
        # self.toolbar.DeleteToolByPos(1)
        # self.toolbar.DeleteToolByPos(1)
        # self.toolbar.DeleteToolByPos(1)
        # self.toolbar.DeleteToolByPos(0)
        # self.toolbar.DeleteToolByPos(0)

        # add
        resettool = self.toolbar.AddLabelTool(id=wx.ID_ANY, label='reset', bitmap=wx.Bitmap('./res/reset.png')) # deprecated
        dir(self.toolbar.AddTool)
        # resettool = self.toolbar.AddTool(ToolId=wx.ID_ANY, label='reset', bitmap=wx.Bitmap('./res/reset.png'), 
        #     shortHelp='Reset graph and Kalman filter',
        #     longHelp='Reset the Kalman filter by reseting estimation uncertainties')
        self.toolbar.Realize()
        self.Bind(wx.EVT_TOOL, self.OnKalmanReset, resettool)

        self.toolbar.SetBackgroundColour(array(self.m_pnlGraphs.GetBackgroundColour()[0:3]))

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.TOP)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.m_pnlGraphs.SetSizer(self.sizer)
        self.m_pnlGraphs.Fit()

        subplot(211)
        self.ax = []
        ylim_bottom, ylim_top = (-1, 3)
        self.ax.append(plot(0, 'b', ylim_bottom, 'r--', ylim_top, 'r--', 0, 'g-', 0, 'r--', 0, 'r--'))
        subplot(212)
        ylim_bottom, ylim_top = (-1, 1)
        self.ax.append(plot(0, 'k', 0, 'b', ylim_bottom, 'r--', ylim_top, 'r--'))
        # hold(True)
        # show()

        self.checkFirmware()

        # connect automaticaly
        if len(self.m_cmbPort.GetItems()) == 1:
            self.OnConnect(None)

    def checkFirmware(self):
        """check for latest firmware version"""
        firmware_files = glob('update/firmware/turbidostat_v*.ino.hex')
        firmware_versions = [re.findall(r'turbidostat_v(.*)\.ino\.hex', file)[0] for file in firmware_files]
        firmware_versions.sort(reverse=True)
        print('FW versions=', firmware_versions)
        if len(firmware_versions) > 0:
            self.latest_firmware_version = firmware_versions[0]
        else:
            self.latest_firmware_version = '0'
        self.latest_firmware_version = float(self.latest_firmware_version[0] + '.' + self.latest_firmware_version[1:])

    def findSerialPorts(self):
        """Find serial ports of available turbidostats and update GUI."""
        serialport_list = serial.tools.list_ports.comports()
        if os.name == 'posix':
            port_prefix = 'USB'
        elif os.name == 'nt':
            port_prefix = 'COM'
        serialports = [row[0] for row in serialport_list if port_prefix in row[0]]
        serialports.sort()

        # try to connect to see if port is available
        # for port in serialports:
        #     try:
        #         self.setDTR(port, False)
        #         ser = serial.Serial(port, 115200, timeout=0, exclusive=True)
        #         sleep(0.1)
        #         ser.close()
        #     except serial.SerialException:
        #         serialports.remove(port)
        #         print('remove port ', port)

        if len(serialports) > 0:
            self.m_cmbPort.SetItems(serialports)
            self.m_cmbPort.SetValue(serialports[0])
        else:
            self.m_cmbPort.SetValue('Serial Port')

    def setDTR(self, port, dtr_flag):

        if os.name == 'posix':
            import termios
            try:
                f = open(port)
                attrs = termios.tcgetattr(f)
                # print('DTR= ' + str(attrs[2] & termios.HUPCL))
                if dtr_flag:
                    attrs[2] = attrs[2] | termios.HUPCL
                else:
                    attrs[2] = attrs[2] & ~termios.HUPCL
                termios.tcsetattr(f, termios.TCSAFLUSH, attrs)
                f.flush()  # maybe unnecessary
                f.close()
            except PermissionError:
                print('PermissionError')
                eprint(PermissionError.strerror)
        elif os.name == 'nt':
            ser = serial.Serial()
            ser.port = port
            ser.setDTR(dtr_flag)
            # ser.close()
            # sleep(0.2)

    def connect(self, data_source):
        # turn off reset on connect
        serialport_list = serial.tools.list_ports.comports()
        if os.name == 'posix':
            port_prefix = 'USB'
        elif os.name == 'nt':
            port_prefix = 'COM'
        serialports = [row[0] for row in serialport_list if port_prefix in row[0]]

        # print(serialports)
        if data_source in serialports:
            self.setDTR(data_source, False)

        try:
            # workaround for reconnect bug in linux
            self.ser = serial.Serial(data_source, 9600, timeout=0, exclusive=True)
            self.dummy_mode = False
        except IOError:
            self.ser = None
            try:
                # open prerecorded file
                self.dummy_file = open(data_source)
                self.dummy_mode = True
            except:
                self.dummy_mode = False

        # connect to serial device
        if self.ser:
            # first close lower speed serial connection (linux workaround)
            self.ser.close()

            # now connect with correct speed
            # self.ser = serial.Serial(data_source, 115200, timeout=0)
            self.ser = serial.Serial(data_source, 115200, exclusive=True)
            self.ser.flush()

            # data files 
            port = data_source
            _, port_name = os.path.split(port)
            if self.device_name:
                prefix = self.device_name
            else:
                prefix = ''
            # basename = prefix + '_' + port_name + '_' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            # data_file_path = data_folder + '/' + prefix + '/' + basename + '.txt'
            basename = port_name + '_' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            data_file_path = data_folder + '/' + prefix + '/' + basename + '.txt'
            self.logfile = open(data_file_path, 'w+')
            data_file_path_csv = data_folder + '/' + basename + '.csv'
            self.logfile_csv = open(data_file_path_csv, 'w+')

        if self.ser or self.dummy_mode:
            self.connected = True
            self.connecting = False
            self.done = False

            _thread.start_new_thread(self.SerialThread, ())

    def disconnect(self):
        """Disconnect from serial port."""
        self.I0 = nan
        self.logfile.close()
        self.connected = False
        if self.ser:
            self.ser.close()
            self.ser = None
        # sleep(1)
        wx.CallAfter(self.m_tcDeviceName.SetValue, '')
        self.device_name = None
        self.device_id = None
        self.firmware_version = None
        self.updateTitle()
        self.findSerialPorts()
        # sleep(1)

    def openSerialSession(self):
        self.connect(self.data_source)
        self.logToCSVFile('#time [s]\tIntensity\tOD measured\tOD estimate\tOD estimate uncertainty\tdoubling rate [db/hr]\tdoubling rate uncertainty [db/hr]\tstirrer speed [rpm]\ttemperature [degree C])\n')

        self.pump = False
        self.n_pump_distrust = 10
        self.invalid_samples_left = self.n_pump_distrust
        self.connecting = False

    def closeSerialSession(self):
        self.done = True
        sleep(0.2)
        self.connecting = False
        self.disconnect()

    def OnConnect(self, event):
        if self.m_cmbPort.GetValue() in ('', 'Serial Port'):
            self.findSerialPorts()
            return

        if not self.connected and not self.connecting:
            self.data_source = self.m_cmbPort.GetValue()
            self.openSerialSession()

            if self.ser:
                for widget in self.m_widgetGroup:
                    widget.Enable()
                self.OnSelectPumpMode(event)    # disable unselected pump mode widgets
                print('connect to ' + str(self.data_source) + '...')

            # stop if no valid data source available
            if self.ser is None and self.dummy_mode is False:
                dlg = wx.MessageDialog(self, "Cannot connect to turbidostat" + self.data_source, "Warning", wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                self.findSerialPorts()

            if self.ser or self.dummy_mode:
                self.m_btnConnect.SetLabel('disconnect')
                self.m_bitmConnected.SetBitmap(wx.Bitmap('./res/connected.png'))
                self.m_cmbPort.Disable()

        else:
            self.closeSerialSession()
            self.m_btnConnect.SetLabel('connect')
            self.m_bitmConnected.SetBitmap(wx.Bitmap('./res/disconnected.png'))
            self.m_cmbPort.Enable()
            for widget in self.m_widgetGroup:
                widget.Disable()
            print('_\n')

    def sendCmd(self, cmd):
        cmd = cmd + chr(10)
        print(cmd.strip())
        self.ser.write(cmd.encode())

    def setTime(self, time):
        self.sendCmd('ST ' + str(int(time)))

    def getDeviceSettings(self):
        self.sendCmd('GS')

    def OnSetI0(self, event):
        self.sendCmd('SI0')

    def OnSetTargetOD(self, event):
        od = self.m_tcTargetOD.GetValue().replace(',', '.')
        self.sendCmd('SOD ' + od)

    def OnSetPumpInterval(self, event):
        duration = self.m_tcPumpInterval.GetValue()
        self.sendCmd('SPW ' + duration)

    def OnSetPumpDuration(self, event):
        duration = self.m_tcPumpDuration.GetValue()
        self.sendCmd('SPD ' + duration)

    def OnPumpPowerSlider(self, event):
        power = self.m_sldPumpPower.GetValue()
        self.m_txtPumpPowerPercentage.SetLabel('%.1f' % (100.0 * power / 255) + '%')
        self.sendCmd('SPP ' + str(int(map_lin_log(power))))

    def OnAirpumpPowerSlider(self, event):
        power = self.m_sldAirpumpPower.GetValue()
        self.m_txtAirpumpPowerPercentage.SetLabel('%.1f' % (100.0 * power / 255) + '%')
        self.sendCmd('SAP ' + str(int(map_lin_log(power))))

    def OnSetPumpPower(self, event):
        power = self.m_sldPumpPower.GetValue()
        self.sendCmd('SPP ' + str(power))

    def OnSetAirpumpPower(self, event):
        power = self.m_sldAirpumpPower.GetValue()
        self.sendCmd('SAP ' + str(power))

    def OnSetStirrerTargetSpeed(self, event):
        rpm = self.m_tcStirrerTargetSpeed.GetValue()
        self.sendCmd('SSS ' + rpm)

    def OnSetDeviceName(self, event):
        device_name = self.m_tcDeviceName.GetValue()
        try:
            data_file_folder = data_folder
            # data_file_folder = data_folder + device_name
            # if not os.path.exists(data_file_folder):
            #     os.mkdir(data_file_folder)

            self.sendCmd('SDN ' + device_name)
        except Exception as e:
            wx.MessageBox('invalid device name!')

    def OnSelectPumpMode(self, event):
        if self.m_rbPumpMode.GetSelection() == 0:  # automatic
            self.m_tbManualPump.SetValue(False)
            self.OnManualPump(event)
            for widget in self.m_widgetGroupAutomaticPump:
                widget.Enable()
            for widget in self.m_widgetGroupManualPump:
                widget.Disable()
            cmd = 'SPM ' + '0'
        else:
            for widget in self.m_widgetGroupAutomaticPump:
                widget.Disable()
            for widget in self.m_widgetGroupManualPump:
                widget.Enable()
            cmd = 'SPM ' + '1'
        self.sendCmd(cmd)

    def OnManualPump(self, event):
        if self.m_tbManualPump.GetValue():
            self.m_tbManualPump.SetLabel('Medium Pump ON')
            cmd = 'SMP ' + '1'
        else:
            self.m_tbManualPump.SetLabel('Medium Pump OFF')
            cmd = 'SMP ' + '0'
        self.sendCmd(cmd)

    def OnHalt(self, event):
        self.sendCmd('HALT')

    def OnHWReset(self, event):
        self.sendCmd('RESET')


    def OnTextControlChanged(self, event, original_value):
        """change bg color to indicate untransmitted value.
        reset background color on Enter to give visual feedback.
        """
        tc = event.GetEventObject()

        if tc.GetValue() == str(original_value):
            sys_color = wx.SYS_COLOUR_WINDOW
            color = wx.SystemSettings.GetColour(sys_color)
        else:
            # sys_color = wx.SYS_COLOUR_INFOBK
            color = wx.Colour((255, 240, 150))
        
        # color = wx.SystemSettings.GetColour(sys_color)
        tc.SetBackgroundColour(color)
        tc.Refresh()
        tc.Update()
        # self.Refresh()
        # self.Update()
        # tc.Show()

    def OnDeviceName(self, event):
        self.OnTextControlChanged(event, original_value=self.device_name)

    def OnTargetOD(self, event):
        self.OnTextControlChanged(event, original_value=self.target_od)
        
    def OnPumpInterval(self, event):
        self.OnTextControlChanged(event, original_value=self.pumpInterval)

    def OnPumpDuration(self, event):
        self.OnTextControlChanged(event, original_value=self.pumpDuration)

    def OnStirrerTargetSpeed(self, event):
        self.OnTextControlChanged(event, original_value=self.stirrerTargetSpeed)

    def OnPortEnter(self, event):
        self.OnConnect(event)

    def OnDeviceNameEnter(self, event):
        self.OnSetDeviceName(event)

    def OnTargetODEnter(self, event):
        self.OnSetTargetOD(event)

    def OnPumpIntervalEnter(self, event):
        self.OnSetPumpInterval(event)

    def OnPumpDurationEnter(self, event):
        self.OnSetPumpDuration(event)

    def OnStirrerTargetSpeedEnter(self, event):
        self.OnSetStirrerTargetSpeed(event)

    def OnConsoleInputEnter(self, event):
        self.sendCmd(self.m_txtConsoleInput.GetValue())

    def OnClose(self, event):
        self.done = True
        # print('done: ' + str(self.done))
        dlg = wx.MessageDialog(self,
            "Do you really want to close this application?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()

    # def OnPortFocus(self, event):
    #     if self.m_cmbPort.GetValue() == 'Serial Port':
    #         self.m_cmbPort.SelectAll()
    #         # self.m_cmbPort.SetTextSelection(-1, -1)

    # def OnPortKillFocus(self, event):    
    #     print('losfjlsadjfls')
    #     if self.m_cmbPort.GetValue() == 'Serial Port':
    #         self.m_cmbPort.SetTextSelection(0, 0)
    #         # self.m_cmbPort.SetTextSelection(-1, -1)

    def updateFirmware(self, event):
        # print('latest FW= ', self.latest_firmware_version)             
        # print('Firmware= ', self.firmware_version)
        if float(self.latest_firmware_version) > float(self.firmware_version):
            dlg = wx.MessageDialog(self, 
                u'A Firmware Update is available. Do you want to update now?\n'
                u'This will take around 15seconds.'
                u'\nYour version: ' + str(self.firmware_version) +
                u'\nNew version: ' + str(self.latest_firmware_version),
                u'Firmware Update', wx.YES_NO)
            if dlg.ShowModal() == wx.ID_YES:
                self.OnHalt(None)  # stop actuators
                self.OnConnect(None)  # disconnect
                if self.connected is False:
                    import subprocess
                    if os.name == 'posix':
                        avrdude = 'avrdude'
                    elif os.name == 'nt':
                        avrdude = './update/firmware/avrdude.exe'
                    print(os.getcwd())
                    firmware_file = 'turbidostat_v' + str(self.latest_firmware_version).replace('.', '') + '.ino.hex'
                    ps = subprocess.run([
                        avrdude,
                            '-Cavrdude.conf', '-V',
                            '-patmega328p', '-carduino',
                            '-P' + self.data_source, '-b57600', '-D',
                            '-Uflash:w:' + firmware_file + ':i'],
                        cwd='./update/firmware/',
                        stderr=subprocess.PIPE)
                    output = ps.stderr.decode('unicode_escape')
                    wx.MessageBox(output)

    def OnConsoleFocus(self, event):
        self.m_txtConsoleInput.SetFocus()

    def logToFile(self, f, s):
        if f is  None:
            return

        f.write(s)

        try:
            f.flush()
        # ignore and flush later ('magically' locked file, e.g. by excel import)
        except IOError as e:
            if e.errno != 13:
                debug_log.write(str(e.errno) + '\n')

    def logToTxtFile(self, s):
        self.logToFile(self.logfile, s)

    def logToCSVFile(self, s):
            self.logToFile(self.logfile_csv, s)

    def OnKalmanReset(self, event):
        # covariance of process
        self.Q = matrix([[0, 0],
                         [0, 10**(-13)]])

        # covariance of measurement
        self.R = 40**2
        self.P_OD = 0.005**2

        # Initialisierung
        self.I = nan
        self.x = matrix([log10(self.I0/self.I0), 1.0000]).T          # initial state
        self.P = matrix([[self.P_OD, 0],
                         [        0, (0.0005)**2]])                   # initial state covariance

        self.thread_lock.acquire()
        self.invalid_samples_left = 0

        # self.time_list               = self.time_list[-1]
        # self.measurement_list        = self.measurement_list[-1]
        # self.state_list              = self.state_list[-1]
        # self.dbrate_list             = self.dbrate_list[-1]
        # self.dbrate_uncertainty_list = self.dbrate_uncertainty_list[-1]
        # self.uncertainty_list        = self.uncertainty_list[-1]
        self.time_list = []
        self.measurement_list = []
        self.state_list = []
        self.dbrate_list = []
        self.dbrate_uncertainty_list = []
        self.uncertainty_list = []

        self.thread_lock.release()

    def plot(self):
        # if self.dummy_mode == False or (self.dummy_mode and (self.time % 0.5 == 0)):
        if self.dummy_mode == False or (self.dummy_mode):
            self.thread_lock.acquire()
            subplot(211)
            self.ax[0][0].set_xdata(self.time_list)
            self.ax[0][0].set_ydata(self.dbrate_list)
            self.ax[0][1].set_xdata(self.time_list)
            self.ax[0][1].set_ydata(r_[self.dbrate_list] - r_[self.dbrate_uncertainty_list])
            self.ax[0][2].set_xdata(self.time_list)
            self.ax[0][2].set_ydata(r_[self.dbrate_list] + r_[self.dbrate_uncertainty_list])
            xlim(0, self.time_list[-1])
            # ylim(min(r_[self.dbrate_list] - r_[self.dbrate_uncertainty_list]),
            #                    max(r_[self.dbrate_list] + r_[self.dbrate_uncertainty_list]))
            # ylim(min(r_[self.dbrate_list]), max(r_[self.dbrate_list] + r_[self.dbrate_uncertainty_list]))
            ylabel('rate [doublings/hr]')

            subplot(212)
            self.ax[1][0].set_xdata(self.time_list)
            self.ax[1][0].set_ydata(self.measurement_list)
            self.ax[1][1].set_xdata(self.time_list)
            self.ax[1][1].set_ydata(self.state_list)
            self.ax[1][2].set_xdata(self.time_list)
            self.ax[1][2].set_ydata(r_[self.state_list] - sqrt(r_[self.uncertainty_list]))
            self.ax[1][3].set_xdata(self.time_list)
            self.ax[1][3].set_ydata(r_[self.state_list] + sqrt(r_[self.uncertainty_list]))
            xlim(0, self.time_list[-1])
            # ylim(min(self.measurement_list), max(r_[self.measurement_list] + sqrt(r_[self.uncertainty_list])))
            xlabel('time [min]')
            ylabel('OD')
            self.canvas.draw()
            # self.Fit)
            self.thread_lock.release()

            if self.OD < -110:
                self.OD = 'n/A(-)'
                OD_1cm = 'n/A(-)'
            # else:
                # OD_1cm = self.OD * self.OD1cm_factor
            self.m_txtOD.SetLabel(str(round(float(self.OD), 3)))
            # self.m_txtOD1cm.SetLabel(str(round(OD_1cm, 3)))

    def updateTitle(self):
        self.SetTitle(
            ' name: ' + str(self.device_name) +
            # ' ('+
            # 'id: ' + str(self.device_id) +
            # ' fw: v' + str(self.firmware_version) + 
            # ')'
            ' - TurbidostatGUI v' + str(self.gui_version) 
            )


    def SerialThread(self):
        """Thread for processing serial data."""
        if self.threads > 0:
            return

        read_retries = 0
        max_read_retries = 5
        next_update = 0

        self.threads += 1
        # print('nthreads ', self.threads)
        new_sample_available = False
        msg = ''
        while not self.done:
            if self.connected:
                if self.dummy_mode:
                    # msg = self.dummy_file.readline().decode()
                    msg = self.dummy_file.readline()
                else:
                    try:
                        msg = msg + self.ser.readline().decode()
                        read_retries = 0
                    except:
                        read_retries += 1
                        if read_retries > max_read_retries:
                            print('Warning: could not read from data source ' + self.ser.port + ' (' + str(read_retries) + ')')
                            self.connected = False
                            self.connecting = True
                        continue

                if len(msg) > 1 and msg[-1] == '\n':
                    msg = msg.strip()
                    if msg.find('START') == 0 and len(self.time_list) > 0:
                        if self.time:
                            self.setTime(self.time * 60 * 1000)

                    for var, value in re.findall(r'(\S+)\s*:\s*(.+)', msg):
                        if var =='deviceName':
                            self.device_name = value
                            wx.CallAfter(self.m_tcDeviceName.SetValue, self.device_name)
                            self.updateTitle()

                        if var == 'deviceID':
                            self.device_id = value
                            self.updateTitle()

                        if var == 'version':
                            self.firmware_version = float(value)
                            self.updateTitle()
                            self.checkFirmware()
                            if self.latest_firmware_version > self.firmware_version:
                                wx.CallAfter(self.updateFirmware, None)
                            self.updateTitle()

                        if var =='I0':
                            self.I0 = float(value)
                            self.P[0, 0] = self.P_OD
                            self.x[0, 0] = log10(self.I0 / self.I)

                        if var == 'targetOD':
                            try:
                                self.target_od = float(value)
                            except ValueError as e:
                                wx.MessageBox('invalid value\n', str(e))
                            wx.CallAfter(self.m_tcTargetOD.SetValue, str(self.target_od))

                        if var == 'stirrerTargetSpeed':
                            self.stirrerTargetSpeed = int(value)
                            wx.CallAfter(self.m_tcStirrerTargetSpeed.SetValue, str(self.stirrerTargetSpeed))

                        if var == 'pumpDuration':
                            self.pumpDuration = int(value)
                            wx.CallAfter(self.m_tcPumpDuration.SetValue, str(self.pumpDuration))

                        if var == 'pumpInterval':
                            self.pumpInterval = int(value)
                            wx.CallAfter(self.m_tcPumpInterval.SetValue, str(self.pumpInterval))

                        if var == 'pumpMode':
                            self.pumpMode = int(value)
                            wx.CallAfter(self.m_rbPumpMode.SetSelection, int(self.pumpMode))

                        if var == 'pumpPower':
                            self.pumpPower = map_lin_log_inv(int(value))
                            print('pumpPower', self.pumpPower)
                            wx.CallAfter(self.m_sldPumpPower.SetValue, int(self.pumpPower))
                            wx.CallAfter(self.m_txtPumpPowerPercentage.SetLabel, '%.1f' % (100.0 * self.pumpPower / 255) + '%')

                        if var == 'airpumpPower':
                            self.airpump_power = map_lin_log_inv(int(value))
                            print('airpumpPower', self.airpumpPower)
                            wx.CallAfter(self.m_sldAirpumpPower.SetValue, int(self.airpump_power))
                            wx.CallAfter(self.m_txtAirpumpPowerPercentage.SetLabel, '%.1f' % (100.0 * self.airpump_power / 255) + '%')

                    if msg.find('pump: on') > -1:
                        self.pump = True
                        self.invalid_samples_left = self.n_pump_distrust

                    if msg.find('pump: off') > -1:
                        self.pump = False

                    # process data line
                    values = re.findall(r'([^=\t ]*)=([-0-9\.naninf]+)', msg)
                    for (var, value) in values:
                        # skip data line if it seems corrupted
                        if len(values) not in range(8, 11):  
                            print('corrupted data line', len(values))
                            print(msg)
                            # print(msg_printable)
                            continue

                        if var == 't':
                            self.time = float(value) / (60 * 1000)
                            if (self.time > 0.1) and None in (self.device_id, self.device_name, self.firmware_version):
                                self.getDeviceSettings()

                        if var == 'I':
                            self.I = float(value)

                            if not isnan(self.I0) and self.I != 0:
                                self.OD = log10(self.I0 / self.I)
                                new_sample_available = True

                        if var == 'f_stirrer':
                            self.stirrer_speed = float(value)
                            wx.CallAfter(self.m_txtStirrerSpeed.SetLabel, value)

                        if var == 'temp':
                            temperature = float(value)


                    if new_sample_available:
                        self.thread_lock.acquire()
                        if len(self.time_list) == 0:
                            self.starttime = self.time
                        self.time_list.append(self.time - self.starttime)
                        self.measurement_list.append(self.OD)

                        # -------- Kalman----------
                        # increase uncertainty after pumps
                        # print('self.invalid_samples_left=', self.invalid_samples_left)
                        sample_is_invalid = (0 < self.invalid_samples_left)
                        if sample_is_invalid:
                            std_I = 40
                            self.P[0, 0] = (-std_I / (self.I * log(10)))**2
                            self.P[1, 0] = 0
                            self.P[0, 1] = 0
                            self.x[0, 0] = log10(self.I0 / self.I)
                            if self.pump is False:
                                self.invalid_samples_left -= 1

                        # Extended Kalman Filter step
                        self.x, self.P, self.K = ekf(self.f, self.x, self.P, self.h, self.I, self.Q, self.R, I0=self.I0)     

                        # increase uncertainty if measurement and prediction differs greatly
                        if abs(self.I - self.h(self.x)) > 5*sqrt(self.R):
                            self.P[1, 0] = 0
                            self.P[0, 1] = 0
                            self.P[0, 0] = (self.x[0, 0] - log10(self.I0 / self.I))**2

                        x             = self.x[0, 0]
                        geom_rate     = self.x[1, 0]
                        db_rate       = 3600 * log(geom_rate) / log(2)
                        var_x         = self.P[0, 0]
                        var_geom_rate = self.P[1, 1]
                        std_db_rate   = 3600 * sqrt(var_geom_rate) / (log(2) * geom_rate)
                        self.uncertainty_list.append(var_x)
                        self.state_list.append(x)
                        self.dbrate_list.append(db_rate)
                        self.dbrate_uncertainty_list.append(std_db_rate)
                        self.thread_lock.release()

                        # wx.CallAfter(self.plot)
                        # print('time', self.time, next_update)
                        if next_update < self.time:
                            wx.CallAfter(self.plot)
                            dt = (1 + (self.time_list[-1]-self.starttime)/20 )/ 60
                            # print('-----------=========== dt', dt*60,'===============-----------------')
                            next_update = self.time + dt
                        # sleep(0.1)

                        logstring = '%.0f\t%.0f\t%f\t%f\t%f\t%f\t%f\t%.1f\t%.2f\n' % (self.time * 60, self.I, self.OD, x, sqrt(var_x), db_rate, std_db_rate, self.stirrer_speed, temperature)
                        self.logToCSVFile(logstring)
                        new_sample_available = False

                    # remove non printable characters like zeros
                    msg += '\n'
                    msg_printable = ''.join(s for s in msg if s in string.printable)
                    sys.stdout.write(msg)
                    self.logToTxtFile(msg_printable)
                    # wx.CallAfter(self.m_txtConsole.AppendText, msg_printable)
                    msg = ''
                sleep(0.001)

            elif self.connecting:
                print('connecting to ' + str(self.data_source) + '...\n')
                self.disconnect()
                sleep(1)
                self.connect(self.data_source)

        self.threads -= 1
        eprint('Info: SerialThread finished, threads remaining', self.threads)
        # except:
        #     self.OnConnect(None)

    def __del__(self):
        """Turbidostat class destructor."""
        print('close TurbidostatGUI ' + str(self.done), flush=True)
        sys.stdout.flush()
        # while self.threads > 0:
        if self.connected:
            self.ser.close()


def main():
    """Entry point of GUI."""
    ex = wx.App()
    gui = TurbidostatGUI()
    ex.MainLoop()

if __name__ == '__main__':
    main()
