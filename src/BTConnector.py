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
        
        connectionsGroup = QtGui.QGroupBox(self.tr("BlueTooth GPS Device Selection"))
        
        deviceLabel = QtGui.QLabel(self.tr("Device: "))
        self.deviceCombo = QtGui.QComboBox()     
        
        deviceLayout = QtGui.QHBoxLayout()
        deviceLayout.addWidget(deviceLabel)
        deviceLayout.addWidget(self.deviceCombo)
        
        connectionLayout = QtGui.QVBoxLayout()
        connectionLayout.addItem(deviceLayout)
        connectionsGroup.setLayout(connectionLayout)
        
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(connectionsGroup)
        mainLayout.addStretch(1)
        
        self.refreshButton = QtGui.QPushButton(self.tr("Refresh"))
        mainLayout.addWidget(self.refreshButton)
        
        pushButton = QtGui.QPushButton(self.tr("Connect"))
        mainLayout.addWidget(pushButton)
        
        self.connect(pushButton, QtCore.SIGNAL("clicked()"), self.handleClick)
        self.connect(self.refreshButton, QtCore.SIGNAL("clicked()"), self.scanForDevices)

        self.setLayout(mainLayout)
               
    def handleClick(self):
        print self.deviceCombo.currentText()        
        print self.deviceCombo.itemData(self.deviceCombo.currentIndex()).toString()
        
    
    def scanForDevices(self, wait = 15):
        self.deviceCombo.clear()        
        devices = bluetooth.discover_devices(5, True, True)
        for addr, name in devices:
            self.deviceCombo.addItem(self.trUtf8(name), QtCore.QVariant(addr))        
    
    
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    pygps = BTConnector()
    pygps.show()
    sys.exit(app.exec_())
        