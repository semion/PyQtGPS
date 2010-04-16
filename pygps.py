#!/usr/bin/python
# -*- coding: UTF-8 -*-
from waypoints import AirPort
from decimal import Decimal

# pygps.py

import sys, os, re, math, datetime, signal, decimal, shutil, bluetooth 
from PyQt4 import QtCore, QtGui
from globalmaptiles import GlobalMercator
from gpsparser import GPSString
from tilegrid import TileGrid
from renderarea import RenderArea
from BT_2 import *
from PyQt4.Qt import *
from ProgressBar import * 
from waypoints import *       

class Pygps(QtGui.QWidget):
    '''PyGPS application by Semion Spivak and Boris Shterenberg'''
    def __init__(self, parent = None):
        
        QtGui.QWidget.__init__(self, parent)
        self.deviceAddress = Bluetooth_Search(self)
        self.deviceAddress.start()
        self.sysPath = os.path.join(sys.path[0], "")
        self.Air =  AirPort(self)
        self.fpath=None
        #self.deviceAddress = Bluetooth_Search(self)
        #self.deviceStatus = Bluetooth_Search(self)
        self.bt_Flag = False
        self.mainFlag = False
        self.fileFlag = False
        self.waypointFlag = False
        self.waypoint=[]
        
        self.logging = True
        self.logFileName = self.sysPath + "_pygps.log"
        #self.online = self.deviceAddress.deviceId
        self.online = False
        self.maxZoom = 16
        
        self.setGeometry(0, 0, 512, 512)
        self.setWindowTitle('PyGps')
        
        #render area
        self.renderArea = RenderArea(self)
        self.renderArea.move(0,0)
        
        #label lat lon
        self.label_latlon = PanelLabel(self)
        self.label_latlon.setMinimumSize(135, 65)
        self.label_latlon.move(0,0)
        self.label_latlon.show()
        
        #zoom buttons
        self.zoomin_button = self.createButton("+", QtGui.QColor("white"), self.zoomIn)       
        self.zoomout_button = self.createButton("-", QtGui.QColor("white"), self.zoomOut)
        self.zoom_label = QLabel()
        self.setZoomLabelText()
        #zoom panel - zoom buttons container
        self.zoom_panel = PanelLabel(self)
        self.zoom_panel.setMinimumSize(40, 80)
        zoom_layout = QtGui.QVBoxLayout()        
        zoom_layout.addWidget(self.zoomin_button)
        zoom_layout.addWidget(self.zoom_label)
        zoom_layout.addWidget(self.zoomout_button)
        self.zoom_panel.setLayout(zoom_layout)
        self.zoom_panel.move(0,75)
        self.zoom_panel.show()
        
        #self.settings_panel = QtGui.QLabel(self)
        self.settings_panel = MyLabel(self)
        self.settings_panel.setMinimumSize(40, 40)
        self.settings_panel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)
        self.settings_panel.setPixmap(QtGui.QPixmap("./32px-Crystal_Clear_action_configure.png"))
        size =  self.geometry()
        self.settings_panel.move(size.width()-40, 0)
        self.settings_panel.show()
        
        self.bt_panel = MyLabel(self)
        self.bt_panel.setMinimumSize(40, 40)
        self.bt_panel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)
        self.bt_panel.setPixmap(QtGui.QPixmap("./Bluetooth_32.png"))
        #size =  self.geometry()
        self.bt_panel.move(size.width()-40, 42)
        self.bt_panel.show()
        self.bt_panel.setEnabled(False)
        
        self.airport_panel = MyLabel(self)
        self.airport_panel.setMinimumSize(40, 40)
        self.airport_panel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)
        self.airport_panel.setPixmap(QtGui.QPixmap("./globe-compass-32x32.png"))
        size =  self.geometry()
        self.airport_panel.move(size.width()-40, 84)
        self.airport_panel.show()
        self.airport_panel.setEnabled(True)
        
        self.start_panel = MyLabel(self)
        self.start_panel.setMinimumSize(40, 40)
        self.start_panel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)
        self.start_panel.setPixmap(QtGui.QPixmap("./Airport-Blue-32x32.png"))
#        size =  self.geometry()
        self.start_panel.move(size.width()-40, 126)
        self.start_panel.show()
        self.start_panel.setEnabled(False)
        self.speed_panel = PanelLabel(self)
        self.speed_panel.setMinimumSize(160, 35)
        self.speed_panel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        #print self.speed_panel.alignment()
        self.speed_panel.setObjectName("speed")
        self.speed_panel.move(size.width()/2 - 75, size.height() - 35)
        
        self.time_panel = PanelLabel(self)
        self.time_panel.setMinimumSize(160, 35)
        self.time_panel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        #print self.speed_panel.alignment()
        self.time_panel.setObjectName("time")
        self.time_panel.move(0, size.height() - 35)
        
        
        self.mainPanel = PanelLabel(self)
        self.mainPanel.setMinimumSize(size.width(),size.height())
        self.mainPanel.show()
        
        self.mainMenuPanelGroup = PanelLabel(self)
        self.mainMenuPanelGroup.setMinimumSize(200,180)
        self.mainMenuPanelBox = QVBoxLayout()
        
        self.mainMenuPanelNav = MyLabel("Start Navigation")
        self.mainMenuPanelNav.setObjectName("Navigation")
        self.mainMenuPanelNav.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
#        self.mainMenuPanelNav.move(size.width()/2, size.height()/2)
#        self.mainMenuPanelNav.show()
        self.mainMenuPanelLog = MyLabel("Replay Log")
        self.mainMenuPanelLog.setObjectName("Log")
        self.mainMenuPanelLog.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        self.mainMenuPanelSett = MyLabel("Settings")
        self.mainMenuPanelSett.setObjectName("Sett")
        self.mainMenuPanelSett.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        self.mainMenuPanelMap = MyLabel("Download Maps")
        self.mainMenuPanelMap.setObjectName("Map")
        self.mainMenuPanelMap.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        self.mainMenuPanelExit = MyLabel("Exit")
        self.mainMenuPanelExit.setObjectName("Exit")
        self.mainMenuPanelExit.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        
        self.mainMenuPanelBox.addWidget(self.mainMenuPanelNav)
        self.mainMenuPanelBox.addWidget(self.mainMenuPanelLog)
        self.mainMenuPanelBox.addWidget(self.mainMenuPanelSett)
        self.mainMenuPanelBox.addWidget(self.mainMenuPanelMap)
        self.mainMenuPanelBox.addWidget(self.mainMenuPanelExit)
        
        self.mainMenuPanelGroup.setLayout(self.mainMenuPanelBox)
        self.mainMenuPanelGroup.move((size.width()/2)-100, (size.height()/2)-100)
        self.mainMenuPanelGroup.show()
        
        
        
        self.mainMenuSettingsGroup = PanelLabel(self)
        self.mainMenuSettingsGroup.setMinimumSize(350,300)
        self.mainMenuSettingsBox = QVBoxLayout()
        
        self.mainMenuSetPathGroup = QGroupBox()
        self.mainMenuSetPathLayout = QVBoxLayout()
        self.mainMenuSetLblPath = QLabel("<font color=white size=4>Maps path<\font>")
        self.mainMenuSetLblPath.setAlignment((Qt.AlignVCenter | Qt.AlignCenter))
        self.mainMenuSetTxtPathGroup = QGroupBox()
        self.mainMenuSetTxtPathLayout = QHBoxLayout()
        self.mainMenuSetTxtPath = QLineEdit()
        self.mainMenuSetTxtPath.setText("D:/Maps")
        self.mainMenuSetTxtPathButton = QPushButton("Browse")
        self.mainMenuSetTxtPathLayout.addWidget(self.mainMenuSetTxtPath)
        self.mainMenuSetTxtPathLayout.addWidget(self.mainMenuSetTxtPathButton)
        self.mainMenuSetTxtPathGroup.setLayout(self.mainMenuSetTxtPathLayout)
        self.mainMenuSetLblPath.setBuddy(self.mainMenuSetTxtPath)
        self.mainMenuSetPathLayout.addWidget(self.mainMenuSetLblPath)
        self.mainMenuSetPathLayout.addWidget(self.mainMenuSetTxtPathGroup)
        
        self.mainMenuSetPathGroup.setLayout(self.mainMenuSetPathLayout)
        
        
        
#        self.mainMenuSetSpeedGroup = QGroupBox ("Choose speed unit", self)
#        self.radioSpeed0 = QRadioButton("Knots",self.mainMenuSetSpeedGroup)
#        self.radioSpeed1 = QRadioButton("Km/h",self.mainMenuSetSpeedGroup)
#        self.radioSpeed2 = QRadioButton("Miles/h",self.mainMenuSetSpeedGroup)
#        self.radioSpeed1.setChecked(True)
#        self.mainMenuSetSpeedLayout = QVBoxLayout()
#        self.mainMenuSetSpeedLayout.addWidget(self.radioSpeed0)
#        self.mainMenuSetSpeedLayout.addWidget(self.radioSpeed1)
#        self.mainMenuSetSpeedLayout.addWidget(self.radioSpeed2)
#        self.mainMenuSetSpeedGroup.setLayout(self.mainMenuSetSpeedLayout)
        self.mainMenuSetSpeedGroupBox = QGroupBox ("Choose speed unit", self)
        self.mainMenuSetSpeedGroup = QButtonGroup()
        
        self.mainMenuSetSpeedGroup.exclusive()
        self.radioSpeed0 = QRadioButton("Knots",self)
        self.radioSpeed1 = QRadioButton("Km/h",self)
        self.radioSpeed2 = QRadioButton("Miles/h",self)
        self.mainMenuSetSpeedGroup.addButton(self.radioSpeed0,0)
        self.mainMenuSetSpeedGroup.addButton(self.radioSpeed1,1)
        self.mainMenuSetSpeedGroup.addButton(self.radioSpeed2,2)
        self.radioSpeed1.setChecked(True)
        self.mainMenuSetSpeedLayout = QVBoxLayout()
        self.mainMenuSetSpeedLayout.addWidget(self.radioSpeed0)
        self.mainMenuSetSpeedLayout.addWidget(self.radioSpeed1)
        self.mainMenuSetSpeedLayout.addWidget(self.radioSpeed2)
        self.mainMenuSetSpeedGroupBox.setLayout(self.mainMenuSetSpeedLayout)
        
        self.mainMenuSetDistGroupBox = QGroupBox("Choose distance unit", self)
        self.mainMenuSetDistGroup = QButtonGroup()
        self.mainMenuSetDistGroup.exclusive()
        
        self.radioDist0 = QRadioButton("Nautical Miles",self)
        self.radioDist1 = QRadioButton("Kilometers",self)
        self.radioDist2 = QRadioButton("Meters",self)
        self.radioDist3 = QRadioButton("Miles",self)
        self.radioDist4 = QRadioButton("Yards",self)
        self.radioDist1.setChecked(True)
        self.mainMenuSetDistGroup.addButton(self.radioDist0,0)
        self.mainMenuSetDistGroup.addButton(self.radioDist1,1)
        self.mainMenuSetDistGroup.addButton(self.radioDist2,2)
        self.mainMenuSetDistGroup.addButton(self.radioDist3,3)
        self.mainMenuSetDistGroup.addButton(self.radioDist4,4)
        self.mainMenuSetDistLayout = QVBoxLayout()
        self.mainMenuSetDistLayout.addWidget(self.radioDist0)
        self.mainMenuSetDistLayout.addWidget(self.radioDist1)
        self.mainMenuSetDistLayout.addWidget(self.radioDist2)
        self.mainMenuSetDistLayout.addWidget(self.radioDist3)
        self.mainMenuSetDistLayout.addWidget(self.radioDist4)
        self.mainMenuSetDistGroupBox.setLayout(self.mainMenuSetDistLayout)
        
        self.mainMenuRadioLayout = QHBoxLayout(self)
        
        self.mainMenuRadioLayout.addWidget(self.mainMenuSetSpeedGroupBox)
        self.mainMenuRadioLayout.addWidget(self.mainMenuSetDistGroupBox)
        
        self.mainMenuRadioGroup = QGroupBox()
        self.mainMenuRadioGroup.setLayout(self.mainMenuRadioLayout)
        
        self.mainMenuSetOKbtn = QPushButton("Ok")
        self.mainMenuSetCancelbtn = QPushButton("Cancel")
        
        self.mainMenuButtonLayout = QHBoxLayout(self)
        
        self.mainMenuButtonLayout.addWidget(self.mainMenuSetOKbtn)
        self.mainMenuButtonLayout.addWidget(self.mainMenuSetCancelbtn)
        self.mainMenuButtonGroup = QGroupBox()
        self.mainMenuButtonGroup.setLayout(self.mainMenuButtonLayout)
        
        self.mainMenuSettingsBox.addWidget(self.mainMenuSetPathGroup)
        self.mainMenuSettingsBox.addWidget(self.mainMenuRadioGroup)
        self.mainMenuSettingsBox.addWidget(self.mainMenuButtonGroup)
        
        self.mainMenuSettingsGroup.setLayout(self.mainMenuSettingsBox)
        self.mainMenuSettingsGroup.move((size.width()/2)-175, (size.height()/2)-150)
        self.mainMenuSettingsGroup.setObjectName("SettingsGroup")
        
        self.mainMenuSettingsGroup.hide()
        
        
        
        
        
        
        
        self.speedIDchecked = self.mainMenuSetSpeedGroup.checkedId()
        self.distIDchecked = self.mainMenuSetDistGroup.checkedId()




#        self.zoom_panel = PanelLabel(self)
#        self.zoom_panel.setMinimumSize(40, 80)
#        zoom_layout = QtGui.QVBoxLayout()        
#        zoom_layout.addWidget(self.zoomin_button)
#        zoom_layout.addWidget(self.zoom_label)
#        zoom_layout.addWidget(self.zoomout_button)
#        self.zoom_panel.setLayout(zoom_layout)
#        self.zoom_panel.move(0,75)
#        self.zoom_panel.show()
        
        
        #self.connect(self.bt_panel,PYSIGNAL("sigClicked"),
         #            self.CallConnect)
        self.connect(self.bt_panel, SIGNAL('sigclicked'),
                        self.CallConnect)
        
        self.connect(self.airport_panel, SIGNAL('sigclicked'),
                        self.setWayPoints)
        self.connect(self.mainMenuPanelNav, SIGNAL('sigclicked'),
                     self.startNav)
        self.connect(self.mainMenuPanelLog, SIGNAL('sigclicked'),
                     self.replayFromLog)
        self.connect(self.mainMenuPanelSett, SIGNAL('sigclicked'),
                     self.setSettings)
        self.connect(self.mainMenuSetCancelbtn, SIGNAL('clicked()'),
                     self.closeSettings)
        self.connect(self.mainMenuSetOKbtn, SIGNAL('clicked()'),
                     self.writeSettings)
        self.connect(self.mainMenuSetTxtPathButton, SIGNAL('clicked()'),
                     self.setMapPath)
        self.connect(self.mainMenuPanelExit, SIGNAL('sigclicked'),
                     self.close)
        
        self.connect(self.settings_panel, SIGNAL('sigclicked'),
                        self.showMainMenu)
        
        self.connect(self.start_panel, SIGNAL('sigclicked'),
                        self.drawMap)
        
        self.connect(self.deviceAddress, SIGNAL('btn_on'),self.btn_Enable)
        
        self.connect(self.Air, SIGNAL('waypointset'),self.setWayFlag)
#        self.connect(self.em, SIGNAL('waypointset'),self.setWaypointFlag)
#        self.connect(self.deviceAddress, SIGNAL('refresh'), self.RefreshBtnSearch)
                
        self.olddata = ""
 
        #add zoom buttons
        
        #assign slots
        
        #center the main window in the desktop
        self.center()
        self.timer = QtCore.QTimer()


    
    def writeSettings(self):
#        print self.mainMenuSetSpeedGroup.checkedId()
#        print self.mainMenuSetDistGroup.checkedId()
        
        self.fpath=self.mainMenuSetTxtPath.text() 
        
        if self.fpath!= None and QFile.exists(self.fpath):
            pygpsSettings.setValue("path", QVariant(self.mainMenuSetTxtPath.text()))
            pygpsSettings.setValue("speedUnits",QVariant(self.mainMenuSetSpeedGroup.checkedId()))
            pygpsSettings.setValue("distUnits",QVariant(self.mainMenuSetDistGroup.checkedId()))
        
        
        else:
            QMessageBox.critical(self, self.tr("WARNING!"),
                self.trUtf8('Set map path'))
        self.mainMenuPanelGroup.show()
        self.mainMenuSettingsGroup.hide()
                                   
    
    def setMapPath(self):
#        fpath = QFileDialog()
        self.fpath= QFileDialog.getExistingDirectory(self,self.trUtf8("Open Directory"),self.mainMenuSetTxtPath.text(),QFileDialog.ShowDirsOnly)#|QFileDialog.DontResolveSymlinks)
        self.mainMenuSetTxtPath.setText(self.fpath)
        print self.fpath 

    def setSettings(self):
        if QFile.exists(self.sysPath+"settings.ini"):
            self.mainMenuSetTxtPath.setText(pygpsSettings.value("path").toString())
            self.speedID = pygpsSettings.value("speedUnits").toString()
            self.distID = pygpsSettings.value("distUnits").toString()
            if self.speedID != "":
                if self.speedID == "0":
                    self.radioSpeed0.setChecked(True)
                elif self.speedID == "1":
                    self.radioSpeed1.setChecked(True)
                elif self.speedID == "2":
                    self.radioSpeed2.setChecked(True)
            if self.distID != "":
                if self.distID == "0":
                    self.radioDist0.setChecked(True)
                elif self.distID == "1":
                    self.radioDist1.setChecked(True)
                elif self.distID == "2":
                    self.radioDist2.setChecked(True)
                elif self.distID == "3":
                    self.radioDist3.setChecked(True)
                elif self.distID == "4":
                    self.radioDist4.setChecked(True)
        self.mainMenuPanelGroup.hide()
        self.mainMenuSettingsGroup.show()

    def closeSettings(self):
        self.mainMenuPanelGroup.show()
        self.mainMenuSettingsGroup.hide()

#    def printWayPoints(self):
#        print str(self.waypoint)
        

    
    
    
    def setWayFlag(self):
        print "!"
        if self.online == True and self.Air.waypointFlag == True:
            self.waypoint=self.Air.waypoints
            self.start_panel.setEnabled(True)
            print "TRUE"
            print self.waypoint
    
    def showMainMenu(self):
        self.mainFlag = False
        self.mainPanel.show()
        self.mainMenuPanelGroup.show()
    
    
    def replayFromLog(self):
        
#        filterFname=QFileDialog()
#        filterFname.setFilter("*.log")
        fname=QFileDialog.getOpenFileName(self,"Open Log",self.sysPath ,"*.log")
        self.logFileName = fname
        print fname
        if fname != "" and QFile.exists(fname):
            self.bt_panel.hide()
            self.airport_panel.hide()
            self.mainPanel.hide()
            self.mainMenuPanelGroup.hide()
            self.mainFlag = True
            self.renderArea.tilegrid.setMapPath(pygpsSettings.value("path").toString())
            if QFile.exists(self.sysPath+"settings.ini"):
                self.speedID = pygpsSettings.value("speedUnits").toString()
                self.distID = pygpsSettings.value("distUnits").toString()
                if self.speedID != "":
                    self.speedIDchecked = self.speedID
                if self.distID != "":
                    self.distIDchecked = self.distID
                
            self.drawMap()
        
        
    
    def startNav (self):
        if self.bt_Flag == True :
            self.mainPanel.hide()
            self.mainMenuPanelGroup.hide()
            self.bt_panel.show()
            self.airport_panel.show()
            self.mainFlag = True
            self.renderArea.tilegrid.setMapPath(pygpsSettings.value("path").toString())
            self.logFileName = self.sysPath + "_pygps.log"
            if QFile.exists(self.sysPath+"settings.ini"):
                self.speedID = pygpsSettings.value("speedUnits").toString()
                self.distID = pygpsSettings.value("distUnits").toString()
                if self.speedID != "":
                    self.speedIDchecked = self.speedID
                if self.distID != "":
                    self.distIDchecked = self.distID 
        else:
            QMessageBox.critical(self, self.tr("WARNING!"),
                self.trUtf8('Bluetooth not found yet!'))
            
    def setWayPoints(self):
        self.waypoint = self.Air.startRun(self.waypoint)
#        self.waypoint = AirPort.startRun(self, self.waypoint)
        print self.waypoint
        
             
    def setZoomLabelText(self):
        self.zoom_label.setText(self.tr("<span style='color: white; font-size: 16px; " + \
                        "font-family:Monospace; font-weight:bold; '>" + \
                        str(self.renderArea.tilegrid.zoomlevel) + "</span>"))
        
    def btn_Enable(self):
        print "Bluetooth Found"
        self.bt_panel.setEnabled(True)
        self.bt_Flag = True
#        self.em.emitNow()   
    def drawMap(self):
        if self.mainFlag == True:
            if self.logging and self.online:
                self.fileFlag = True
                self.logfh = open(self.logFileName, "w")
            
            if self.online:
            
                #TODO: make selection of BT devices
                self.fh = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                #self.fh.setblocking(False)
                try:
                    #self.fh.connect((self.deviceAddress.deviceId, 1)) #("00:0D:B5:31:58:58", 1))
                    self.fh.connect((self.deviceId, 1)) #("00:0D:B5:31:58:58", 1))
                    #assign socket notifier
                    self.notifier = QtCore.QSocketNotifier(self.fh.fileno(), QtCore.QSocketNotifier.Read)
                    self.connect(self.notifier, QtCore.SIGNAL("activated(int)"), self.readBTData)
                except bluetooth.btcommon.BluetoothError, ex:
                    print "Error: %s" % ex
            else:
                #open NMEA.log file - test purposes only
                self.logfh = open(self.logFileName, "r")                
                #assign timer to read NMEA data
                
                self.connect(self.timer,  QtCore.SIGNAL("timeout()"),  self.readLog)
                self.timer.start(1000/15) #1 second
                
        
    def createButton(self, text, color, member):
        button = Button(text, color)
        self.connect(button, QtCore.SIGNAL("clicked()"), member)
        return button
    
    def updateLabelLatLon(self, lat, lon, hd):
        self.label_latlon.setText(self.trUtf8("lat:%.6f°\nlon:%.6f°\nheading:%.1f°" % (lat, lon, hd)))
        
    def zoomIn(self):
        self.renderArea.tilegrid.zoomIn()
        self.setZoomLabelText()
        self.renderArea.update()
    
    def zoomOut(self):
        self.renderArea.tilegrid.zoomOut()
        self.setZoomLabelText()
        self.renderArea.update()
            
    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, 
        (screen.height()-size.height())/2)        
        
    def closeEvent(self, event):
        #QtGui.QMessageBox.about(self, self.tr("About Application"),
        #   self.trUtf8('Боря, с Днем Рожденья! :)'))
        
        
        
        if self.online and self.fileFlag:
#            print self.online
            self.disconnect(self.notifier, QtCore.SIGNAL("activated(int)"), self.readBTData)
            self.fh.close()
        else:
            if self.timer.isActive():
               self.timer.stop()
            
            #self.logfh.close()
        if self.logging and self.online and self.fileFlag:
#            print "1"
            self.logfh.close()
#            print "2"
            reply = QMessageBox.question(self,'Save log?',"Do you want to save your flight to log file?", 
                                     QMessageBox.Yes,QMessageBox.No)
        
            if reply == QMessageBox.Yes:
                fname = QFileDialog.getSaveFileName(self,"Save flight to Log",self.sysPath ,"*.log")
                if fname != "":
                    print fname
                    shutil.copyfile(self.logFileName, fname)
    #                self.logFileName = fname
        event.accept()
        
    def resizeEvent(self, event):
        size =  self.geometry()
        self.renderArea.setGeometry(0, 0, size.width(), size.height())
        self.renderArea.tilegrid.setBounds(size.width(), size.height())
        self.settings_panel.move(size.width()-40, 0)
        self.speed_panel.move(size.width()/2 - 75, size.height() - 35)
        self.bt_panel.move(size.width()-40,42)
        self.airport_panel.move(size.width()-40,84)
        self.start_panel.move(size.width()-40,126)
        self.time_panel.move(0,size.height()-35)
        self.mainPanel.setMinimumSize(size.width(), size.height())
        self.mainMenuPanelGroup.move((size.width()/2)-100, (size.height()/2)-100)
        self.mainMenuSettingsGroup.move((size.width()/2)-175, (size.height()/2)-150)
        event.accept()

    def readBTData(self):
        if self.mainFlag == True:
            bufferSize = 1024
            
    #FIXME:        #add try
            data = self.fh.recv(bufferSize)      
    
            if len(data) > 0:          
                data = self.olddata + data
                lines = data.splitlines(1)        
                for line in lines:            
                    if line.find("\r\n") != -1 :
                        line = line.strip()
                        self.olddata = ""                    
                        #log the line
                        if self.logging:
                            self.logfh.write('%s\n' % line)                    
                        #print line                        
                        try:
                            
                            ber = self.renderArea.tilegrid.bearing
                            gps = GPSString(line)
    #                        PCtime = gps.stripisotime()
    #                        try:
    #                            gps.date = PCtime.date()
    #                        except:
    #                            gps.date = datetime.datetime.utcnow().date()
                        
                            try:
                                gps.parse()
                            except gps.FailedChecksum:
                                sys.stderr.write( "Failed Checksum: " + str(gps.checksum()) + 
                                  " :: " + gps.msg + '\n')
                                continue
                            print gps.quality 
                            if gps.hdop < 6 :
                                
                                if gps.id == 3:
                                    self.time_panel.setText(self.tr("TIME: %s "%gps.datetime))
    #                                self.time_panel.setText(self.tr("TIME: %s "%gps.gpsTime))
    #                                self.speed_panel.setText(self.tr("%.1f <small>km/h</small>" % gps.kmph))
                                    if self.speedIDchecked == "0":
                                        self.speed_panel.setText(self.tr("%.1f knots" % gps.knots))
                                    elif self.speedIDchecked == "1":
                                        self.speed_panel.setText(self.tr("%.1f km/h" % gps.kmph))
                                    elif self.speedIDchecked == "2":
                                        self.speed_panel.setText(self.tr("%.1f mile/h" % gps.mph))
                                    self.renderArea.tilegrid.setBearing(gps.cog)                        
                                if gps.id == 1:    
    #                                self.time_panel.setText(self.tr(gps.stripisotime))
                                    self.time_panel.setText(self.tr("TIME: %s "%gps.datetime))
    #                                self.speed_panel.setText(self.tr("%.1f <small>km/h</small>" % gps.kmph))
    #                                self.time_panel.setText(self.tr("TIME: %s "%gps.gpsTime))
                                    self.renderArea.tilegrid.moveTo(gps.latitude, gps.longitude, True)
                                    self.updateLabelLatLon(gps.latitude, gps.longitude,ber )                            
                                    
                                self.renderArea.update()
                                #print "bearing:" + gps.cog + ", knots:" + gps.knots
                            else:
                                print "The received location is not precise enough to use."
                                print "Hdop = %s"%gps.hdop                            
                        except Exception, er:
                            #print er
                            print line
                            pass
            
                    # else we need to keep the line to add to data
                    else :
                        self.olddata = line

    def readLog(self):
        if self.mainFlag == True:
            count = 0
            line = self.logfh.readline()
            while line.find("$GPRMC") == -1:
                line = self.logfh.readline() 
                if not line:
                    self.logfh.seek(0)
                    count = count + 1
                    if count > 1:
                    #self.timer.stop()
                        return 
                
            try:                
                ber = self.renderArea.tilegrid.bearing
                gps = GPSString(line)
    #            PCtime = gps.stripisotime()
    #            try:
    #                gps.date = PCtime.date()
    #            except:
    #                gps.date = datetime.datetime.utcnow().date()
                try:
                    gps.parse()
                except gps.FailedChecksum:
                    sys.stderr.write( "Failed Checksum: " + gps.checksum() + 
                      " :: " + gps.msg + '\n')
                    pass 
                if gps.fixstatus == 1:
                                               
                    if gps.id == 3:
                        #self.renderArea.tilegrid.setBearing(gps.cog)                        
                        self.time_panel.setText(self.tr("TIME: %s "%gps.datetime))
#                        self.speed_panel.setText(self.tr("%.1f <small>km/h</small>" % gps.kmph))
                        if self.speedIDchecked == "0":
                            self.speed_panel.setText(self.tr("%.1f knots" % gps.knots))
                        elif self.speedIDchecked == "1":
                            self.speed_panel.setText(self.tr("%.1f km/h" % gps.kmph))
                        elif self.speedIDchecked == "2":
                            self.speed_panel.setText(self.tr("%.1f mile/h" % gps.mph))
                    self.renderArea.tilegrid.moveTo(gps.latitude, gps.longitude, True)
                    self.updateLabelLatLon(gps.latitude, gps.longitude,ber)                            
                    self.renderArea.update()
                    print "bearing:" + gps.cog + ", knots:" + gps.knots                           
            except:
                    pass
        
#    def RefreshBtnSearch(self):
#        self.deviceAddress.exit()
#        print "Refreshing"
#        self.deviceAddress.start()
        
    def CallConnect(self):
        #print "Connect"
#        self.deviceAddress = Bluetooth_Search(self)
#        self.deviceAddress.start()
#        self.bar = ProgressBar(self)
#        self.bar.timer1.start(100,self)
#        self.bar.show()
        self.list = QStringList()
        self.list =self.deviceAddress.GetApp()
        self.deviceId= ""
        l1,ok= QInputDialog.getItem(self,self.tr("Select Device"),self.tr("Device"),self.list,0,False)
        if ok and not l1.isEmpty():
                #print str(l1).split("   ")
                
                self.deviceName,self.deviceId = str(l1).split("   ")
                self.online = True
                print self.deviceId
                self.setWayFlag() 
                    
        else:
                self.deviceId= False
#                QMessageBox.about(self, self.tr("WARNING!!!"),
#                self.trUtf8('Application is OFFLINE!'))
                self.online = False
                self.start_panel.setEnabled(False)
#        self.online = self.deviceId
#        self.callGps = self.drawMap()
        
        
        
        
class MyLabel(QLabel):
    def __init__(self, parent = None):
        QLabel.__init__(self,parent)
        self.mainparent = parent
        #self.callGps = Pygps()
    def mouseDoubleClickEvent(self,event):
        self.emit(SIGNAL('sigclicked'),())

class PanelLabel(QLabel):
    def __init__(self, parent = None):
        QLabel.__init__(self,parent) 

class Button(QtGui.QToolButton):
    def __init__(self, text, color, parent=None):
        QtGui.QToolButton.__init__(self, parent)

        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        self.setText(text)

        newPalette = self.palette()
        newPalette.setColor(QtGui.QPalette.Button, color)
        self.setPalette(newPalette)

    def sizeHint(self):
        size = QtGui.QToolButton.sizeHint(self)
        size.setHeight(size.height() + 20)
        size.setWidth(max(size.width(), size.height()))
        return size
                    
    
    
app = QtGui.QApplication(sys.argv)
#icon = ProgressBar()
#icon.show()
pygpsSettings = QSettings("settings.ini",QSettings.IniFormat)

pygps = Pygps()
pygps.setStyleSheet(open(pygps.sysPath + "pygps.qss", "r").read())

pygps.show()
sys.exit(app.exec_())
