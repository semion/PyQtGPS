#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import division
import sys
import bluetooth
from PyQt4.QtCore import  *
from PyQt4.QtGui import *
from renderarea import RenderArea

class Bluetooth_Search(QDialog):
    def __init__(self, parent = None):
        super(Bluetooth_Search,self).__init__(parent)
        self.deviceNo=""
        self.list = QListWidgetItem()
        #self.listBox = QInputDialog()
        self.applications = QStringList()
        
        self.refButton = QPushButton("Refresh")
        self.disConnectButton = QPushButton("Disconnect")
        self.connectButton = QPushButton("Connect")
        
        horLayout = QHBoxLayout()
        horLayout.addWidget(self.refButton)
        horLayout.addWidget(self.disConnectButton)
        horLayout.addWidget(self.connectButton)
        
        layout = QVBoxLayout()
        #layout.addWidget(self.listBox)
       # layout.addLayout(horLayout)
        self.setLayout(layout)

        print "looking for nearby devices..."
        
        nearby_devices = bluetooth.discover_devices(lookup_names = True, flush_cache = True, duration = 5)
        print "found %d devices" % len(nearby_devices)
        
        for addr, name in nearby_devices:
            #print "  %s - %s" % (addr, name)
            #for services in bluetooth.find_service(address = addr):
             #   print "       Name:        %s" % (services["name"])
                #print "       Description: %s" % (services["description"])
                #print "       Protocol:    %s" % (services["protocol"])
                #print "       Provider:    %s" % (services["provider"])
                #print "       Port:        %s" % (services["port"])
                #print "       Service id:  %s" % (services["service-id"])
                #print ""
            
            
            #print ""
            if name == "":
                name = "Unknown Device"
            if self.applications.contains(name):
                continue
            self.applications.append(self.trUtf8("%s   %s"%(name,addr)))
        l1,ok= QInputDialog.getItem(self,self.tr("Select Device"),self.tr("Device"),self.applications,0,False)
        if ok and not l1.isEmpty():
            deviceId = l1
            
        #self.listBox.insertItems(0,self.applications)
        #self.Box = QListView(self.listBox)
        self.connect(self.connectButton, SIGNAL("clicked()"),self.PushButton)
        
    def PushButton(self):        
     pass
      


app = QApplication(sys.argv)
form = Bluetooth_Search()
form.show()
app.exec_()