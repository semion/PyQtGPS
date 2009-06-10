#!/usr/bin/python
# -*- coding: UTF-8 -*-

# pygps.py

import sys, re, math, datetime, bluetooth
from PyQt4 import QtCore, QtGui
from globalmaptiles import GlobalMercator
from gpsparser import GPSString
from tilegrid import TileGrid
from renderarea import RenderArea
from BT import * 
class Pygps(QtGui.QMainWindow):
    def __init__(self):
        
        QtGui.QMainWindow.__init__(self)
        
        self.logging = True
        self.logFileName = "d:\pygps.log"
        self.online = True
        
        self.setGeometry(0, 0, 512, 512)
        self.setWindowTitle('PyGps')
        self.renderArea = RenderArea(self)
        self.setCentralWidget(self.renderArea)
        self.olddata = ""
        self.maxDopAllowed = "6"
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
                self.fh.connect(("00:0D:B5:31:58:58", 1))
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
            self.timer.start(1000) #1 second
            
    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, 
        (screen.height()-size.height())/2)        
        
    def closeEvent(self, event):
        #QtGui.QMessageBox.about(self, self.tr("About Application"),
           #self.trUtf8('Боря, с Днем Рожденья! :)'))
        
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
#                            PCtime = gps.stripisotime()
#                            try:
#                                gps.date = PCtime.date()
#                            except:
#                                gps.date = datetime.datetime.utcnow().date()
                        try:
                            gps.parse()
                        except gps.FailedChecksum:
                            sys.stderr.write( "Failed Checksum: " + gps.checksum() + 
                              " :: " + gps.msg + '\n') 
                            continue
                        print gps.quality
                        if gps.hdop <= self.maxDopAllowed:
                            
                            if gps.id in (1,3):
                                self.renderArea.tilegrid.moveTo(gps.latitude, gps.longitude)
                                self.renderArea.update()
                            if gps.id == 5:
                                print gps.visibleSVs
                        else:
                            print "The received location is not precise enough to use."
                            print "Hdop = %s"%gps.hdop 
                                                
                    except:
                        print line
                        pass
        
                # else we need to keep the line to add to data
                else :
                    self.olddata = line

    def readLog(self):
        count = 0
        line = self.fh.readline()
        while line.find("$GPGGA") == -1:
            line = self.fh.readline() 
            if not line:
                self.fh.seek(0)
                count = count + 1
                if count > 1:
                #self.timer.stop()
                    return 
        
        gps = GPSString(line)
        PCtime = gps.stripisotime()
        try:
            gps.date = PCtime.date()
        except:
            gps.date = datetime.datetime.utcnow().date()
        try:
            gps.parse()
            self.renderArea.tilegrid.moveTo(gps.latitude, gps.longitude)
            self.renderArea.update()
        except gps.FailedChecksum:
            sys.stderr.write( "Failed Checksum: " + gps.checksum() + 
              " :: " + gps.msg + '\n') 
            pass
                    
    
    
app = QtGui.QApplication(sys.argv)
pygps = Pygps()
pygps.show()
sys.exit(app.exec_())
