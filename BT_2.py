#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import division
from PyQt4 import QtGui
import sys
import bluetooth
from PyQt4.QtCore import  *
from PyQt4.QtGui import *
from renderarea import RenderArea

#try:
#    import bluetooth
#except:
#    print "Bluetoorh modele not found!  Working in Replay mode only!"
#    class BError(QMessageBox):
#        def __init__(self, parent=None):
#            QMessageBox.critical(self, self.tr("WARNING!!!"),
#                self.trUtf8('Bluetoorh modele not found! \n Working in Replay mode only!'))
class Bluetooth_Search(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.applications = QStringList()
        self.flag = True
        self.errorFlag = True
#        try:
#            import bluetooth
#            self.errorFlag = False
#        except:
#            print "Bluetoorh modele not found!  Working in Replay mode only!"
#        self.count = 0
    def run(self):    
        if not self.errorFlag:
            while self.flag == True:
                print "looking for nearby devices..."
                try:           
                    nearby_devices = bluetooth.discover_devices(duration = 20,lookup_names = True, flush_cache = True)
        #            nearby_devices = bluetooth.discover_devices(duration = 20,lookup_names = True, flush_cache = True)
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
                    self.emit(SIGNAL('btn_on'),())
                    self.emit(SIGNAL('waypointset'),())
                    self.flag = False
        #            self.exit()
                except:
                    print "No Gps"
    #                self.count+=1
    #                print self.count
    #                self.emit(SIGNAL('refresh()'),())
        #            self.exit()
    
    
                
    def GetApp(self):
            return self.applications
        
#            l1,ok= QInputDialog.getItem(self,self.tr("Select Device"),self.tr("Device"),self.applications,0,False)
#            if ok and not l1.isEmpty():
            #print str(l1).split("   ")
            
#                self.deviceName,self.deviceId = str(l1).split("   ")
#                print self.deviceId
#            else:
#                self.deviceId= False
#                QMessageBox.about(self, self.tr("WARNING!!!"),
#                self.trUtf8('Application is OFFLINE!'))
            #self.deviceId = str(l1)
            
        #self.listBox.insertItems(0,self.applications)
        #self.Box = QListView(self.listBox)
        #self.connect(self.connectButton, SIGNAL("clicked()"),self.PushButton)
#        except:
#            self.deviceId = False
#            QMessageBox.critical(self, self.trUtf8("'No Bluetooth Device Found!!!!"),
#                                 self.trUtf8('Application is OFFLINE!'))
                                 
    #def PushButton(self):        
     #pass
      


#app = QApplication(sys.argv)
#form = Bluetooth_Search()
#form.show()
#app.exec_()