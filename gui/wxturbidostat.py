# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.aui

###########################################################################
## Class TsFrame
###########################################################################

class TsFrame ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Turbidostat", pos = wx.DefaultPosition, size = wx.Size( 558,660 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.Size( 444,660 ), wx.DefaultSize )

		bSizer2 = wx.BoxSizer( wx.VERTICAL )

		self.m_auinotebook = wx.aui.AuiNotebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_NB_SCROLL_BUTTONS|wx.aui.AUI_NB_WINDOWLIST_BUTTON )
		self.m_pnlSettings = wx.Panel( self.m_auinotebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizerSuper = wx.FlexGridSizer( 4, 1, 0, 0 )
		fgSizerSuper.AddGrowableCol( 0 )
		fgSizerSuper.AddGrowableRow( 0 )
		fgSizerSuper.AddGrowableRow( 1 )
		fgSizerSuper.AddGrowableRow( 2 )
		fgSizerSuper.AddGrowableRow( 3 )
		fgSizerSuper.SetFlexibleDirection( wx.BOTH )
		fgSizerSuper.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		sbSizerConnection = wx.StaticBoxSizer( wx.StaticBox( self.m_pnlSettings, wx.ID_ANY, u"Connection" ), wx.VERTICAL )

		fgSizerConnection = wx.FlexGridSizer( 2, 5, 0, 0 )
		fgSizerConnection.AddGrowableCol( 1 )
		fgSizerConnection.SetFlexibleDirection( wx.BOTH )
		fgSizerConnection.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_txtPort = wx.StaticText( sbSizerConnection.GetStaticBox(), wx.ID_ANY, u"Port:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtPort.Wrap( -1 )

		fgSizerConnection.Add( self.m_txtPort, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		m_cmbPortChoices = [ u"?" ]
		self.m_cmbPort = wx.ComboBox( sbSizerConnection.GetStaticBox(), wx.ID_ANY, u"Serial Port", wx.DefaultPosition, wx.DefaultSize, m_cmbPortChoices, wx.TE_PROCESS_ENTER|wx.TAB_TRAVERSAL )
		self.m_cmbPort.SetMinSize( wx.Size( 140,-1 ) )

		fgSizerConnection.Add( self.m_cmbPort, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_btnConnect = wx.Button( sbSizerConnection.GetStaticBox(), wx.ID_ANY, u"connect", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizerConnection.Add( self.m_btnConnect, 0, wx.ALL, 5 )

		self.m_bitmConnected = wx.StaticBitmap( sbSizerConnection.GetStaticBox(), wx.ID_ANY, wx.Bitmap( u"res/disconnected.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizerConnection.Add( self.m_bitmConnected, 0, wx.ALL, 5 )

		self.m_btnReset = wx.Button( sbSizerConnection.GetStaticBox(), wx.ID_ANY, u"RESET", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_btnReset.SetToolTip( u"Restart the Turbidostat Device.\nSettings will be retained." )

		fgSizerConnection.Add( self.m_btnReset, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )

		self.m_txtDeviceName = wx.StaticText( sbSizerConnection.GetStaticBox(), wx.ID_ANY, u"Device:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtDeviceName.Wrap( -1 )

		fgSizerConnection.Add( self.m_txtDeviceName, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.m_tcDeviceName = wx.TextCtrl( sbSizerConnection.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,-1 ), wx.TE_PROCESS_ENTER )
		self.m_tcDeviceName.SetToolTip( u"The name of the device.\nIt will be used for saving the data log files." )

		fgSizerConnection.Add( self.m_tcDeviceName, 0, wx.ALL|wx.EXPAND, 5 )


		sbSizerConnection.Add( fgSizerConnection, 1, wx.ALL|wx.EXPAND, 5 )


		fgSizerSuper.Add( sbSizerConnection, 1, wx.ALL|wx.EXPAND, 5 )

		sbSizerOD = wx.StaticBoxSizer( wx.StaticBox( self.m_pnlSettings, wx.ID_ANY, u"Optical Density (at 650nm)" ), wx.VERTICAL )

		fgSizerOD = wx.FlexGridSizer( 3, 4, 0, 0 )
		fgSizerOD.SetFlexibleDirection( wx.BOTH )
		fgSizerOD.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_txtODText = wx.StaticText( sbSizerOD.GetStaticBox(), wx.ID_ANY, u"OD:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtODText.Wrap( -1 )

		fgSizerOD.Add( self.m_txtODText, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.m_txtOD = wx.StaticText( sbSizerOD.GetStaticBox(), wx.ID_ANY, u"n/A", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtOD.Wrap( -1 )

		fgSizerOD.Add( self.m_txtOD, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.m_btnSetI0 = wx.Button( sbSizerOD.GetStaticBox(), wx.ID_ANY, u"set OD₀", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_btnSetI0.SetToolTip( u"Set the current OD as the reference OD₀.\n(Internally the Intensity I₀ is used)" )

		fgSizerOD.Add( self.m_btnSetI0, 0, wx.ALL, 5 )


		fgSizerOD.Add( ( 0, 0), 1, wx.ALL, 5 )

		self.m_txtOD1cmText = wx.StaticText( sbSizerOD.GetStaticBox(), wx.ID_ANY, u"OD(1cm):", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtOD1cmText.Wrap( -1 )

		self.m_txtOD1cmText.Hide()

		fgSizerOD.Add( self.m_txtOD1cmText, 0, wx.ALL, 5 )

		self.m_txtOD1cm = wx.StaticText( sbSizerOD.GetStaticBox(), wx.ID_ANY, u"n/A", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtOD1cm.Wrap( -1 )

		self.m_txtOD1cm.Hide()

		fgSizerOD.Add( self.m_txtOD1cm, 0, wx.ALL, 5 )


		fgSizerOD.Add( ( 0, 0), 1, wx.ALL, 5 )


		fgSizerOD.Add( ( 0, 0), 1, wx.ALL, 5 )

		self.m_txtTargetODText = wx.StaticText( sbSizerOD.GetStaticBox(), wx.ID_ANY, u"Target OD:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtTargetODText.Wrap( -1 )

		fgSizerOD.Add( self.m_txtTargetODText, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.m_tcTargetOD = wx.TextCtrl( sbSizerOD.GetStaticBox(), wx.ID_ANY, u"1.54", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER )
		self.m_tcTargetOD.SetMaxLength( 0 )
		fgSizerOD.Add( self.m_tcTargetOD, 0, wx.ALL, 5 )

		self.m_btnSetTargetOD = wx.Button( sbSizerOD.GetStaticBox(), wx.ID_ANY, u"&set", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_btnSetTargetOD.SetToolTip( u"set Target Optical Density" )

		fgSizerOD.Add( self.m_btnSetTargetOD, 0, wx.ALL, 5 )


		sbSizerOD.Add( fgSizerOD, 1, wx.ALL, 5 )


		fgSizerSuper.Add( sbSizerOD, 1, wx.ALL|wx.EXPAND, 5 )

		sbSizerPump = wx.StaticBoxSizer( wx.StaticBox( self.m_pnlSettings, wx.ID_ANY, u"Pump" ), wx.VERTICAL )

		gSizerPump = wx.FlexGridSizer( 5, 4, 0, 0 )
		gSizerPump.SetFlexibleDirection( wx.BOTH )
		gSizerPump.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		m_rbPumpModeChoices = [ u"auto", u"manual" ]
		self.m_rbPumpMode = wx.RadioBox( sbSizerPump.GetStaticBox(), wx.ID_ANY, u"Pump mode", wx.DefaultPosition, wx.DefaultSize, m_rbPumpModeChoices, 2, wx.RA_SPECIFY_COLS )
		self.m_rbPumpMode.SetSelection( 0 )
		gSizerPump.Add( self.m_rbPumpMode, 0, 0, 5 )

		self.m_tbManualPump = wx.ToggleButton( sbSizerPump.GetStaticBox(), wx.ID_ANY, u"Medium Pump Off", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_tbManualPump.SetValue( True )
		gSizerPump.Add( self.m_tbManualPump, 0, wx.ALL, 5 )

		self.m_txtManualPump = wx.StaticText( sbSizerPump.GetStaticBox(), wx.ID_ANY, u"Manual pump:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtManualPump.Wrap( -1 )

		self.m_txtManualPump.Hide()

		gSizerPump.Add( self.m_txtManualPump, 0, wx.ALL, 5 )


		gSizerPump.Add( ( 0, 0), 1, wx.ALL, 5 )

		self.m_txtPumpInterval = wx.StaticText( sbSizerPump.GetStaticBox(), wx.ID_ANY, u"Pump interval:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtPumpInterval.Wrap( -1 )

		gSizerPump.Add( self.m_txtPumpInterval, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.m_tcPumpInterval = wx.TextCtrl( sbSizerPump.GetStaticBox(), wx.ID_ANY, u"5000", wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER|wx.TE_RIGHT )
		self.m_tcPumpInterval.SetToolTip( u"pump pulse interval in ms (milli seconds)\ndefault: 5000" )

		gSizerPump.Add( self.m_tcPumpInterval, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )

		self.m_txtPumpIntervalUnit = wx.StaticText( sbSizerPump.GetStaticBox(), wx.ID_ANY, u"ms", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtPumpIntervalUnit.Wrap( -1 )

		gSizerPump.Add( self.m_txtPumpIntervalUnit, 0, wx.ALL, 5 )

		self.m_btnSetPumpInterval = wx.Button( sbSizerPump.GetStaticBox(), wx.ID_ANY, u"set", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_btnSetPumpInterval.SetToolTip( u"Set the time between the pump pulses." )

		gSizerPump.Add( self.m_btnSetPumpInterval, 0, wx.ALL, 5 )

		self.m_txtPumpDuration = wx.StaticText( sbSizerPump.GetStaticBox(), wx.ID_ANY, u"Pump duration:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtPumpDuration.Wrap( -1 )

		gSizerPump.Add( self.m_txtPumpDuration, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.m_tcPumpDuration = wx.TextCtrl( sbSizerPump.GetStaticBox(), wx.ID_ANY, u"1000", wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER|wx.TE_RIGHT )
		self.m_tcPumpDuration.SetToolTip( u"pump pulse duration in ms (milli seconds)\ndefault: 1000" )

		gSizerPump.Add( self.m_tcPumpDuration, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )

		self.m_txtPumpDurationUnit = wx.StaticText( sbSizerPump.GetStaticBox(), wx.ID_ANY, u"ms", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtPumpDurationUnit.Wrap( -1 )

		gSizerPump.Add( self.m_txtPumpDurationUnit, 0, wx.ALL, 5 )

		self.m_btnSetPumpDuration = wx.Button( sbSizerPump.GetStaticBox(), wx.ID_ANY, u"set", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_btnSetPumpDuration.SetToolTip( u"Set the duration of each pump pulse." )

		gSizerPump.Add( self.m_btnSetPumpDuration, 0, wx.ALL, 5 )

		self.m_txtPumpPower = wx.StaticText( sbSizerPump.GetStaticBox(), wx.ID_ANY, u"Pump power:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtPumpPower.Wrap( -1 )

		gSizerPump.Add( self.m_txtPumpPower, 0, wx.ALL, 5 )

		self.m_sldPumpPower = wx.Slider( sbSizerPump.GetStaticBox(), wx.ID_ANY, 255, 0, 255, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
		self.m_sldPumpPower.SetMinSize( wx.Size( 100,-1 ) )

		gSizerPump.Add( self.m_sldPumpPower, 0, wx.ALL, 5 )

		self.m_txtPumpPowerPercentage = wx.StaticText( sbSizerPump.GetStaticBox(), wx.ID_ANY, u"100.0%", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtPumpPowerPercentage.Wrap( -1 )

		gSizerPump.Add( self.m_txtPumpPowerPercentage, 0, wx.ALL, 5 )

		self.m_btnSetPumpPower = wx.Button( sbSizerPump.GetStaticBox(), wx.ID_ANY, u"set", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_btnSetPumpPower.Hide()

		gSizerPump.Add( self.m_btnSetPumpPower, 0, wx.ALL, 5 )

		self.m_txtAirpumpPower = wx.StaticText( sbSizerPump.GetStaticBox(), wx.ID_ANY, u"Air pump power:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtAirpumpPower.Wrap( -1 )

		gSizerPump.Add( self.m_txtAirpumpPower, 0, wx.ALL, 5 )

		self.m_sldAirpumpPower = wx.Slider( sbSizerPump.GetStaticBox(), wx.ID_ANY, 255, 0, 255, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
		self.m_sldAirpumpPower.SetMinSize( wx.Size( 100,-1 ) )

		gSizerPump.Add( self.m_sldAirpumpPower, 0, wx.ALL, 5 )

		self.m_txtAirpumpPowerPercentage = wx.StaticText( sbSizerPump.GetStaticBox(), wx.ID_ANY, u"100.0%", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtAirpumpPowerPercentage.Wrap( -1 )

		gSizerPump.Add( self.m_txtAirpumpPowerPercentage, 0, wx.ALL, 5 )

		self.m_btnSetAirpumpPower = wx.Button( sbSizerPump.GetStaticBox(), wx.ID_ANY, u"set", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_btnSetAirpumpPower.Hide()

		gSizerPump.Add( self.m_btnSetAirpumpPower, 0, wx.ALL, 5 )


		sbSizerPump.Add( gSizerPump, 1, wx.ALL, 5 )


		fgSizerSuper.Add( sbSizerPump, 1, wx.ALL|wx.EXPAND, 5 )

		sbSizerStirrer = wx.StaticBoxSizer( wx.StaticBox( self.m_pnlSettings, wx.ID_ANY, u"Stirrer" ), wx.VERTICAL )

		fgSizerStirrer = wx.FlexGridSizer( 2, 4, 0, 0 )
		fgSizerStirrer.SetFlexibleDirection( wx.BOTH )
		fgSizerStirrer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_txtStirrerTargetSpeed = wx.StaticText( sbSizerStirrer.GetStaticBox(), wx.ID_ANY, u"Stirrer target speed:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtStirrerTargetSpeed.Wrap( -1 )

		fgSizerStirrer.Add( self.m_txtStirrerTargetSpeed, 0, wx.ALL, 5 )

		self.m_tcStirrerTargetSpeed = wx.TextCtrl( sbSizerStirrer.GetStaticBox(), wx.ID_ANY, u"800", wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER|wx.TE_RIGHT )
		self.m_tcStirrerTargetSpeed.SetToolTip( u"stirrer speed in RPM (rounds per minute)\ndefault: 800" )

		fgSizerStirrer.Add( self.m_tcStirrerTargetSpeed, 0, wx.ALL, 5 )

		self.m_txtStirrerTargetSpeedUnit = wx.StaticText( sbSizerStirrer.GetStaticBox(), wx.ID_ANY, u"rpm", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtStirrerTargetSpeedUnit.Wrap( -1 )

		fgSizerStirrer.Add( self.m_txtStirrerTargetSpeedUnit, 0, wx.ALL, 5 )

		self.m_btnSetStirrerTargetSpeed = wx.Button( sbSizerStirrer.GetStaticBox(), wx.ID_ANY, u"set", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_btnSetStirrerTargetSpeed.SetToolTip( u"Set the speed of the magnetic stirrer." )

		fgSizerStirrer.Add( self.m_btnSetStirrerTargetSpeed, 0, wx.ALL, 5 )

		self.m_txtStirrerSpeedText = wx.StaticText( sbSizerStirrer.GetStaticBox(), wx.ID_ANY, u"Stirrer speed:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtStirrerSpeedText.Wrap( -1 )

		fgSizerStirrer.Add( self.m_txtStirrerSpeedText, 0, wx.ALL, 5 )

		self.m_txtStirrerSpeed = wx.StaticText( sbSizerStirrer.GetStaticBox(), wx.ID_ANY, u"800", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtStirrerSpeed.Wrap( -1 )

		fgSizerStirrer.Add( self.m_txtStirrerSpeed, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )

		self.m_txtStirrerSpeedUnit = wx.StaticText( sbSizerStirrer.GetStaticBox(), wx.ID_ANY, u"rpm", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtStirrerSpeedUnit.Wrap( -1 )

		fgSizerStirrer.Add( self.m_txtStirrerSpeedUnit, 0, wx.ALL, 5 )


		fgSizerStirrer.Add( ( 0, 0), 1, wx.ALL, 5 )


		sbSizerStirrer.Add( fgSizerStirrer, 1, wx.ALL, 5 )


		fgSizerSuper.Add( sbSizerStirrer, 1, wx.ALL|wx.EXPAND, 5 )


		self.m_pnlSettings.SetSizer( fgSizerSuper )
		self.m_pnlSettings.Layout()
		fgSizerSuper.Fit( self.m_pnlSettings )
		self.m_auinotebook.AddPage( self.m_pnlSettings, u"Settings", True, wx.NullBitmap )
		self.m_pnlGraphs = wx.Panel( self.m_auinotebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_auinotebook.AddPage( self.m_pnlGraphs, u"Graph", False, wx.NullBitmap )
		self.m_pnlConsole = wx.Panel( self.m_auinotebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_pnlConsole.SetBackgroundColour( wx.Colour( 4, 34, 7 ) )
		self.m_pnlConsole.Hide()

		fgSizerConsole = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizerConsole.AddGrowableCol( 0 )
		fgSizerConsole.AddGrowableRow( 0 )
		fgSizerConsole.SetFlexibleDirection( wx.BOTH )
		fgSizerConsole.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_txtConsole = wx.TextCtrl( self.m_pnlConsole, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY|wx.BORDER_NONE|wx.VSCROLL )
		self.m_txtConsole.SetFont( wx.Font( 6, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
		self.m_txtConsole.SetForegroundColour( wx.Colour( 207, 230, 206 ) )
		self.m_txtConsole.SetBackgroundColour( wx.Colour( 4, 34, 7 ) )

		fgSizerConsole.Add( self.m_txtConsole, 1, wx.ALL|wx.EXPAND, 15 )

		self.m_txtConsoleInput = wx.TextCtrl( self.m_pnlConsole, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		fgSizerConsole.Add( self.m_txtConsoleInput, 0, wx.ALL|wx.EXPAND, 5 )


		self.m_pnlConsole.SetSizer( fgSizerConsole )
		self.m_pnlConsole.Layout()
		fgSizerConsole.Fit( self.m_pnlConsole )
		self.m_auinotebook.AddPage( self.m_pnlConsole, u"Console", False, wx.NullBitmap )

		bSizer2.Add( self.m_auinotebook, 1, wx.EXPAND |wx.ALL, 5 )


		self.SetSizer( bSizer2 )
		self.Layout()

		# Connect Events
		self.m_cmbPort.Bind( wx.EVT_KILL_FOCUS, self.OnPortKillFocus )
		self.m_cmbPort.Bind( wx.EVT_SET_FOCUS, self.OnPortFocus )
		self.m_cmbPort.Bind( wx.EVT_TEXT_ENTER, self.OnPortEnter )
		self.m_btnConnect.Bind( wx.EVT_BUTTON, self.OnConnect )
		self.m_btnReset.Bind( wx.EVT_BUTTON, self.OnHWReset )
		self.m_tcDeviceName.Bind( wx.EVT_TEXT, self.OnDeviceName )
		self.m_tcDeviceName.Bind( wx.EVT_TEXT_ENTER, self.OnDeviceNameEnter )
		self.m_btnSetI0.Bind( wx.EVT_BUTTON, self.OnSetI0 )
		self.m_tcTargetOD.Bind( wx.EVT_TEXT, self.OnTargetOD )
		self.m_tcTargetOD.Bind( wx.EVT_TEXT_ENTER, self.OnTargetODEnter )
		self.m_btnSetTargetOD.Bind( wx.EVT_BUTTON, self.OnSetTargetOD )
		self.m_rbPumpMode.Bind( wx.EVT_RADIOBOX, self.OnSelectPumpMode )
		self.m_tbManualPump.Bind( wx.EVT_TOGGLEBUTTON, self.OnManualPump )
		self.m_tcPumpInterval.Bind( wx.EVT_TEXT, self.OnPumpInterval )
		self.m_tcPumpInterval.Bind( wx.EVT_TEXT_ENTER, self.OnPumpIntervalEnter )
		self.m_btnSetPumpInterval.Bind( wx.EVT_BUTTON, self.OnSetPumpInterval )
		self.m_tcPumpDuration.Bind( wx.EVT_TEXT, self.OnPumpDuration )
		self.m_tcPumpDuration.Bind( wx.EVT_TEXT_ENTER, self.OnPumpDurationEnter )
		self.m_btnSetPumpDuration.Bind( wx.EVT_BUTTON, self.OnSetPumpDuration )
		self.m_sldPumpPower.Bind( wx.EVT_SCROLL, self.OnPumpPowerSlider )
		self.m_btnSetPumpPower.Bind( wx.EVT_BUTTON, self.OnSetPumpPower )
		self.m_sldAirpumpPower.Bind( wx.EVT_SCROLL, self.OnAirpumpPowerSlider )
		self.m_btnSetAirpumpPower.Bind( wx.EVT_BUTTON, self.OnSetAirpumpPower )
		self.m_tcStirrerTargetSpeed.Bind( wx.EVT_TEXT, self.OnStirrerTargetSpeed )
		self.m_tcStirrerTargetSpeed.Bind( wx.EVT_TEXT_ENTER, self.OnStirrerTargetSpeedEnter )
		self.m_btnSetStirrerTargetSpeed.Bind( wx.EVT_BUTTON, self.OnSetStirrerTargetSpeed )
		self.m_txtConsole.Bind( wx.EVT_SET_FOCUS, self.OnConsoleFocus )
		self.m_txtConsoleInput.Bind( wx.EVT_TEXT_ENTER, self.OnConsoleInputEnter )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def OnPortKillFocus( self, event ):
		event.Skip()

	def OnPortFocus( self, event ):
		event.Skip()

	def OnPortEnter( self, event ):
		event.Skip()

	def OnConnect( self, event ):
		event.Skip()

	def OnHWReset( self, event ):
		event.Skip()

	def OnDeviceName( self, event ):
		event.Skip()

	def OnDeviceNameEnter( self, event ):
		event.Skip()

	def OnSetI0( self, event ):
		event.Skip()

	def OnTargetOD( self, event ):
		event.Skip()

	def OnTargetODEnter( self, event ):
		event.Skip()

	def OnSetTargetOD( self, event ):
		event.Skip()

	def OnSelectPumpMode( self, event ):
		event.Skip()

	def OnManualPump( self, event ):
		event.Skip()

	def OnPumpInterval( self, event ):
		event.Skip()

	def OnPumpIntervalEnter( self, event ):
		event.Skip()

	def OnSetPumpInterval( self, event ):
		event.Skip()

	def OnPumpDuration( self, event ):
		event.Skip()

	def OnPumpDurationEnter( self, event ):
		event.Skip()

	def OnSetPumpDuration( self, event ):
		event.Skip()

	def OnPumpPowerSlider( self, event ):
		event.Skip()

	def OnSetPumpPower( self, event ):
		event.Skip()

	def OnAirpumpPowerSlider( self, event ):
		event.Skip()

	def OnSetAirpumpPower( self, event ):
		event.Skip()

	def OnStirrerTargetSpeed( self, event ):
		event.Skip()

	def OnStirrerTargetSpeedEnter( self, event ):
		event.Skip()

	def OnSetStirrerTargetSpeed( self, event ):
		event.Skip()

	def OnConsoleFocus( self, event ):
		event.Skip()

	def OnConsoleInputEnter( self, event ):
		event.Skip()


