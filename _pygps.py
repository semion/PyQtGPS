#!/usr/bin/python
# -*- coding: UTF-8 -*-

# pygps.py

import sys, os, re, math, datetime, bluetooth
from PyQt4 import QtCore, QtGui
from globalmaptiles import GlobalMercator
from gpsparser import GPSString
from tilegrid import TileGrid
from renderarea import RenderArea
from BT import *
        

class Pygps(QtGui.QWidget):
    '''PyGPS application by Semion Spivak and Boris Shterenberg'''
    def __init__(self, parent = None):
        
        QtGui.QWidget.__init__(self, parent)
        
        self.sysPath = os.path.join(sys.path[0], "")
        
        self.logging = True
        self.logFileName = self.sysPath + "_pygps.log"
        self.online = False
        
        self.maxZoom = 16
        
        self.setGeometry(0, 0, 512, 512)
        self.setWindowTitle('PyGps')
        self.deviceAddress = Bluetooth_Search(self)
        #render area
        self.renderArea = RenderArea(self)
        self.renderArea.move(0,0)
        
        #label lat lon
        self.label_latlon = QtGui.QLabel(self)
        self.label_latlon.setMinimumSize(135, 45)
        self.label_latlon.move(0,0)
        self.label_latlon.show()
        
        #zoom buttons
        self.zoomin_button = self.createButton("+", QtGui.QColor("white"), self.zoomIn)       
        self.zoomout_button = self.createButton("-", QtGui.QColor("white"), self.zoomOut)
        
        #zoom panel - zoom buttons container
        self.zoom_panel = QtGui.QLabel(self)
        self.zoom_panel.setMinimumSize(40, 60)
        zoom_layout = QtGui.QVBoxLayout()        
        zoom_layout.addWidget(self.zoomin_button)
        zoom_layout.addWidget(self.zoomout_button)
        self.zoom_panel.setLayout(zoom_layout)
        self.zoom_panel.move(0,60)
        self.zoom_panel.show()
        
        self.settings_panel = QtGui.QLabel(self)
        self.settings_panel.setMinimumSize(40, 40)
        self.settings_panel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)
        self.settings_panel.setPixmap(QtGui.QPixmap("./32px-Crystal_Clear_action_configure.png"))
        size =  self.geometry()
        self.settings_panel.move(size.width()-40, 0)
        self.settings_panel.show()
        
        self.speed_panel = QtGui.QLabel(self)
        self.speed_panel.setMinimumSize(160, 35)
        self.speed_panel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        #print self.speed_panel.alignment()
        self.speed_panel.setObjectName("speed")
        self.speed_panel.move(size.width()/2 - 75, size.height() - 35)

        
        
        
        self.olddata = ""
 
        #add zoom buttons
        
        #assign slots
        
        #center the main window in the desktop
        self.center()
        
        if self.logging and self.online:
            self.logfh = open(self.logFileName, "w")
        
        if self.online:
        
            #TODO: make selection of BT devices
            self.fh = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            #self.fh.setblocking(False)
            try:
                self.fh.connect((self.deviceAddress.deviceId, 1)) #("00:0D:B5:31:58:58", 1))
                #assign socket notifier
                self.notifier = QtCore.QSocketNotifier(self.fh.fileno(), QtCore.QSocketNotifier.Read)
                self.connect(self.notifier, QtCore.SIGNAL("activated(int)"), self.readBTData)
            except bluetooth.btcommon.BluetoothError, ex:
                print "Error: %s" % ex
        else:
            #open NMEA.log file - test purposes only
            self.fh = open(self.logFileName, "r")                
            #assign timer to read NMEA data
            self.timer = QtCore.QTimer()
            self.connect(self.timer,  QtCore.SIGNAL("timeout()"),  self.readLog)
            self.timer.start(1000/13) #1 second
            
    def createButton(self, text, color, member):
        button = Button(text, color)
        self.connect(button, QtCore.SIGNAL("clicked()"), member)
        return button
    
    def updateLabelLatLon(self, lat, lon):
        self.label_latlon.setText(self.tr("lat:%.6f\nlon:%.6f" % (lat, lon)))
        
    def zoomIn(self):
        self.renderArea.tilegrid.zoomIn()
        self.renderArea.update()
    
    def zoomOut(self):
        self.renderArea.tilegrid.zoomOut()
        self.renderArea.update()
            
    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, 
        (screen.height()-size.height())/2)        
        
    def closeEvent(self, event):
        #QtGui.QMessageBox.about(self, self.tr("About Application"),
        #   self.trUtf8('Боря, с Днем Рожденья! :)'))
        
        if self.online:
            self.disconnect(self.notifier, QtCore.SIGNAL("activated(int)"), self.readBTData)
        self.fh.close()
        if self.logging and self.online:
            self.logfh.close()
        event.accept()
        
    def resizeEvent(self, event):
        size =  self.geometry()
        self.renderArea.setGeometry(0, 0, size.width(), size.height())
        self.renderArea.tilegrid.setBounds(size.width(), size.height())
        self.settings_panel.move(size.width()-40, 0)
        self.speed_panel.move(size.width()/2 - 75, size.height() - 35)
        event.accept()

    def readBTData(self):
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
                        
                        gps = GPSString(line)
                        PCtime = gps.stripisotime()
                        try:
                            gps.date = PCtime.date()
                        except:
                            gps.date = datetime.datetime.utcnow().date()
                    
                        try:
                            gps.parse()
                        except gps.FailedChecksum:
                            sys.stderr.write( "Failed Checksum: " + str(gps.checksum()) + 
                              " :: " + gps.msg + '\n')
                            continue
                        print gps.quality 
                        if gps.hdop < 6 :
                            
                            if gps.id == 3:
                                self.speed_panel.setText(self.tr("%.1f km/h" % gps.kmph))
                                self.renderArea.tilegrid.setBearing(gps.cog)                        
                            if gps.id in (1 , 3):    
                                self.renderArea.tilegrid.moveTo(gps.latitude, gps.longitude, False)
                                self.updateLabelLatLon(gps.latitude, gps.longitude)                            
                                
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
        count = 0
        line = self.fh.readline()
        while line.find("$GPRMC") == -1:
            line = self.fh.readline() 
            if not line:
                self.fh.seek(0)
                count = count + 1
                if count > 1:
                #self.timer.stop()
                    return 
            
        try:                
            gps = GPSString(line)
            PCtime = gps.stripisotime()
            try:
                gps.date = PCtime.date()
            except:
                gps.date = datetime.datetime.utcnow().date()
            try:
                gps.parse()
            except gps.FailedChecksum:
                sys.stderr.write( "Failed Checksum: " + gps.checksum() + 
                  " :: " + gps.msg + '\n')
                pass 
                       
            if gps.id == 3:
                self.renderArea.tilegrid.setBearing(gps.cog)                        
                self.renderArea.tilegrid.moveTo(gps.latitude, gps.longitude, False)
                self.updateLabelLatLon(gps.latitude, gps.longitude)                            
                self.speed_panel.setText(self.tr("%.1f <small>km/h</small>" % gps.kmph))
                self.renderArea.update()
            print "bearing:" + gps.cog + ", knots:" + gps.knots                           
        except:
            pass
        
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
pygps = Pygps()
pygps.setStyleSheet(open(pygps.sysPath + "pygps.qss", "r").read())
pygps.show()
sys.exit(app.exec_())
