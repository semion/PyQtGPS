'''
Created on May 22, 2009

@author: semion
'''

import sys, bluetooth
from PyQt4 import QtCore, QtGui

class BTConnector(QtGui.QWidget):
    '''
    classdocs
    '''
    currentDevice = None

    def __init__(self, parent = None):
        '''
        Constructor
        '''
        QtGui.QWidget.__init__(self, parent)
        
        connectionsGroup = QtGui.QGroupBox(self.tr("GPS Device Selection"))
        
        deviceLabel = QtGui.QLabel(self.tr("Device: "))
        self.deviceCombo = QtGui.QComboBox()
        
        devices = self.scanForDevices(10)
        for addr, name in devices:
            self.deviceCombo.addItem(self.tr(name), QtCore.QVariant(addr))
        
        deviceLayout = QtGui.QHBoxLayout()
        deviceLayout.addWidget(deviceLabel)
        deviceLayout.addWidget(self.deviceCombo)
        
        connectionLayout = QtGui.QVBoxLayout()
        connectionLayout.addItem(deviceLayout)
        connectionsGroup.setLayout(connectionLayout)
        
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(connectionsGroup)
        mainLayout.addStretch(1)
        
        pushButton = QtGui.QPushButton(self.tr("Connect"))
        mainLayout.addWidget(pushButton)
        
        self.connect(pushButton, QtCore.SIGNAL("clicked()"), self.handleClick)

        self.setLayout(mainLayout)
               
    def handleClick(self):
        print self.deviceCombo.currentText()
        print self.deviceCombo.itemData(self.deviceCombo.currentIndex())
        
    
    def scanForDevices(self, wait):
        nearby_devices = bluetooth.discover_devices(lookup_names = True, flush_cache = True, duration = wait)
        return nearby_devices
    
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    pygps = BTConnector()
    pygps.show()
    sys.exit(app.exec_())
        